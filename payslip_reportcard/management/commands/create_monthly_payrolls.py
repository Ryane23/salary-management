from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from payslip_reportcard.models import PayrollEmployee, Payroll

class Command(BaseCommand):
    help = 'Create monthly payrolls for all active employees'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=int,
            help='Month number (1-12)',
            default=timezone.now().month
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Year',
            default=timezone.now().year
        )
        parser.add_argument(
            '--company',
            type=str,
            help='Company name (optional)',
        )

    def handle(self, *args, **options):
        month = options['month']
        year = options['year']
        company_name = options.get('company')

        if month < 1 or month > 12:
            self.stdout.write(
                self.style.ERROR('Month must be between 1 and 12')
            )
            return

        # Get employees
        employees = PayrollEmployee.objects.filter(is_active=True)
        if company_name:
            employees = employees.filter(company__name__icontains=company_name)

        created_count = 0
        skipped_count = 0

        for employee in employees:
            payroll, created = Payroll.objects.get_or_create(
                employee=employee,
                month=month,
                year=year,
                defaults={
                    'attendance_days': 22,  # Default working days
                    'bonus': 0,
                    'deductions': 0,
                    'created_by': employee.user,  # Will need to be updated by HR
                }
            )

            if created:
                created_count += 1
                self.stdout.write(f'Created payroll for {employee.full_name}')
            else:
                skipped_count += 1
                self.stdout.write(f'Payroll already exists for {employee.full_name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Process completed. Created: {created_count}, Skipped: {skipped_count}'
            )
        )
