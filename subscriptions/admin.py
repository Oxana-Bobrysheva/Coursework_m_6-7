from django.contrib import admin
from .models import Mailing, Subscriber, Message, MailingAttempt


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'start_time', 'end_time', 'message', 'created_at',
                    'get_total_attempts', 'get_successful_attempts', 'get_failed_attempts', 'get_success_rate']
    list_filter = ['status', 'created_at']
    filter_horizontal = ['subscribers']
    readonly_fields = ['created_at', 'updated_at']

       # Register the Subscriber model
@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'comment')  # Fields to display in the list view
    search_fields = ('email', 'name')  # Fields to search by in the admin interface
    list_filter = ('name',)  # Fields to filter by in the admin interface

# Register the Message model
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject_of_the_letter',)  # Fields to display in the list view
    search_fields = ('subject_of_the_letter',)  # Fields to search by in the admin interface

@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ['mailing', 'subscriber', 'status', 'attempt_time']
    list_filter = ['status', 'attempt_time', 'mailing']
    search_fields = ['subscriber__email', 'mailing__message__subject']
    readonly_fields = ['attempt_time']
