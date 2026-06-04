from django.urls import path
from .views import signup
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView


urlpatterns = [

    path(
        "signup/",
        signup,
        name="signup"
    ),

    path(
        "login/",
        LoginView.as_view(
            template_name="accounts/login.html"
        ),
        name="login"
    ),

    path(
        "logout/",
        LogoutView.as_view(),
        name="logout"
    ),

]