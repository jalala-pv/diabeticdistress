from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
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
        elif user.groups.filter(name='user'):

            return redirect('/myapp/user_home/')
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
def user_home(request):
    return render(request, 'users/users_home.html')
def editprofile_get(request,id):
    data=Users.objects.get(id=id)
    return render(request, 'users/editprofile.html',{'data':data})
def editprofile_post(request):
    name = request.POST['fullname']
    dob = request.POST['dob']
    email = request.POST['email']
    phone = request.POST['phoneno']
    gender = request.POST['gender']
    place = request.POST['place']
    city = request.POST['city']
    pin = request.POST['pincode']
    district = request.POST['district']
    state = request.POST['state']
    id = request.POST['id']
    u = Users.objects.get(id=id)
    b=u.AUTHUSER
    b.username=email
    b.save()

    if "photo" in request.FILES:
        photo = request.FILES['photo']

        fs = FileSystemStorage()
        date = datetime.now().strftime('%d-%M-%Y-%H-%M-%S') + '.jpg'
        fs.save(date, photo)
        path = fs.url(date)
        u.photo = path
        u.save()
    u.name = name
    u.dob = dob
    u.email = email
    u.phone = phone
    u.gender = gender
    u.place = place
    u.city = city
    u.pin = pin
    u.district = district
    u.state = state
    u.AUTHUSER = b
    u.status = "pending"
    u.save()
    return redirect('/myapp/viewprofile_get/')

def sentcomplaint_get(request):
    return render(request, 'users/sentcomplaint.html')
def sentcomplaint_post(request):
    return

def signup_get(request):
    return render(request, 'users/signup.html')

def signup_post(request):
    name=request.POST['fullname']
    dob=request.POST['dob']
    email=request.POST['email']
    phone=request.POST['phoneno']
    gender=request.POST['gender']
    photo=request.FILES['photo']
    place= request.POST['place']
    city = request.POST['city']
    pin = request.POST['pincode']
    district = request.POST['district']
    state = request.POST['state']
    password=request.POST['password']
    confirmpassword=request.POST['confirmpassword']

    if password!=confirmpassword:
        messages.error(request, 'password doesnt match')
        return redirect('/myapp/signup_get/')

    user=User.objects.create_user(username=email,password=password)
    user.groups.add(Group.objects.get(name="user"))
    user.save()

    fs=FileSystemStorage()
    date=datetime.now().strftime('%d-%M-%Y-%H-%M-%S')+'.jpg'
    fs.save(date,photo)
    path=fs.url(date)

    u=Users()
    u.name=name
    u.dob=dob
    u.email=email
    u.phone=phone
    u.gender=gender
    u.photo=path
    u.place=place
    u.city=city
    u.pin=pin
    u.district=district
    u.state=state
    u.AUTHUSER=user
    u.status="pending"
    u.save()
    return redirect('/myapp/login_get/')

def viewprofile_get(request):
    data=Users.objects.get(AUTHUSER=request.user)
    return render(request, 'users/viewprofile.html',{'data':data})

def viewreply_get(request):
    return render(request, 'users/viewreply.html')

def ratingandreview_get(request):
    return render(request, 'users/ratingandreview.html')
def ratingandreview_post(request):
    return


