from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


# Create your views here.
def login_get(request):
    return render(request,'login.html')

def login_post(request):
    email=request.POST['email']
    password=request.POST['password']
    user=authenticate(request,username=email,password=password)
    if user is not None:
        login(request,user)
        if user.groups.filter(name='admin'):
            return redirect('/myapp/admin_home/')
        else:
            messages.error(request,'no such group')
            return redirect('/myapp/login_get/')
    else:
        messages.error(request, 'no user found')
        return redirect('/myapp/login_get/')


# u=User.objects.get(username='admin@gmail.com')
# u.set_password('12345')
# u.save()
def forgetpassword_get(request):
    return render(request, 'forgetpassword.html')
def forgetpassword_post(request):
    return

# A D M I N--------------------------------
def admin_home(request):
    return render(request, 'admins/admin_home.html')

def changepassword_get(request):
    return render(request, 'admins/changepassword.html')
def changepassword_post(request):
    password = request.POST['currentpassword']
    newpassword = request.POST['newpassword']
    confirmpassword = request.POST['confirmpassword']

    data=request.user
    if not data.check_password(password):
        messages.error(request, 'invalid current password')
        return redirect('/myapp/changepassword_get/')
    if newpassword!=confirmpassword:
        messages.error(request, 'password doesnt match')
        return redirect('/myapp/changepassword_get/')
    data.set_password(newpassword)
    data.save()
    return redirect('/myapp/login_get/')





def sentreply_get(request):
    return render(request, 'admins/sentreply.html')
def sentreply_post(request):
    return

def viewblockeduser_get(request):
    return render(request, 'admins/viewblockeduser.html')

def viewcomplaint_get(request):
    return render(request, 'admins/viewcomplaint.html')

def viewlogs_get(request):
    return render(request, 'admins/viewlogs.html')

def viewuser_get(request):
    return render(request, 'admins/viewuser.html')
#U S E R
def editprofile_get(request):
    return render(request, 'users/editprofile.html')
def editprofile_post(request):
    return

def sentcomplaint_get(request):
    return render(request, 'users/sentcomplaint.html')
def sentcomplaint_post(request):
    return

def signup_get(request):
    return render(request, 'users/signup.html')
def signup_post(request):
    return

def viewprofile_get(request):
    return render(request, 'users/viewprofile.html')

def viewreply_get(request):
    return render(request, 'users/viewreply.html')

def ratingandreview_get(request):
    return render(request, 'users/ratingandreview.html')
def ratingandreview_post(request):
    return


