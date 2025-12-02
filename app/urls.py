from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.user_login, name="login"),
    path('signup/',views.signup, name="signup"),
    path('dashboard/',views.dashboard, name="dashboard"),
    path('',views.user_login),
]