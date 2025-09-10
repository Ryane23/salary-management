from django.core.management.base import BaseCommand
from django.db.models import Sum
from payslip_reportcard.models import Company, Payroll

class Command(BaseCommand):
    help = 'Update company bank balances'

    def add_arguments(self, parser):
        parser.add_argument(
            '--company',
            type=str,
            help='Company name to update (optional)',
        )
        parser.add_argument(
            '--amount',
            type=float,
            help='Amount to add to balance',
            required=True
        )

    def handle(self, *args, **options):
        company_name = options.get('company')
        amount = options['amount']

        if company_name:
            try:
                company = Company.objects.get(name__icontains=company_name)
                companies = [company]
            except Company.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Company "{company_name}" not found')
                )
                return
        else:
            companies = Company.objects.all()

        for company in companies:
            old_balance = company.bank_balance
            company.bank_balance += amount
            company.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Updated {company.name}: ${old_balance} -> ${company.bank_balance}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f'Updated {len(companies)} companies')
        )
