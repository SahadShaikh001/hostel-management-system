from django import forms
from hostel_app.models import Resident, Booking, RoomType

class AdminResidentForm(forms.ModelForm):
    class Meta:
        model = Resident
        fields = ['name', 'email', 'phone', 'college', 'guardian', 'guardian_phone', 'room_type', 'join_date', 'duration', 'payment_method', 'payment_status', 'status', 'emergency_contact']
        widgets = {
            'join_date': forms.DateInput(attrs={'type': 'date'}),
        }

class AdminBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room_type', 'date', 'booked_count']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'room_type': forms.Select(choices=[(rt.id, rt.type_name) for rt in RoomType.objects.all()]),
        }