from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('admission/apply/', views.admission_apply, name='admission_apply'),
    path('records/', views.view_records, name='view_records'),
    path('records/cancel/<str:admission_code>/', views.cancel_admission, name='cancel_admission'),
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('laundry/book/', views.book_laundry, name='book_laundry'),
    path('laundry/view/', views.view_laundry, name='view_laundry'),
    path('laundry/cancel/<int:booking_id>/', views.cancel_laundry, name='cancel_laundry'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='hostel_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='hostel_app/logout.html'), name='logout'),
    
    # Password reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='hostel_app/password_reset.html',
             form_class=CustomPasswordResetForm
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='hostel_app/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='hostel_app/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='hostel_app/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # API endpoints
    path('api/room-availability/', views.api_room_availability, name='api_room_availability'),
    path('api/room-types/', views.api_room_types, name='api_room_types'),
    path('api/receipt/<str:admission_code>/', views.generate_receipt, name='generate_receipt'),
]

