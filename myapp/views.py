from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


# Create your views here.
from myapp.models import complaints, Users, logs


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


def logout_get(request):
    logout(request)
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



def sentreply_get(request,id):
    return render(request, 'admins/sentreply.html',{'id':id})
def sentreply_post(request):
    id = request.POST['id']
    reply = request.POST['reply']
    data=complaints.objects.get(id=id)
    data.reply=reply
    data.status="replied"
    data.save()
    return redirect('/myapp/viewcomplaint_get/')

def viewblockeduser_get(request):
    data = Users.objects.filter(status='blocked')
    return render(request, 'admins/viewblockeduser.html', {'Users': data})

def blockeduser(request,id):
    Users.objects.filter(id=id).update(status="blocked")
    return redirect('/myapp/viewblockeduser_get/')

def viewcomplaint_get(request):
    data=complaints.objects.all()
    return render(request, 'admins/viewcomplaint.html',{'complaint':data})

def viewlogs_get(request):
    data = logs.objects.all()
    return render(request, 'admins/viewlogs.html',{'logs':data})

def viewuser_get(request):
    data = Users.objects.all()
    return render(request, 'admins/viewuser.html', {'Users': data})


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


