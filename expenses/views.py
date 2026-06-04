from django.shortcuts import render, redirect
from django.db.models import Sum
from .forms import ExpenseForm
from .models import Expense
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import openpyxl
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Budget
from decimal import Decimal
import requests
from datetime import date
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from django.db.models.functions import TruncMonth, TruncDay

def dashboard(request):

    search = request.GET.get("search")
    category = request.GET.get("category")

    # -------------------------
    # 1. RECENT EXPENSES (SAFE TO SLICE)
    # -------------------------
    expenses = Expense.objects.filter(user=request.user)

    if search:
        expenses = expenses.filter(title__icontains=search)

    if category:
        expenses = expenses.filter(category=category)

    expenses = expenses.order_by("-id")[:5]   # ✅ slice ONLY here

    # -------------------------
    # 2. MONTHLY EXPENSES (NO SLICE)
    # -------------------------
    monthly_expenses = (
        Expense.objects
        .filter(user=request.user)   # ✅ fresh queryset (IMPORTANT FIX)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    total_sum = sum(item['total'] for item in monthly_expenses)
    months_count = len(monthly_expenses)

    average_monthly = total_sum / months_count if months_count > 0 else 0

    return render(request, "expenses/dashboard.html", {
        "expenses": expenses,
        "monthly_expenses": monthly_expenses,
        "average_monthly": average_monthly
    })



@login_required
def add_expense(request):

    if request.method == "POST":
        form = ExpenseForm(request.POST)

        if form.is_valid():
            expense = form.save(commit=False)

            expense.user = request.user

            if expense.category == "Other":
                expense.note = request.POST.get("note")

            expense.save()

            return redirect("dashboard")

    else:
        form = ExpenseForm()

    return render(request, "expenses/add_expense.html", {"form": form})


@login_required
def delete_expense(request, id):

    expense = Expense.objects.get(
        id=id
    )

    expense.delete()

    return redirect(
        "dashboard"
    )


@login_required
def edit_expense(request, id):

    expense = Expense.objects.get(
        id=id
    )

    if request.method == "POST":

        form = ExpenseForm(
            request.POST,
            instance=expense
        )

        if form.is_valid():

            form.save()

            return redirect(
                "dashboard"
            )

    else:

        form = ExpenseForm(
            instance=expense
        )

    return render(
        request,
        "expenses/edit_expense.html",
        {
            "form": form
        }
    ) 

@login_required
def export_excel(request):

    expenses = Expense.objects.filter(
        user=request.user
    )

    workbook = openpyxl.Workbook()

    sheet = workbook.active

    sheet.title = "Expenses"

    sheet.append([
        "Title",
        "Amount",
        "Category",
        "Date"
    ])

    for expense in expenses:

        sheet.append([
            expense.title,
            expense.amount,
            expense.category,
            str(expense.created_at)
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="expenses.xlsx"'

    workbook.save(
        response
    )

    return response

@login_required
def financial_health_page(request):

    today = date.today()

    expenses = Expense.objects.filter(
        user=request.user,
        created_at__month=today.month,
        created_at__year=today.year
    )

    total_expense = expenses.aggregate(total=Sum("amount"))["total"] or 0

    current_month = today.strftime("%B")
    current_year = today.year

    monthly_budget_obj = Budget.objects.filter(
        user=request.user,
        month=current_month,
        year=current_year,
        is_total=True
    ).first()

    monthly_budget = monthly_budget_obj.total_budget if monthly_budget_obj else 0

    current_day = today.day
    total_days = 30

    ideal_daily_expense = monthly_budget / total_days if monthly_budget else 0
    expected_expense = ideal_daily_expense * current_day

    remaining_budget = monthly_budget - total_expense

    status = "Overspending ⚠️" if total_expense > expected_expense else "On Track ✅"

    chart_data = []
    running_total = 0

    for day in range(1, current_day + 1):
        day_total = sum(exp.amount for exp in expenses if exp.created_at.day == day)
        running_total += float(day_total)

        chart_data.append({
            "day": f"Day {day}",
            "ideal": round(ideal_daily_expense * day, 2),
            "actual": round(running_total, 2)
        })

    def get_budget(cat):
        return Budget.objects.filter(
            user=request.user,
            category=cat,
            month=current_month,
            year=current_year
        ).aggregate(total=Sum("total_budget"))["total"] or 0

    def get_expense(cat):
        return expenses.filter(category=cat).aggregate(total=Sum("amount"))["total"] or 0

    categories = ["Travel", "Bills", "Food", "Shopping", "Other"]

    category_data = []

    for cat in categories:
        budget = get_budget(cat)
        spent = get_expense(cat)

        category_data.append({
            "category": cat,
            "budget": budget,
            "spent": spent,
            "remaining": max(budget - spent, 0)
        })

    return render(request, "expenses/financial_health.html", {
        "monthly_budget": monthly_budget,
        "total_expense": total_expense,
        "remaining_budget": remaining_budget,
        "ideal_daily_expense": round(ideal_daily_expense, 2),
        "expected_expense": round(expected_expense, 2),
        "status": status,
        "chart_data": chart_data,
        "category_data": category_data
    })





@login_required
def budget_planner(request):

    error = None

    month = request.GET.get("month") or request.POST.get("month")
    year = request.GET.get("year") or request.POST.get("year")

    if not month:
        month= date.today().strftime("%B")

    if not year:
        year = date.today().year    
        
    month = month.strip().capitalize()
    year = int(year)

    budgets = Budget.objects.filter(
        user=request.user,
        month=month,
        year=year
    )

    total_budget_obj = budgets.filter(is_total=True).first()
    total_budget = total_budget_obj.total_budget if total_budget_obj else 0

    allocations = budgets.filter(is_total=False)

    total_allocated = allocations.aggregate(
        total=Sum("total_budget")
    )["total"] or 0

    remaining = total_budget - total_allocated

    if request.method == "POST":

        if request.POST.get("total_budget"):

            amount = float(request.POST.get("total_budget"))
            month = request.POST.get("month").strip().capitalize()
            year = int(request.POST.get("year"))

            existing = Budget.objects.filter(
                user=request.user,
                month=month,
                year=year,
                is_total=True
            ).first()

            if existing:
                existing.total_budget = amount
                existing.save()
            else:
                Budget.objects.create(
                    user=request.user,
                    month=month,
                    year=year,
                    total_budget=amount,
                    is_total=True
                )

            return redirect(f"/budget/?month={month}&year={year}")

        elif request.POST.get("category"):

            category = request.POST.get("category")
            amount = float(request.POST.get("monthly_budget"))

            if total_budget == 0:
                error = "Please set total monthly budget first."

            elif amount > remaining:
                error = f"Only ₹{remaining} remaining to allocate."

            else:
                Budget.objects.create(
                    user=request.user,
                    month=month,
                    year=year,
                    category=category,
                    total_budget=amount,
                    is_total=False
                )

                return redirect(f"/budget/?month={month}&year={year}")

    all_budgets = Budget.objects.filter(
        user=request.user,
        is_total=True
    ).order_by("-year", "-month")

    all_history = Budget.objects.filter(
        user=request.user
    ).order_by("-year","-month")

    return render(request, "expenses/budget_planner.html", {
        "budgets": budgets,
        "allocations": allocations,
        "total_budget": total_budget,
        "total_allocated": total_allocated,
        "remaining": remaining,
        "error": error,
        "month": month,
        "year": year,
        "all_budgets": all_budgets,
        "all_history": all_history
    })

@login_required
def edit_budget(request, budget_id):

    budget = Budget.objects.get(
        id=budget_id,
        user=request.user
    )

    if request.method == "POST":

        budget.total_budget = request.POST.get("amount")
        budget.save()

        return redirect("budget_planner")

    return render(
        request,
        "expenses/edit_budget.html",
        {"budget": budget}
    )

@login_required
def delete_budget(request, budget_id):

    budget = Budget.objects.get(
        id=budget_id,
        user=request.user
    )

    budget.delete()

    return redirect("budget_planner")

@login_required
def edit_total_budget(request,pk):

    budget = get_object_or_404(
        Budget,
        id=pk,
        user=request.user,
        is_total=True
    )

    if request.method == "POST":
        budget.total_budget = request.POST.get(
            "total_budget"
        )

        budget.save()

        return redirect(
            f"/budget/?month={budget.month}&year={budget.year}"
        )
    
    return render(
        request,
        "expenses/edit_total_budget.html",
        {
            "budget": budget
        }
    )
    
    
@login_required
def delete_total_budget(request,pk):
    budget= get_object_or_404(
        Budget,
        id=pk,
        user=request.user,
        is_total=True
    ) 

    month=budget.month
    year=budget.year

    budget.delete()

    return redirect(
        f"/budget/?month={month}&year={year}"
    )  

@login_required
def currency_converter(request):

    result = None
    error = None

    if request.method == "POST":

        from_currency = request.POST.get("from_currency")
        to_currency = request.POST.get("to_currency")
        amount = request.POST.get("amount")

        try:
            amount = float(amount)

            url = f"https://api.frankfurter.app/latest?from={from_currency}"
            response = requests.get(url, timeout=5)
            data = response.json()
            print(data)

            rates = data.get("rates")

            if not rates:
                error = "API did not return rates. Try again later."

            elif to_currency not in rates:
                error = "Invalid target currency code"

            else:
                conversion_rate = rates[to_currency]
                result = amount * conversion_rate

        except Exception as e:
            error = "Error: " + str(e)

    return render(
        request,
        "expenses/currency_converter.html",
        {
            "result": result,
            "error": error
        }
    )

@login_required
def ai_suggestions(request):

    expenses = Expense.objects.filter(
        user=request.user
    )

    total = (
        expenses.aggregate(
            Sum("amount")
        )["amount__sum"] or 0
    )

    food_total = expenses.filter(
        category="Food"
    ).aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    travel_total = expenses.filter(
        category="Travel"
    ).aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    shopping_total = expenses.filter(
        category="Shopping"
    ).aggregate(
        Sum("amount")
    )["amount__sum"] or 0

    suggestions = []

    if total > 10000:
        suggestions.append(
            "Your overall spending is high this month."
        )

    if food_total > 3000:
        suggestions.append(
            "Food spending is high."
        )

    if travel_total > 2000:
        suggestions.append(
            "Travel spending is increasing."
        )

    if shopping_total > 4000:
        suggestions.append(
            "Shopping expenses are high."
        )

    if not suggestions:

        suggestions.append(
            "Great job! Your spending looks balanced."
        )

    return render(
        request,
        "expenses/ai_suggestions.html",
        {
            "suggestions": suggestions,
            "total": total
        }
    ) 



def send_daily_reminder():

    today = date.today()

    users = User.objects.all()

    for user in users:

        expenses_today = Expense.objects.filter(user=user, created_at=today)

        if not expenses_today.exists():

            send_mail(
                subject="📊 Expense Reminder",
                message="You haven't added today's expenses yet. Please update your financial records.",
                from_email="yourgmail@gmail.com",
                recipient_list=[user.email],
                fail_silently=False
            )              