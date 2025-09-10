# Generated migration for Payroll Management System

from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('payslip_reportcard', '0001_initial'),
        ('Dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('bank_balance', models.DecimalField(
                    decimal_places=2, 
                    help_text="Company's available funds for payroll", 
                    max_digits=15, 
                    validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Dashboard.user')),
            ],
            options={
                'verbose_name_plural': 'Companies',
            },
        ),
        migrations.CreateModel(
            name='ExtendedUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(
                    choices=[('Admin', 'Admin'), ('HR', 'HR'), ('Director', 'Director')], 
                    default='HR', 
                    max_length=20
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payslip_reportcard.company')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Dashboard.user')),
            ],
        ),
        migrations.CreateModel(
            name='PayrollEmployee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=15)),
                ('role', models.CharField(help_text="Employee's job role", max_length=100)),
                ('base_salary', models.DecimalField(
                    decimal_places=2, 
                    max_digits=10, 
                    validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]
                )),
                ('bank_name', models.CharField(blank=True, max_length=100)),
                ('bank_account_number', models.CharField(blank=True, max_length=30)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payslip_reportcard.company')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Dashboard.user')),
            ],
        ),
        migrations.CreateModel(
            name='Payroll',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendance_days', models.PositiveIntegerField(default=0, help_text='Number of days employee attended work')),
                ('bonus', models.DecimalField(
                    decimal_places=2, 
                    default=Decimal('0.00'), 
                    max_digits=10, 
                    validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]
                )),
                ('deductions', models.DecimalField(
                    decimal_places=2, 
                    default=Decimal('0.00'), 
                    max_digits=10, 
                    validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]
                )),
                ('final_salary', models.DecimalField(
                    decimal_places=2, 
                    editable=False, 
                    help_text='Auto-calculated: base_salary + bonus - deductions', 
                    max_digits=10
                )),
                ('payment_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(
                    choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Paid', 'Paid')], 
                    default='Pending', 
                    max_length=20
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('month', models.PositiveSmallIntegerField(choices=[(i, f"{i:02d}") for i in range(1, 13)])),
                ('year', models.PositiveSmallIntegerField()),
                ('approved_by', models.ForeignKey(
                    blank=True, 
                    null=True, 
                    on_delete=django.db.models.deletion.SET_NULL, 
                    related_name='approved_payrolls', 
                    to='Dashboard.user'
                )),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Dashboard.user')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payslip_reportcard.payrollemployee')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PayrollNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payslip_reportcard.payrollemployee')),
                ('payroll', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payslip_reportcard.payroll')),
            ],
            options={
                'ordering': ['-sent_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='payroll',
            unique_together={('employee', 'month', 'year')},
        ),
    ]
