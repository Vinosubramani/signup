from django.shortcuts import render, redirect
from .models import Login


def signup(request):
    msg = ""
    
    if request.method == "POST":
        name = request.POST.get("username")
        pwd = request.POST.get("password")
        pwd1 = request.POST.get("password1")
        
        print(name)
        if Login.objects.filter(username=name).exists():
            
            msg = "username already exists"
        else:
            if pwd == pwd1:
               Login.objects.create(username=name, password=pwd)
               

               return redirect("login")
            else:
                msg = "Password and confirm password must be same "
        
    

    return render(request,"signup.html",{"msg":msg})

def user_login(request):
    error=""
    if request.method=="POST":
        name=request.POST.get("username")
        pwd = request.POST.get("password")

        user=Login.objects.filter(username=name,password=pwd).first()
        if user:
            return redirect("dashboard")
        else:
            error="Inalid username or password"
    return render(request, "login.html", {"error":error})

def dashboard(request):
    return render(request, "dashboard.html")