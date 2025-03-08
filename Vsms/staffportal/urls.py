from django.urls import path
from.import views


urlpatterns=[
    path('',views.demo),
    path('staffget/',views.Staffget),
    path('staffregistration/',views.registerstaff),
    path('staff-login/', views.staff_auth_token, name='staff-login'),

    path('staff-logout/', views.staff_logout, name='staff-logout'),  # Added logout URL
    path('staffdepsdata/',views.Staffdepartments),
    path('verifyemail/',views.verifyemail),
    path('verifyotp/',views.verify_otp),
    path('change-password/<str:email>/',views.change_password),
    path('staffloginprofile/',views.stafflogindetails),
    
    path('createdepartment/',views.departmentpost),
    path('departments/', views.get_departments, name='get_departments'),


    path('staffUpdateget/<int:mobile>/',views.updatestaffapiget),
    path('staffUpdate/<int:mobile>/',views.updatestaffapi),

   path('createadmin/',views.registerAdmin),
   path('admin-login/', views.admin_auth_token),
    path('logout/', views.logout, name='logout'),  # Add this line



    path('staffdetails/', views.get_all_staff_details, name='all-staff-details'),

]