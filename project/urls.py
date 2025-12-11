"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from project.views import user_login, logout_view,signup
from django.contrib.auth import views as auth_views



urlpatterns = [

    

    path('admin/logout/', auth_views.LogoutView.as_view(next_page='/'), name='admin_logout'),

    # Default admin
    path('admin/', admin.site.urls),

    path('admin/logout/', logout_view,name='admin_logout'),
    path('admin/', admin.site.urls),
    path('master-admin/',include('administartor.urls')),
    path('staff/',include("staff.urls")),
    path('student/',include('app.urls')),
    path('logout/', logout_view, name='logout'),
    path('signup/',signup, name="signup"),
    path('', user_login, name='login'),
    path('product', include('product.urls')),

]
