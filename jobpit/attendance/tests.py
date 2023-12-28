
from django.test import TestCase, Client
from django.contrib.auth.models import User
import json
 
# Create your tests here.
 
class LoginAttendanceTest(TestCase):
    def setUp(self):
        # テスト用のユーザーを作成
        self.credentials = {
            'username': 'testuser',
            'password': 'samplesecret'
        }
        User.objects.create_user(**self.credentials)
 
        self.client = Client()
        # テストユーザーでログイン
        self.client.login(
            username=self.credentials['username'], 
            password=self.credentials['password']
        )    
 
    def test_push_attendance(self):
        '''
        出勤、退勤打刻ができることを確認するテスト
        '''
        # 出勤打刻を行う
        response = self.client.post('/push', {'push_type': 'attendance'})
        response_body = json.loads(response.content.decode('utf-8'))
        # ステータスコードが200であること
        self.assertEqual(response.status_code, 200)
        # 出勤打刻が成功したときのレスポンスが受け取れていること
        self.assertEqual(response_body['result'], 'success')
 
        # 退勤打刻を行う
        response = self.client.post('/push', {'push_type': 'leave'})
        response_body = json.loads(response.content.decode('utf-8'))
        # ステータスコードが200であること
        self.assertEqual(response.status_code, 200)
        # 退勤打刻が成功したときのレスポンスが受け取れていること
        self.assertEqual(response_body['result'], 'success')
 
    def test_push_leave_first(self):
        '''
        先に退勤打刻を押したときのテスト
        '''
        # 退勤打刻を行う
        response = self.client.post('/push', {'push_type': 'leave'})
        response_body = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        # まだ出勤打刻が押されていない時のレスポンスが受けて取れていること
        self.assertEqual(response_body['result'], 'not_attended')
    
    def test_double_push(self):
        '''
        ボタンを２重に押したときの挙動を確認するテスト
        '''
        # 出勤打刻を行う
        response = self.client.post('/push', {'push_type': 'attendance'})
        response_body = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body['result'], 'success')
 
        # 出勤打刻をもう一度行う
        response = self.client.post('/push', {'push_type': 'attendance'})
        response_body = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        # すでに打刻されたときのレスポンスを受け取れていること
        self.assertEqual(response_body['result'], 'already_exists')
 
        # 退勤打刻を行う
        response = self.client.post('/push', {'push_type': 'leave'})
        response_body = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body['result'], 'success')
 
        # もう一度退勤打刻を行う
        response = self.client.post('/push', {'push_type': 'leave'})
        response_body = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        # すでに打刻されたときのレスポンスが受け取れていること
        self.assertEqual(response_body['result'], 'already_exists')

class AttendanceRecordsTest(TestCase):
    fixtures = ['test_attendance_records.json']
    def setUp(self):
        # テストユーザーでログイン(アカウントはfixtureで登録)
        self.client = Client()
        self.client.login(
            username='testuser',
            password='samplesecret'
        )
 
    def test_attendance_records(self):
        '''
        出勤簿に表示するデータがある時のcontextを確認するテスト
        '''
        # 2021/4の出勤簿を開く
        response = self.client.get('/records', {'year_month': '2021-4'})
        # ステータスコードが200であること
        self.assertEqual(response.status_code, 200)
        # contextの出勤記録が２つあること
        self.assertEqual(len(response.context['attendances']), 2)
 
        # 2021/5の出勤簿を開く
        response = self.client.get('/records', {'year_month': '2021-5'})
        self.assertEqual(response.status_code, 200)
        # contextの出勤記録が1つあること
        self.assertEqual(len(response.context['attendances']), 1)
        # 過去の退勤打刻が押されていない場合は'not_pushed'となっていること
        self.assertEqual(response.context['attendances'][0]['leave_at'], 'not_pushed')
 
    def test_empty_attendance_records(self):
        '''
        出勤簿に表示するデータがないときのcontextを確認するテスト
        '''
        # 2021/6の出勤簿を開く
        response = self.client.get('/records', {'year_month': '2021-6'})
        self.assertEqual(response.status_code, 200)
        # contextの出勤記録が1つもないこと
        self.assertEqual(len(response.context['attendances']), 0)
