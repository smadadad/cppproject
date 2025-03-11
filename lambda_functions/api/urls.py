from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # JWT token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Student endpoints
    path('students/my_results/', views.get_student_results_view, name='student_results'),
    path('complaints/submit/', views.submit_complaint_view, name='submit_complaint'),

    # Teacher endpoints
    path('teachers/upload_results/', views.upload_results_view, name='upload_results'),
    path('teachers/all_results/', views.get_all_results_view, name='all_results'),
    path('complaints/', views.get_complaints_view, name='get_complaints'),
    path('complaints/<str:complaint_id>/resolve/', views.resolve_complaint_view, name='resolve_complaint'),

    # Admin endpoints
    path('admin/upload-staff/', views.upload_staff_view, name='upload_staff'),
    path('admin/upload-students/', views.upload_students_view, name='upload_students'),
    
    # Password reset endpoints
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('change_password/', views.change_password, name='change_password'),
    path('register/', views.register_user, name='register'),
]
