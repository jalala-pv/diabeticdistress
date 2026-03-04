from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect


# Create your views here.
from myapp.models import complaints, Users, logs, review


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
            if Users.objects.filter(AUTHUSER_id=request.user.id,status='blocked').exists():
                messages.error(request,'YOU ARE BLOCKED')
                return redirect('/myapp/login_get/')
            else:
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

def unblockeduser(request,id):
    Users.objects.filter(id=id).update(status="pending")
    return redirect('/myapp/viewblockeduser_get/')

def viewcomplaint_get(request):
    data=complaints.objects.all()
    return render(request, 'admins/viewcomplaint.html',{'complaint':data})

def viewlogs_get(request):
    data = logs.objects.all()
    return render(request, 'admins/viewlogs.html',{'logs':data})

def viewuser_get(request):
    data = Users.objects.filter(status='pending')
    return render(request, 'admins/viewuser.html', {'Users': data})



def adm_view_feedback(request):
    data=review.objects.all()
    return render(request,'admins/viewfeedback.html',{'data':data})


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
    complaint=request.POST['sentcomplaint']
    obj = complaints()
    obj.reply = 'pending'
    obj.status = "pending"
    obj.date = datetime.now().date()
    obj.complaint = complaint
    obj.USER = Users.objects.get(AUTHUSER_id=request.user.id)
    obj.save()
    messages.success(request,'Complaint Sended...')
    return redirect('/myapp/sentcomplaint_get/#a')

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
    data=complaints.objects.filter(USER__AUTHUSER_id=request.user.id)
    return render(request, 'users/viewreply.html',{'data':data})

def ratingandreview_get(request):
    return render(request, 'users/ratingandreview.html')

def ratingandreview_post(request):
    rate=request.POST['rating']
    rev=request.POST['review']
    from datetime import datetime
    r=review()
    r.date=datetime.now().date()
    r.review=rev
    r.rating=rate
    r.USER=Users.objects.get(AUTHUSER_id=request.user.id)
    r.save()
    return redirect('/myapp/view_rating/#a')

def view_rating(request):
    data=review.objects.all()
    return render(request,'users/view_rating.html',{'data':data})


def u_changepassword_get(request):
    return render(request, 'users/changepassword.html')
def u_changepassword_post(request):
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


def upload_logs(request):
    return render(request,'users/randomupload.html')




def upload_logs_post(request):
    import joblib
    import numpy as np
    import os
    age = float(request.POST['age'])
    gender = request.POST['gender']
    hypertension = int(request.POST['hypertension'])
    heartdisease = int(request.POST['heartdisease'])
    smokinghistory = request.POST['smokinghistory']
    bmi = float(request.POST['bmi'])
    hba1clevel = float(request.POST['hba1clevel'])
    bloodglucoselevel = float(request.POST['bloodglucoselevel'])

    # Load the trained model
    model_path = os.path.join(r'D:\diabeticdistress-master-01-03-26\diabeticdistress-master\myapp\diabetes_rf_model.pkl')
    model = joblib.load(model_path)
    # model = joblib.load(model_path)

    # Encode categorical features (same encoding used during training)
    from sklearn.preprocessing import LabelEncoder
    gender_encoder = LabelEncoder()
    smoking_encoder = LabelEncoder()

    # Fit encoders on training data categories
    gender_encoder.fit(['Male', 'Female', 'Other'])
    smoking_encoder.fit(['never', 'No Info', 'former', 'current', 'ever', 'not current'])

    gender_encoded = gender_encoder.transform([gender])[0]
    smoking_encoded = smoking_encoder.transform([smokinghistory])[0]

    # Prepare input
    input_data = np.array([[age, gender_encoded, hypertension, heartdisease, smoking_encoded,
                            bmi, hba1clevel, bloodglucoselevel]])

    # Predict
    prediction = model.predict(input_data)[0]

    result = "Diabetic" if prediction == 1 else "Non-Diabetic"

    l=logs()
    from datetime import datetime
    l.date=datetime.now().date()
    l.time=datetime.now().time()
    l.result=result
    l.USER=Users.objects.get(AUTHUSER_id=request.user.id)
    l.save()



    return render(request, 'users/randomupload.html', {'result': result})
