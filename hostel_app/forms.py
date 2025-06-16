from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Resident, Booking, RoomType, RoomAmenity, Feedback, LaundryBooking, ContactMessage, MessMenu, HostelRule, WardenInfo, RoomImage
import random
import string

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # Simplify the form by customizing help texts
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname]
            
class UserLoginForm(AuthenticationForm):
    """
    Custom login form with Bootstrap styling.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class AdmissionForm(forms.ModelForm):
    """
    Form for resident admission, used for adding new residents.
    """
    class Meta:
        model = Resident
        fields = [
            'name', 'email', 'phone', 'college', 
            'room_type', 'join_date', 'duration', 'payment_method', 'payment_status', 'status', 
        ]
        widgets = {
            'join_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'payment_method': forms.Select(choices=Resident.PAYMENT_METHOD_CHOICES, attrs={'class': 'form-control'}),
            'payment_status': forms.Select(choices=Resident.PAYMENT_STATUS_CHOICES, attrs={'class': 'form-control'}),
            'status': forms.Select(choices=Resident.STATUS_CHOICES, attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        resident = super().save(commit=False)
        if commit:
            room_type = resident.room_type
            resident.total_fees = (room_type.price_monthly * resident.duration) + room_type.security_deposit
            resident.admission_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            resident.save()
        return resident

class AdminResidentForm(forms.ModelForm):
    """
    Enhanced form for admin to manage resident details, including room amenities.
    """
    amenities = forms.ModelMultipleChoiceField(
        queryset=RoomAmenity.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="Room Amenities"
    )

    class Meta:
        model = Resident
        fields = [
            'name', 'email', 'phone', 'college', 'guardian', 'guardian_phone',
            'room_type', 'join_date', 'duration', 'payment_method', 'payment_status',
            'status', 'emergency_contact', 'total_fees'
        ]
        widgets = {
            'join_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'total_fees': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'payment_method': forms.Select(choices=Resident.PAYMENT_METHOD_CHOICES, attrs={'class': 'form-control'}),
            'payment_status': forms.Select(choices=Resident.PAYMENT_STATUS_CHOICES, attrs={'class': 'form-control'}),
            'status': forms.Select(choices=Resident.STATUS_CHOICES, attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'college': 'College Name',
            'guardian': 'Guardian Name',
            'guardian_phone': 'Guardian Phone',
            'room_type': 'Room Type',
            'join_date': 'Join Date',
            'duration': 'Duration (Months)',
            'payment_method': 'Payment Method',
            'payment_status': 'Payment Status',
            'status': 'Resident Status',
            'emergency_contact': 'Emergency Contact',
            'total_fees': 'Total Fees (₹)',
        }

    def __init__(self, *args, **kwargs):
        super(AdminResidentForm, self).__init__(*args, **kwargs)
        if self.instance.pk and self.instance.room_type:
            self.fields['amenities'].queryset = RoomAmenity.objects.filter(room_type=self.instance.room_type)

    def save(self, commit=True):
        resident = super().save(commit=False)
        if commit:
            resident.save()
            if 'amenities' in self.cleaned_data and resident.room_type:
                resident.room_type.amenities.set(self.cleaned_data['amenities'])
            room_type = resident.room_type
            resident.total_fees = (room_type.price_monthly * resident.duration) + room_type.security_deposit
            resident.save()
        return resident

class AdminBookingForm(forms.ModelForm):
    """
    Form for admin to manage booking details.
    """
    class Meta:
        model = Booking
        fields = ['room_type', 'date', 'booked_count']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'room_type': forms.Select(attrs={'class': 'form-control'}, choices=[(rt.id, rt.type_name) for rt in RoomType.objects.all()]),
            'booked_count': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
        }
        labels = {
            'room_type': 'Room Type',
            'date': 'Booking Date',
            'booked_count': 'Number of Bookings',
        }

class FeedbackForm(forms.ModelForm):
    """
    Form for submitting feedback.
    """
    class Meta:
        model = Feedback
        fields = ['email', 'rating', 'text']
        widgets = {
            'rating': forms.Select(choices=Feedback.RATING_CHOICES, attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

class LaundryBookingForm(forms.ModelForm):
    """
    Form for managing laundry bookings.
    """
    class Meta:
        model = LaundryBooking
        fields = ['email', 'day', 'items']
        widgets = {
            'day': forms.Select(choices=LaundryBooking.DAY_CHOICES, attrs={'class': 'form-control'}),
            'items': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
        }

class ContactForm(forms.ModelForm):
    """
    Form for contact messages.
    """
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }

class CustomPasswordResetForm(PasswordResetForm):
    """
    Customized password reset form with Bootstrap styling.
    """
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'})
    )

class MessMenuForm(forms.ModelForm):
    """
    Form for managing the mess menu.
    """
    class Meta:
        model = MessMenu
        fields = ['day', 'breakfast', 'lunch', 'dinner']
        widgets = {
            'day': forms.Select(choices=MessMenu.DAY_CHOICES, attrs={'class': 'form-control'}),
            'breakfast': forms.TextInput(attrs={'class': 'form-control'}),
            'lunch': forms.TextInput(attrs={'class': 'form-control'}),
            'dinner': forms.TextInput(attrs={'class': 'form-control'}),
        }

class HostelRuleForm(forms.ModelForm):
    """
    Form for managing hostel rules.
    """
    class Meta:
        model = HostelRule
        fields = ['rule']
        widgets = {
            'rule': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class WardenInfoForm(forms.ModelForm):
    """
    Form for managing warden information.
    """
    class Meta:
        model = WardenInfo
        fields = ['name', 'contact', 'email', 'office_hours', 'emergency_contact']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'office_hours': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RoomImageForm(forms.ModelForm):
    """
    Form for uploading room images.
    """
    class Meta:
        model = RoomImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

class RoomTypeForm(forms.ModelForm):
    """
    Form for managing room types.
    """
    class Meta:
        model = RoomType
        fields = ['type_name', 'capacity', 'price_monthly', 'security_deposit', 'total_rooms', 'size', 'floor', 'facilities', 'maintenance']
        widgets = {
            'type_name': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'price_monthly': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'security_deposit': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'total_rooms': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'size': forms.TextInput(attrs={'class': 'form-control'}),
            'floor': forms.TextInput(attrs={'class': 'form-control'}),
            'facilities': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'maintenance': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }