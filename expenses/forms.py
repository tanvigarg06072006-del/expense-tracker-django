from django import forms
from .models import Expense
from .models import Budget


class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense

        fields = [
            "title",
            "amount",
            "category",
           # 'note'
            
        ]


class BudgetForm(forms.ModelForm):

    class Meta:
        model = Budget

        fields = [
            "category",
            "month",
            "year",
            "total_budget",
        ]       