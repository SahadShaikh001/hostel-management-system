from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.contrib import messages
from hostel_app.models import Resident, Booking, Feedback, LaundryBooking, RoomType
from hostel_app.forms import AdmissionForm
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO
import csv
from datetime import datetime, timedelta
import random
import string
from django.db.models import Sum

@staff_member_required
def dashboard(request):
    total_users = Resident.objects.count()
    active_bookings = Booking.objects.filter(date__gte=datetime.now().date()).count()
    available_rooms = sum(rt.total_rooms - (Booking.objects.filter(room_type=rt, date=datetime.now().date()).aggregate(total=Sum('booked_count'))['total'] or 0) for rt in RoomType.objects.all())
    monthly_revenue = Resident.objects.filter(join_date__month=datetime.now().month).aggregate(total=Sum('total_fees'))['total'] or 0
    recent_bookings = Booking.objects.order_by('-date')[:5]
    recent_applications = Resident.objects.order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'active_bookings': active_bookings,
        'available_rooms': available_rooms,
        'monthly_revenue': monthly_revenue,
        'recent_bookings': recent_bookings,
        'recent_applications': recent_applications,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)

@staff_member_required
def residents(request):
    residents = Resident.objects.all()
    return render(request, 'admin_dashboard/residents.html', {'residents': residents})

@staff_member_required
def bookings(request):
    bookings = Booking.objects.all()
    return render(request, 'admin_dashboard/bookings.html', {'bookings': bookings})

@staff_member_required
def feedback(request):
    feedback_list = Feedback.objects.all()
    return render(request, 'admin_dashboard/feedback.html', {'feedback_list': feedback_list})

@staff_member_required
def laundry(request):
    laundry_bookings = LaundryBooking.objects.all()
    return render(request, 'admin_dashboard/laundry.html', {'laundry_bookings': laundry_bookings})

@staff_member_required
def reports(request):
    return render(request, 'admin_dashboard/reports.html')

@staff_member_required
def download_report(request, report_type):
    if report_type == 'residents':
        data = Resident.objects.all()
        filename = "residents_report"
        headers = ['Name', 'Admission Code', 'Email', 'Phone', 'Room Type', 'Status']
        rows = [[r.name, r.admission_code, r.email, r.phone, r.room_type.type_name, r.status] for r in data]
    elif report_type == 'bookings':
        data = Booking.objects.all()
        filename = "bookings_report"
        headers = ['Room Type', 'Date', 'Booked Count']
        rows = [[b.room_type.type_name, b.date, b.booked_count] for b in data]
    else:
        return HttpResponse("Invalid report type", status=400)

    if request.GET.get('format') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.csv"'
        writer = csv.writer(response)
        writer.writerow(headers)
        writer.writerows(rows)
        return response

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    table_data = [headers] + rows
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#d3d3d3'),
        ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), '#f5f5f5'),
        ('GRID', (0, 0), (-1, -1), 1, '#000000'),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.pdf"'
    return response

@staff_member_required
def add_resident(request):
    if request.method == 'POST':
        form = AdmissionForm(request.POST)
        if form.is_valid():
            resident = form.save(commit=False)
            resident.user = request.user
            resident.admission_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            resident.total_fees = (resident.room_type.price_monthly * resident.duration) + resident.room_type.security_deposit
            resident.save()
            messages.success(request, f'Resident added successfully! Admission Code: {resident.admission_code}')
            return redirect('admin_residents')
    else:
        form = AdmissionForm()
    return render(request, 'admin_dashboard/resident_form.html', {'form': form, 'title': 'Add Resident'})

@staff_member_required
def update_resident(request, admission_code):
    resident = get_object_or_404(Resident, admission_code=admission_code)
    if request.method == 'POST':
        form = AdmissionForm(request.POST, instance=resident)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resident updated successfully')
            return redirect('admin_residents')
    else:
        form = AdmissionForm(instance=resident)
    return render(request, 'admin_dashboard/resident_form.html', {'form': form, 'title': 'Update Resident'})

@staff_member_required
def delete_resident(request, admission_code):
    resident = get_object_or_404(Resident, admission_code=admission_code)
    resident.delete()
    messages.success(request, 'Resident deleted successfully')
    return redirect('admin_residents')

@staff_member_required
def add_booking(request):
    if request.method == 'POST':
        room_type_id = request.POST.get('room_type')
        date = request.POST.get('date')
        booked_count = int(request.POST.get('booked_count', 0))
        room_type = get_object_or_404(RoomType, id=room_type_id)
        booking, created = Booking.objects.get_or_create(room_type=room_type, date=date, defaults={'booked_count': booked_count})
        if not created:
            booking.booked_count += booked_count
            booking.save()
        messages.success(request, 'Booking added successfully')
        return redirect('admin_bookings')
    room_types = RoomType.objects.all()
    return render(request, 'admin_dashboard/booking_form.html', {'room_types': room_types, 'title': 'Add Booking'})

# Added complementary views
@staff_member_required
def update_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        room_type_id = request.POST.get('room_type')
        date = request.POST.get('date')
        booked_count = int(request.POST.get('booked_count', 0))
        room_type = get_object_or_404(RoomType, id=room_type_id)
        
        booking.room_type = room_type
        booking.date = date
        booking.booked_count = booked_count
        booking.save()
        messages.success(request, 'Booking updated successfully')
        return redirect('admin_bookings')
    
    room_types = RoomType.objects.all()
    return render(request, 'admin_dashboard/booking_form.html', {
        'room_types': room_types,
        'booking': booking,
        'title': 'Update Booking'
    })

@staff_member_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    messages.success(request, 'Booking deleted successfully')
    return redirect('admin_bookings')

@staff_member_required
def add_laundry_booking(request):
    if request.method == 'POST':
        resident_id = request.POST.get('resident')
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        resident = get_object_or_404(Resident, id=resident_id)
        
        laundry_booking = LaundryBooking.objects.create(
            resident=resident,
            date=date,
            time_slot=time_slot
        )
        messages.success(request, 'Laundry booking added successfully')
        return redirect('admin_laundry')
    
    residents = Resident.objects.all()
    return render(request, 'admin_dashboard/laundry_form.html', {
        'residents': residents,
        'title': 'Add Laundry Booking'
    })

@staff_member_required
def update_laundry_booking(request, booking_id):
    laundry_booking = get_object_or_404(LaundryBooking, id=booking_id)
    if request.method == 'POST':
        resident_id = request.POST.get('resident')
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        resident = get_object_or_404(Resident, id=resident_id)
        
        laundry_booking.resident = resident
        laundry_booking.date = date
        laundry_booking.time_slot = time_slot
        laundry_booking.save()
        messages.success(request, 'Laundry booking updated successfully')
        return redirect('admin_laundry')
    
    residents = Resident.objects.all()
    return render(request, 'admin_dashboard/laundry_form.html', {
        'residents': residents,
        'laundry_booking': laundry_booking,
        'title': 'Update Laundry Booking'
    })

@staff_member_required
def delete_laundry_booking(request, booking_id):
    laundry_booking = get_object_or_404(LaundryBooking, id=booking_id)
    laundry_booking.delete()
    messages.success(request, 'Laundry booking deleted successfully')
    return redirect('admin_laundry')

@staff_member_required
def delete_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.delete()
    messages.success(request, 'Feedback deleted successfully')
    return redirect('admin_feedback')