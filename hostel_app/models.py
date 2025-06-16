from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class RoomType(models.Model):
    """
    Model to represent different types of rooms (e.g., Single, Double, Dorm).
    """
    type_name = models.CharField(max_length=100, unique=True, help_text="Name of the room type (e.g., Single Room)")
    capacity = models.IntegerField(help_text="Maximum capacity of the room")
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monthly rental price")
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, help_text="Security deposit amount")
    total_rooms = models.IntegerField(help_text="Total number of rooms available")
    size = models.CharField(max_length=50, help_text="Size of the room (e.g., 10x10 sq ft)")
    floor = models.CharField(max_length=50, help_text="Floor number or location")
    facilities = models.TextField(blank=True, help_text="General facilities description")
    maintenance = models.TextField(blank=True, help_text="Maintenance notes")

    def __str__(self):
        return self.type_name

class RoomImage(models.Model):
    """
    Model to store images for room types.
    """
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='room_images/', help_text="Upload image of the room")

    def __str__(self):
        return f"Image for {self.room_type.type_name}"

"""class RoomAmenity(models.Model):
    
    Model to represent amenities available for rooms (e.g., Wi-Fi, AC).
    
    name = models.CharField(max_length=100, unique=True, help_text="Name of the amenity (e.g., Wi-Fi)")
    description = models.TextField(blank=True, help_text="Description of the amenity")

    def __str__(self):
        return self.name

    # Remove the ForeignKey to RoomType; use ManyToManyField in RoomType instead
    # The relationship will be managed via RoomType.amenities"""
class RoomAmenity(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='amenities')
    amenity_name = models.CharField(max_length=100)

    def __str__(self):
        return self.amenity_name
    
class Resident(models.Model):
    """
    Model to represent hostel residents.
    """
    STATUS_CHOICES = [
        ('Pending Approval', 'Pending Approval'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('upi', 'UPI'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='residencies')
    admission_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    college = models.CharField(max_length=200)
    guardian = models.CharField(max_length=100)
    guardian_phone = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=20)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    join_date = models.DateField(default=timezone.now)
    duration = models.IntegerField(help_text="Duration in months")
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending Approval')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.admission_code}"

class Booking(models.Model):
    """
    Model to represent room bookings.
    """
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    date = models.DateField()
    booked_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('room_type', 'date')

    def __str__(self):
        return f"{self.room_type.type_name} - {self.date} ({self.booked_count} booked)"

class Feedback(models.Model):
    """
    Model to store feedback from residents or visitors.
    """
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    text = models.TextField()
    date = models.DateField(default=timezone.now)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback by {self.email} - {self.rating} stars"

class MessMenu(models.Model):
    """
    Model to manage weekly mess menu.
    """
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    day = models.CharField(max_length=10, choices=DAY_CHOICES, unique=True)
    breakfast = models.CharField(max_length=200)
    lunch = models.CharField(max_length=200)
    dinner = models.CharField(max_length=200)

    def __str__(self):
        return f"Menu for {self.day}"

class LaundryBooking(models.Model):
    """
    Model to manage laundry service bookings.
    """
    STATUS_CHOICES = [
        ('Booked', 'Booked'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    items = models.IntegerField()  # Changed to IntegerField to count items
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Booked')

    def __str__(self):
        return f"Laundry booking by {self.email} for {self.day}"

class HostelRule(models.Model):
    """
    Model to store hostel rules.
    """
    rule = models.TextField()

    def __str__(self):
        return self.rule[:50]

class WardenInfo(models.Model):
    """
    Model to store warden contact information.
    """
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    email = models.EmailField()
    office_hours = models.CharField(max_length=100)
    emergency_contact = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class ContactMessage(models.Model):
    """
    Model to store contact messages from users.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} from {self.name}"
    
