import json
import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import (
    RoomType, RoomImage, RoomAmenity, Resident, Booking,
    Feedback, MessMenu, LaundryBooking, HostelRule, WardenInfo, ContactMessage
)
from .models import Resident, Booking, Feedback, LaundryBooking, RoomType
from .forms import AdmissionForm
from .forms import  AdmissionForm, FeedbackForm, LaundryBookingForm, ContactForm

from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UserRegisterForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Save phone number to user profile or custom user model
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'hostel_app/register.html', {'form': form})


def index(request):
    room_types = RoomType.objects.all()
    mess_menu = MessMenu.objects.all().order_by('day')
    hostel_rules = HostelRule.objects.all()
    warden_info = WardenInfo.objects.first()
    
    # Get room availability
    today = timezone.now().date()
    availability = {}
    for room_type in room_types:
        availability[room_type.id] = {}
        for i in range(30):
            date = today + timedelta(days=i)
            booking = Booking.objects.filter(room_type=room_type, date=date).first()
            booked = booking.booked_count if booking else 0
            availability[room_type.id][date.isoformat()] = room_type.total_rooms - booked
    
    # Get recent feedback
    recent_feedback = Feedback.objects.all().order_by('-date')[:5]
    
    context = {
        'room_types': room_types,
        'mess_menu': mess_menu,
        'hostel_rules': hostel_rules,
        'warden_info': warden_info,
        'availability': json.dumps(availability),
        'recent_feedback': recent_feedback,
    }
    return render(request, 'hostel_app/index.html', context)

def about(request):
    return render(request, 'hostel_app/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            
            # Send email notification
            subject = f"New Contact Message: {contact_message.subject}"
            message = f"""
            Name: {contact_message.name}
            Email: {contact_message.email}
            Subject: {contact_message.subject}
            
            Message:
            {contact_message.message}
            """
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent. We will get back to you soon!')
            except Exception as e:
                messages.warning(request, 'Your message was saved but email notification failed. We will still process your inquiry.')
            
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'hostel_app/contact.html', {'form': form})

@login_required
def admission_apply(request):
    if request.method == 'POST':
        form = AdmissionForm(request.POST)
        if form.is_valid():
            resident = form.save(commit=False)
            resident.user = request.user
            
            # Generate unique admission code
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            resident.admission_code = code
            
            # Calculate total fees
            room_type = resident.room_type
            resident.total_fees = (room_type.price_monthly * resident.duration) + room_type.security_deposit
            
            resident.save()
            
            # Update bookings
            join_date = resident.join_date
            for i in range(resident.duration * 30):  # Approximate days in months
                date = join_date + timedelta(days=i)
                booking, created = Booking.objects.get_or_create(
                    room_type=room_type,
                    date=date,
                    defaults={'booked_count': 1}
                )
                if not created:
                    booking.booked_count += 1
                    booking.save()
            
            messages.success(request, f'Application submitted successfully! Your admission code is {code}')
            return redirect('index')
    else:
        form = AdmissionForm()
    
    return render(request, 'hostel_app/admission_form.html', {'form': form})

@login_required
def view_records(request):
    records = Resident.objects.filter(user=request.user).order_by('-join_date')
    return render(request, 'hostel_app/records.html', {'records': records})

@login_required
def cancel_admission(request, admission_code):
    resident = get_object_or_404(Resident, admission_code=admission_code, user=request.user)
    
    if resident.status != 'Pending Approval':
        messages.error(request, 'Only pending applications can be cancelled')
        return redirect('view_records')
    
    # Update resident status
    resident.status = 'Cancelled'
    resident.save()
    
    # Update bookings
    room_type = resident.room_type
    join_date = resident.join_date
    for i in range(resident.duration * 30):
        date = join_date + timedelta(days=i)
        booking = Booking.objects.filter(room_type=room_type, date=date).first()
        if booking:
            booking.booked_count -= 1
            booking.save()
    
    messages.success(request, 'Application cancelled successfully')
    return redirect('view_records')

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            
            # Check if user is a verified resident
            verified = Resident.objects.filter(
                user=request.user, 
                status='Confirmed'
            ).exists()
            feedback.verified = verified
            
            feedback.save()
            messages.success(request, 'Feedback submitted successfully')
            return redirect('index')
    else:
        form = FeedbackForm(initial={'email': request.user.email})
    
    return render(request, 'hostel_app/feedback_form.html', {'form': form})

@login_required
def book_laundry(request):
    if request.method == 'POST':
        form = LaundryBookingForm(request.POST)
        if form.is_valid():
            # Check if slots are available
            day = form.cleaned_data['day']
            bookings_count = LaundryBooking.objects.filter(
                day=day, 
                status='Booked'
            ).count()
            
            if bookings_count >= 10:
                messages.error(request, f'No slots available for {day}. Please choose another day.')
                return redirect('book_laundry')
            
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            
            messages.success(request, f'Laundry slot booked for {day}')
            return redirect('view_laundry')
    else:
        form = LaundryBookingForm(initial={'email': request.user.email})
    
    # Get availability for each day
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    availability = {}
    for day in days:
        bookings_count = LaundryBooking.objects.filter(day=day, status='Booked').count()
        availability[day] = 10 - bookings_count
    
    return render(request, 'hostel_app/laundry_form.html', {
        'form': form,
        'availability': availability
    })

@login_required
def view_laundry(request):
    bookings = LaundryBooking.objects.filter(user=request.user).order_by('-date')
    
    # Get availability for each day
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    availability = {}
    for day in days:
        bookings_count = LaundryBooking.objects.filter(day=day, status='Booked').count()
        availability[day] = 10 - bookings_count
    
    return render(request, 'hostel_app/laundry_bookings.html', {
        'bookings': bookings,
        'availability': availability
    })

@login_required
def cancel_laundry(request, booking_id):
    booking = get_object_or_404(LaundryBooking, id=booking_id, user=request.user)
    
    if booking.status != 'Booked':
        messages.error(request, 'Only active bookings can be cancelled')
        return redirect('view_laundry')
    
    booking.status = 'Cancelled'
    booking.save()
    
    messages.success(request, 'Laundry booking cancelled successfully')
    return redirect('view_laundry')

"""
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Save phone number to user profile or custom user model
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'hostel_app/register.html', {'form': form})
"""
@csrf_exempt
def api_room_availability(request):
    room_type_id = request.GET.get('room_type_id')
    if not room_type_id:
        return JsonResponse({'error': 'Room type ID is required'}, status=400)
    
    room_type = get_object_or_404(RoomType, id=room_type_id)
    today = timezone.now().date()
    
    availability = {}
    for i in range(30):
        date = today + timedelta(days=i)
        booking = Booking.objects.filter(room_type=room_type, date=date).first()
        booked = booking.booked_count if booking else 0
        availability[date.isoformat()] = room_type.total_rooms - booked
    
    return JsonResponse(availability)

@csrf_exempt
def api_room_types(request):
    room_types = RoomType.objects.all()
    data = []
    
    for room_type in room_types:
        # Get images
        images = [img.image.url for img in room_type.images.all()]
        
        # Get amenities
        amenities = [amenity.name for amenity in room_type.amenities.all()]
        
        # Get availability
        today = timezone.now().date()
        booking = Booking.objects.filter(room_type=room_type, date=today).first()
        booked = booking.booked_count if booking else 0
        available = room_type.total_rooms - booked
        
        data.append({
            'id': room_type.id,
            'type': room_type.type_name,
            'capacity': room_type.capacity,
            'priceMonthlyINR': float(room_type.price_monthly),
            'securityDepositINR': float(room_type.security_deposit),
            'images': images,
            'total': room_type.total,
            'booked': booked,
            'amenities': amenities,
            'size': room_type.size,
            'floor': room_type.floor,
            'facilities': room_type.facilities,
            'maintenance': room_type.maintenance,
            'available': available
        })
    
    return JsonResponse({'room_types': data})

@login_required
def generate_receipt(request, admission_code):
    resident = get_object_or_404(Resident, admission_code=admission_code, user=request.user)
    
    # Create receipt text
    receipt_text = f"""
    SERENITY BOYS HOSTEL
    ADMISSION RECEIPT
    ==========================================
    
    Admission Code: {resident.admission_code}
    Date: {timezone.now().strftime('%d-%m-%Y')}
    
    RESIDENT INFORMATION:
    Name: {resident.name}
    Email: {resident.email}
    Phone: {resident.phone}
    College: {resident.college}
    
    ROOM INFORMATION:
    Room Type: {resident.room_type.type_name}
    Join Date: {resident.join_date}
    Duration: {resident.duration} months
    
    PAYMENT DETAILS:
    Monthly Rent: ₹{resident.room_type.price_monthly}
    Security Deposit: ₹{resident.room_type.security_deposit}
    Total Amount: ₹{resident.total_fees}
    Payment Method: {resident.get_payment_method_display()}
    Payment Status: {resident.payment_status}
    
    
    STATUS: {resident.status}
    
    ==========================================
    Thank you for choosing Serenity Boys Hostel!
    """
    
    # Create response
    response = HttpResponse(receipt_text, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="receipt_{admission_code}.txt"'
    return response

