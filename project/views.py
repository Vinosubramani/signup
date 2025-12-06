from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout,logout as auth_logout
from django.contrib.auth.models import User

def signup(request):
    msg=""
    if request.method =="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        password1 =request.POST.get('password1')

        if User.objects.filter(username=username).exists():
            msg="username already exists"
        else:
            if password == password1:
                User.objects.create(username=username, password=password)
                user.save()

                return redirect("login")
            else:
                msg="password and confirm password must be same"

    return render(request,"signup.html",{"msg":msg})
            


def user_login(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            print(user)
            login(request, user)
            print(request)

            # CHECK USER TYPE
            if user.is_superuser:
                print(user)
                return redirect('/master-admin/')   # for superuser
                
                #return redirect('/auth_logout/')
            elif user.is_staff:
                print(user)
                print("Staff")
                return redirect('/staff/')  # for staff user
            else:
                print(user)
                print("user")
                return redirect('/student/')

        return render(request, 'login.html', {'error': 'Invalid Username or Password!'})

    return render(request, 'login.html')


def logout_view(request):


    
    is_superuser = request.user.is_superuser
    auth_logout(request)

    if is_superuser:
        return redirect('/admin/')
    else:
        return redirect('/')
        
    

    