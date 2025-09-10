from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Payroll, PayrollNotification, PayrollEmployee

@receiver(post_save, sender=Payroll)
def send_payroll_notification(sender, instance, created, **kwargs):
    """
    Send notification when payroll status changes.
    """
    if not created and instance.status == 'Approved':
        # Check if this is a status change to 'Approved'
        try:
            previous_instance = Payroll.objects.get(pk=instance.pk)
            if hasattr(previous_instance, '_state') and previous_instance.status != 'Approved':
                # Send email notification if configured
                send_payroll_email_notification(instance)
        except Payroll.DoesNotExist:
            pass

def send_payroll_email_notification(payroll):
    """
    Send email notification for payroll approval.
    """
    try:
        employee = payroll.employee
        subject = f'Payroll Approved - {payroll.month:02d}/{payroll.year}'
        message = f"""
        Dear {employee.full_name},

        Your payroll for {payroll.month:02d}/{payroll.year} has been approved.
        
        Details:
        - Base Salary: ${payroll.employee.base_salary}
        - Bonus: ${payroll.bonus}
        - Deductions: ${payroll.deductions}
        - Final Salary: ${payroll.final_salary}
        
        Payment will be processed on: {payroll.payment_date if payroll.payment_date else 'To be determined'}
        
        Best regards,
        Payroll Management System
        """
        
        # Send email if email settings are configured
        if hasattr(settings, 'EMAIL_HOST') and employee.user.email:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@company.com',
                [employee.user.email],
                fail_silently=True,
            )
    except Exception as e:
        # Log error in production
        print(f"Error sending email notification: {e}")

@receiver(post_save, sender='Dashboard.User')
def create_extended_user(sender, instance, created, **kwargs):
    """
    Create ExtendedUser when a Dashboard.User is created.
    """
    if created:
        from .models import ExtendedUser
        ExtendedUser.objects.get_or_create(user=instance)

def send_sms_notification(phone_number, message):
    """
    Placeholder for SMS notification functionality.
    Integrate with SMS service like Twilio, AWS SNS, etc.
    """
    # TODO: Implement SMS sending logic
    # Example with Twilio:
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # client.messages.create(
    #     body=message,
    #     from_='+1234567890',
    #     to=phone_number
    # )
    print(f"SMS to {phone_number}: {message}")

@receiver(post_save, sender=PayrollNotification)
def handle_notification_created(sender, instance, created, **kwargs):
    """
    Handle actions when a new notification is created.
    """
    if created:
        # Send SMS if phone number is available
        if instance.employee.phone:
            sms_message = f"Payroll Update: {instance.message[:100]}..."
            send_sms_notification(instance.employee.phone, sms_message)
