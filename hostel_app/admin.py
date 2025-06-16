from django.contrib import admin
from .models import (
    RoomType, RoomImage, RoomAmenity, Resident, Booking,
    Feedback, MessMenu, LaundryBooking, HostelRule, WardenInfo
)

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 3

class RoomAmenityInline(admin.TabularInline):
    model = RoomAmenity
    extra = 5

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'capacity', 'price_monthly', 'total_rooms', 'floor')
    search_fields = ('type_name', 'floor')
    inlines = [RoomImageInline, RoomAmenityInline]

@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ('name', 'admission_code', 'room_type', 'join_date', 'duration', 'payment_status', 'status')
    list_filter = ('status', 'payment_status', 'room_type', 'join_date')
    search_fields = ('name', 'email', 'admission_code', 'phone')
    date_hierarchy = 'join_date'
    readonly_fields = ('admission_code', 'total_fees')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'date', 'booked_count')
    list_filter = ('room_type', 'date')
    date_hierarchy = 'date'

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('email', 'rating', 'date', 'verified')
    list_filter = ('rating', 'verified', 'date')
    search_fields = ('email', 'text')

@admin.register(MessMenu)
class MessMenuAdmin(admin.ModelAdmin):
    list_display = ('day', 'breakfast', 'lunch', 'dinner')
    list_filter = ('day',)

@admin.register(LaundryBooking)
class LaundryBookingAdmin(admin.ModelAdmin):
    list_display = ('email', 'day', 'items', 'date', 'status')
    list_filter = ('day', 'status', 'date')
    search_fields = ('email',)

@admin.register(HostelRule)
class HostelRuleAdmin(admin.ModelAdmin):
    list_display = ('rule',)

@admin.register(WardenInfo)
class WardenInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'email', 'office_hours')



