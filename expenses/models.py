from django.db import models
from django.contrib.auth.models import User


class Expense(models.Model):

    CATEGORY = [
        ('Food', 'Food'),
        ('Travel', 'Travel'),
        ('Shopping', 'Shopping'),
        ('Bills', 'Bills'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=100
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY
    )

    note = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class Budget(models.Model):

    CATEGORY_CHOICES = [
        ("Food", "Food"),
        ("Travel", "Travel"),
        ("Shopping", "Shopping"),
        ("Bills", "Bills"),
        ("Entertainment", "Entertainment"),
        ("Other", "Other"),
    ]

    MONTH_CHOICES = [
        ("January", "January"),
        ("February", "February"),
        ("March", "March"),
        ("April", "April"),
        ("May", "May"),
        ("June", "June"),
        ("July", "July"),
        ("August", "August"),
        ("September", "September"),
        ("October", "October"),
        ("November", "November"),
        ("December", "December"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    month = models.CharField(
        max_length=20,
        choices=MONTH_CHOICES
    )

    year = models.IntegerField()

    total_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True
    )

    is_total = models.BooleanField(
        default=False
    )

    note=models.CharField(max_length=225,blank=True,null=True)

    def __str__(self):
        if self.is_total:
            return f"{self.user.username} - TOTAL - {self.month} {self.year}"

        return f"{self.user.username} - {self.category} - {self.month} {self.year}"


