from django.apps import AppConfig


class PayslipReportcardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payslip_reportcard'
    verbose_name = 'Payroll Management System'

    def ready(self):
        """Import signals when the app is ready."""
        import payslip_reportcard.signals
