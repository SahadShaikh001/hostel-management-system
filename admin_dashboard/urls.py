from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('residents/', views.residents, name='admin_residents'),
    path('bookings/', views.bookings, name='admin_bookings'),
    path('feedback/', views.feedback, name='admin_feedback'),
    path('laundry/', views.laundry, name='admin_laundry'),
    path('reports/', views.reports, name='admin_reports'),
    path('download-report/<str:report_type>/', views.download_report, name='download_report'),
    path('resident/add/', views.add_resident, name='add_resident'),
    path('resident/update/<str:admission_code>/', views.update_resident, name='update_resident'),
    path('resident/delete/<str:admission_code>/', views.delete_resident, name='delete_resident'),
    path('booking/add/', views.add_booking, name='add_booking'),
]