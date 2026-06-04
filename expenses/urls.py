from django.urls import path

from .views import (
    dashboard,
    add_expense,
    delete_expense,
    edit_expense,
    export_excel,
    financial_health_page,
    budget_planner,
    currency_converter,
    ai_suggestions
)
from . import views

urlpatterns = [

    path(
        "",
        dashboard,
        name="dashboard"
    ),

    path(
        "add/",
        add_expense,
        name="add_expense"
    ),

    path(
        "delete/<int:id>/",
        delete_expense,
        name="delete_expense"
    ),

    path(
        "edit/<int:id>/",
        edit_expense,
        name="edit_expense"
    ),

    path(
        "export/",
        export_excel,
        name="export_excel"
    ),

    path(
        "financial-health/",
        financial_health_page,
        name="financial_health_page"
    ),

    path(
        "budget/",
        budget_planner,
        name="budget_planner"
    ),

    path(
    "budget/edit/<int:budget_id>/",
    views.edit_budget,
    name="edit_budget"
),

path(
    "budget/delete/<int:budget_id>/",
    views.delete_budget,
    name="delete_budget"
),

path(
    "budget/edit-total/<int:pk>/",
    views.edit_total_budget,
    name="edit_total_budget"
),

path(
    "budget/delete-total/<int:pk>/",
    views.delete_total_budget,
    name="delete_total_budget"
),

    path(
        "currency/",
        currency_converter,
        name="currency_converter"
    ),

    path(
    "ai-suggestions/",
    ai_suggestions,
    name="ai_suggestions"
    ),

]