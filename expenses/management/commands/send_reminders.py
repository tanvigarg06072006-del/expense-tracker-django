from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.contrib.auth.models import User
from expenses.models import Expense
from datetime import date

class Command(BaseCommand):
    def handle(self,*args,**kwargs):
        today = date.today()
        users = User.objects.all()

        for user in users:

            expense_exists = Expense.objects.filter(
                user=user,
                created_at=today
            ).exists()

            if not expense_exists:

                send_mail(
                    subject="Expense Reminder",
                    message="You have not added today's expenses.",
                    from_email="yourgmail@gmail.com",
                    recipient_list=[user.email],
                    fail_silently=False
                )

                print(f"Reminder sent to {user.email}")

        self.stdout.write(
            self.style.SUCCESS("Reminder emails sent")
        )