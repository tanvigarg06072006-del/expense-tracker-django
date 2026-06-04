from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import(
    permission_classes
)
from expenses.models import Expense
from rest_framework.decorators import permission_classes

@api_view(["GET"])
@permission_classes([
    IsAuthenticated
])
def expense_list(request):

    expenses = Expense.objects.filter(
        user=request.user
    )

    data = []

    for expense in expenses:

        data.append({

            "title":
            expense.title,

            "amount":
            str(
                expense.amount
            ),

            "category":
            expense.category

        })

    return Response(
        data
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_api(request):
    return Response({"message": "JWT working"})

# Create your views here.
