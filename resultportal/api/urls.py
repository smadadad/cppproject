from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # JWT token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Student endpoints
    path('api/students/my_results/', views.get_student_results, name='student_results'),
    path('api/complaints/', views.submit_complaint, name='submit_complaint'),
    
    # Teacher endpoints
    path('api/teachers/upload_results/', views.upload_results, name='upload_results'),
    path('api/teachers/all_results/', views.get_all_results, name='all_results'),
    path('api/complaints/', views.get_complaints, name='get_complaints'),
    path('api/complaints/<str:complaint_id>/resolve/', views.resolve_complaint, name='resolve_complaint'),
    
    # Admin endpoints
    path('api/admin/upload-staff/', views.upload_staff, name='upload_staff'),
    path('api/admin/upload-students/', views.upload_students, name='upload_students'),
]