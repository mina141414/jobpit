from django.http.response import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import Attendances
from datetime import date, datetime
 
 
class HomeView(LoginRequiredMixin, TemplateView):
    # 表示するテンプレートを定義
    template_name = 'home.html'
    # ログインがされてなかったらリダイレクトされるURL
    login_url = '/accounts/login/'
 
 
class PushTimecard(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    # POSTメソッドでリクエストされたら実行するメソッド
    def post(self, request, *args, **kwargs):
        push_type = request.POST.get('push_type')
 
        is_attendanced = Attendances.objects.filter(
            user = request.user,
            attendance_time__date = date.today()
        ).exists()

        is_left = Attendances.objects.filter(
             user = request.user,
             leave_time__date = date.today()
         ).exists()
 
        response_body = {}
        if push_type == 'attendance' and not is_attendanced:
            # 出勤したユーザーをDBに保存する
            attendance = Attendances(user=request.user)
            attendance.save()
            response_time = attendance.attendance_time
            response_body = {
                'result': 'success',
                'attendance_time': response_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        elif push_type == 'leave' and not is_left:
            if is_attendanced:
                # 退勤するユーザーのレコードの退勤時間を更新する
                attendance = Attendances.objects.filter(
                    user = request.user,
                    attendance_time__date = date.today()
                )[0]
                attendance.leave_time = datetime.now()
                attendance.save()
                response_time = attendance.leave_time
                response_body = {
                    'result': 'success',
                    'leave_time': response_time.strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                response_body = {
                    'result': 'not_attended',
                }
        if not response_body:
            response_body = {
                'result': 'already_exists'
            }
        return JsonResponse(response_body)



class AttendanceRecords(LoginRequiredMixin, TemplateView):
     template_name = 'attend_records.html'
     login_url = '/accounts/login'
     def get(self, request, *args, **kwargs):
        today = datetime.today()
        # リクエストパラメータを受け取る
        search_param = request.GET.get('year_month')
        if search_param:
            search_params = list(map(int, search_param.split('-')))
            search_year = search_params[0]
            search_month = search_params[1]
        else:
            search_year = today.year
            search_month = today.month
 
        # 年と月でデータを絞り込む
        month_attendances = Attendances.objects.filter(
            user = request.user,
            attendance_time__year = search_year,
            attendance_time__month = search_month
        ).order_by('attendance_time')
 
        # context用のデータに整形
        attendances_context = []
        for attendance in month_attendances:
            attendance_time = attendance.attendance_time
            leave_time = attendance.leave_time
            if leave_time:
                leave_time = leave_time.strftime('%H:%M:%S')
            else:
                if attendance_time.date() == today.date():
                    leave_time = None
                else:
                    leave_time = 'not_pushed'
            day_attendance = {
                'date': attendance_time.strftime('%Y-%m-%d'),
                'attendance_at': attendance_time.strftime('%H:%M:%S'),
                'leave_at': leave_time
            }
            attendances_context.append(day_attendance)
 
        context = {'attendances': attendances_context}
        # Templateにcontextを含めてレスポンスを返す
        return self.render_to_response(context)
