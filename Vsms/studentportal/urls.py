from django.urls import path
from.import views



urlpatterns=[
    path('studentlist/',views.Studentlist),

    path('createstudent/',views.student_create),

    path('studentAccount/<int:mobile_number>/', views.update_student, name='student_account_setup_api'),

    path('student_login/',views.student_auth_token),

    path('makepayment/<str:student_id>/',views.make_payment),

    path('batches/', views.batch_list, name='batch_list'),#to view all the batches
    path('createnewbatch/',views.create_new_batch,name='new_batch'),#for craeting new batch

   path('batch/<str:batch_id>/students/', views.students_in_batch, name='students_in_batch'),#to view all students for paticular batch
  # path('session_attendance/<str:batch_id>/attendance/<str:session_date>/', views.batch_students_attendance_view, name='session-attendance'),#to view attendance for all students

   path('sessions/', views.get_sessions, name='get-sessions'),#to view all sessions

   path('batch-sessions/<str:batch_id>/<str:session_type>/', views.get_sessions_by_batch, name='get-sessions-by-batch'),#to view session for paticular batch


   path('create-lab-sessions/', views.create_lab_sessions, name='create_lab_sessions'),#to create labsession for paticular batch

   path('mark-attendance/<str:batch_id>/', views.mark_attendance, name='mark_attendance'),#to create attendance for seeion

   path('viewloginuser_attendence/',views.attendance_list),#to view login user attendence
   
   path('view_loginuser_profile/',views.studentdetails),#to view login user profile

   path('view_attendancecount/',views. lab_session_data),#to view login user lab attendennce
   path('view_attendancecount_weekelytest/',views. weekelytest_session_data),#to view login user weekelytest attendennce
   path('view_attendancecount_weekelymock/',views. weekelymock_session_data),#to view login user weekelymock attendennce

   path('Delete_attendence/<int:session>/<str:student>/',views.DeleteAttendence),

   path('students-with-outstanding-fees/<str:batch_id>/<str:status>/', views.get_students_with_outstanding_fees, name='students_with_outstanding_fees'),# to get the students in batch batch who have balance to pay


   path('Deletestudent/<int:mobile_no>/',views.Deletestudent),
   path('newbatch/',views.create_new_batch),
   path('student-login/', views.student_auth_token, name='student-login'),

   path('student-logout/', views.student_logout, name='student_logout'),

   path('tasks/', views.add_task, name='add_task'),
   #path('gettask/', views.get_tasks, name='get_tasks'),
   path('gettask/batch/<str:batch_id>/', views.get_tasks_by_batch, name='get_tasks_by_batch'),

   path('daily_videos/', views.create_daily_video, name='create_daily_video'),
   path('daily_video/', views.get_daily_video, name='get_daily_video'),

   path('notificationcreate/', views.notification_create, name='notification_create'),
   path('notification/', views.notification_list, name='notification_list'),
    path('notification/<int:pk>/mark_as_read/', views.mark_notification_as_read, name='mark_notification_as_read'),

   path('placementnotificreate/', views.placementnotifi_create, name='placementnotifi_create'),
   path('placementnotifi/', views.placementnotifi_list, name='placementnotifi_list'),

   path('student-count/', views.count_students, name='student_count'),
   path('staff-count/', views.count_staff, name='staff_count'),

   path('student-graph-data/', views.student_graph_data, name='student_graph_data'),
   path('staff-graph-data/', views.staff_graph_data, name='staff_graph_data'),

   path('updatestudentget/<int:mobile_no>/',views.updatestudentget),
   path('updatestudent/<int:mobile_no>/',views.updatestudent),


   path('view_lab_performance/<int:mobile_no>/',views.lab_performance),
   path('view_weekelytest_performance/<int:mobile_no>/',views.weekely_test_performance),
   path('view_weekelymock_performance/<int:mobile_no>/',views.weekely_mock_performance),
   path('staff_attendence_view_lab/<int:mobile_no>/',views.staff_attendance_view_Lab),
   path('staff_attendence_view_weekelytest/<int:mobile_no>/',views.staff_view_weekelyTest),
   path('staff_attendence_view_weekelymock/<int:mobile_no>/',views.staff_attendance_view_WeekelyMock),

   path('session_attendance/<str:batch_id>/attendance/<int:id>/', views.batch_students_attendance_view, name='session-attendance'),#to view attendance for all students


   path('studentattdence_view_Lab/',views.student_attendance_view_Lab),
   path('studentlogin_view_weekelyTest/',views.student_attendance_view_weekelyTest),
   path('studentlogin_view_weekelymock/',views.student_attendance_view_WeekelyMock)
]