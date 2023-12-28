from django.http.response import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from .models import AttendanceFixRequests
from attendance.models import Attendances
from datetime import datetime
 
 # Create your views here.
class FixAttendanceRequestView(LoginRequiredMixin, TemplateView):
    template_name = 'fix_request.html'
    login_url = '/accounts/login/'
    def get(self, request, *args, **kwargs):
        # ユーザーの申請一覧を取得
        fix_requests = AttendanceFixRequests.objects.filter(
            user = request.user
        )
 
        resp_params = []
        # 表示用に整形
        for fix_request in fix_requests:
            if not fix_request.is_accepted and not fix_request.checked_time:
                request_status = 'not_checked'
            elif not fix_request.is_accepted and fix_request.checked_time:
                request_status = 'rejected'
            else:
                request_status = 'accepted'
            resp_param = {
                'date': fix_request.revision_time.strftime('%Y/%m/%d'),
                'stamp_type': fix_request.get_stamp_type_display(),
                'revision_time': fix_request.revision_time.strftime('%H:%M'),
                'request_status': request_status
            }
            resp_params.append(resp_param)
         
        context = {
            'fix_requests': resp_params
        }
        return self.render_to_response(context)
 
    def post(self, request, *args, **kwargs):
        # リクエストパラメータを取得
        push_type = request.POST.get('push_type')
        push_date = request.POST.get('push_date')
        push_time = request.POST.get('push_time')
        push_reason = request.POST.get('push_reason')
        fix_datetime = '{}T{}'.format(push_date, push_time)
 
        is_attendanced = Attendances.objects.filter(
            user = request.user,
            attendance_time__date = datetime.strptime(push_date, '%Y-%m-%d')
        ).exists()
        # 打刻修正のデータを登録する
        if is_attendanced:
            attendance = Attendances.objects.get(
                user = request.user,
                attendance_time__date = datetime.strptime(push_date, '%Y-%m-%d')
            )
            fix_request = AttendanceFixRequests(
                user = request.user,
                attendance = attendance,
                stamp_type = push_type,
                reason = push_reason,
                revision_time = datetime.strptime(fix_datetime, '%Y-%m-%dT%H:%M')
            )
        else:
            fix_request = AttendanceFixRequests(
                user = request.user,
                stamp_type = push_type,
                reason = push_reason,
                revision_time = datetime.strptime(fix_datetime, '%Y-%m-%dT%H:%M')
            )
        fix_request.save()
        return JsonResponse({'status':'OK'})
    

class AttendanceAcceptionView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'request_acception.html'
    login_url = '/accounts/login/'
    def test_func(self):
        user = self.request.user
        return user.is_staff    
 
    def get(self, request, *arg, **kwargs):
        fix_requests = AttendanceFixRequests.objects.all()
        request_list = []
        for fix_request in fix_requests:
            if not fix_request.is_accepted and not fix_request.checked_time:
                request_status = 'not_checked'
            elif not fix_request.is_accepted and fix_request.checked_time:
                request_status = 'rejected'
            else:
                request_status = 'accepted'
            request_data = {
                'id': fix_request.pk,
                'user_name': fix_request.user.username,
                'request_time': fix_request.request_time.strftime('%Y-%m-%d %H:%M:%S'),
                'request_status': request_status
            }
            request_list.append(request_data)
        context = {
            'fix_requests': request_list
        }
        return self.render_to_response(context)
    
class AcceptionDetailView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'acception_detail.html'
    login_url = '/accounts/login'
    def test_func(self):
        user = self.request.user
        return user.is_staff    
 
    def get(self, request, *arg, **kwargs):
        request_id = self.kwargs['request_id']
        fix_request = get_object_or_404(AttendanceFixRequests, pk=request_id)
        context = {'request_detail': fix_request}
        return self.render_to_response(context)
    
class PushAcceptionView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
     login_url = '/accounts/login'
     def test_func(self):
         user = self.request.user
         return user.is_staff    
 
     def post(self, request, *arg, **kwargs):
         result = request.POST.get('result')
         request_id = request.POST.get('request_id')
         fix_request = AttendanceFixRequests.objects.get(pk=request_id)
         # 確認日時が存在するときはデータ更新を行わない
         if fix_request.checked_time:
             return JsonResponse({'result': 'acception_exists'})
         fix_request.checked_time = datetime.now()
         if result == 'accept':
             # 承認されたらfix_requestに紐づくattendancesのレコードを更新させる
             fix_request.is_accepted = True
             if fix_request.attendance:
                 if fix_request.stamp_type == 'AT':
                     fix_request.attendance.attendance_time = fix_request.revision_time
                 elif fix_request.stamp_type == 'LE':
                     fix_request.attendance.leave_time = fix_request.revision_time
             else:
                 if fix_request.stamp_type == 'AT':
                     fix_request.attendance = Attendances(
                         user=fix_request.user,
                         attendance_time=fix_request.revision_time
                     )
                 elif fix_request.stamp_type == 'LE':
                     fix_request.attendance = Attendances(
                         user=fix_request.user,
                         leave_time=fix_request.revision_time
                     )
             fix_request.attendance.save()
         elif result == 'reject':
             fix_request.is_accepted = False
         fix_request.save()
 
         return JsonResponse({'result': 'OK'})
