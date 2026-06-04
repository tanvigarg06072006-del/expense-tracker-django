from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import authenticate , login
from .forms import SignUpForm

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


def login_user(request):

    if request.method == "POST":

        username = request.POST.get("username")

        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect("/")

        else:

            messages.error(
                request,
                "Invalid username or password"
            )

    return render(
        request,
        "accounts/login.html"
    )

def signup(request):
    if request.method == "POST":
        form = SignUpForm(
            request.POST
        )

        if form.is_valid():
            form.save()
            return redirect(
                "login"
            )
        
    else:
        form = SignUpForm()

    return render(
         request,
         "accounts/signup.html",
         {
             "form": form
         }

     )  

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logout successful"})
        except Exception as e:
            return Response({"error": "Invalid token"})     

# Create your views here.
