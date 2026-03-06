from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
import joblib
import numpy as np
import os
import shap
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from .models import logs, Users


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








# import numpy as np
# import joblib
# import shap
# import matplotlib
#
# matplotlib.use('Agg')  # Required for non-GUI environments like Django
# import matplotlib.pyplot as plt
# import pandas as pd
# import base64
# from io import BytesIO
# from django.shortcuts import render
#
#
# def upload_logs_post(request):
#     if request.method == 'POST':
#         try:
#             def to_num(val):
#                 if val is None or val == '': return 0
#                 try:
#                     return float(val)
#                 except ValueError:
#                     return 0
#
#             # 21 Features in EXACT training order
#             feature_names = [
#                 'HighBP', 'HighChol', 'CholCheck', 'BMI', 'Smoker', 'Stroke',
#                 'HeartDiseaseorAttack', 'PhysActivity', 'Fruits', 'Veggies',
#                 'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost', 'GenHlth',
#                 'MentHlth', 'PhysHlth', 'DiffWalk', 'Sex', 'Age', 'Education', 'Income'
#             ]
#
#             data = [to_num(request.POST.get(f)) for f in feature_names]
#             input_data = np.array([data])
#
#             # Load Model
#             model_path = r'D:\diabeticdistress-master-01-03-26\diabeticdistress-master\myapp\diabetes_rf_model1.pkl'
#             model = joblib.load(model_path)
#
#             # Fix: Use .classes_ (with underscore)
#             print("Model Classes identified:", model.classes_)
#
#             # Prediction
#             prediction_idx = int(model.predict(input_data)[0])
#             label_map = {0: "Low Distress", 1: "Moderate Distress", 2: "High Distress"}
#             result = label_map.get(prediction_idx, "Unknown")
#
#             # --- SHAP EXPLANATION LOGIC ---
#             explainer = shap.TreeExplainer(model)
#             shap_values = explainer.shap_values(input_data)
#
#             # Handle Multi-class SHAP output (list of arrays or 3D array)
#             if isinstance(shap_values, list):
#                 # Older SHAP versions: list[class_index][sample_index]
#                 shap_contrib = shap_values[prediction_idx][0]
#             else:
#                 # Newer SHAP versions: [sample, feature, class]
#                 # If 2D (binary), it might only have one set of values
#                 if len(shap_values.shape) == 3:
#                     shap_contrib = shap_values[0, :, prediction_idx]
#                 else:
#                     shap_contrib = shap_values[0]
#
#             # Create DataFrame for Plotting
#             shap_df = pd.DataFrame({
#                 'feature': feature_names,
#                 'shap_value': shap_contrib
#             })
#
#             # Sort by absolute impact
#             shap_df = shap_df.reindex(shap_df['shap_value'].abs().sort_values(ascending=True).index)
#
#             # Plotting with Dark Mode Theme
#             plt.style.use('dark_background')
#             fig, ax = plt.subplots(figsize=(10, 8))
#
#             colors = ['#FF4136' if v > 0 else '#0074D9' for v in shap_df['shap_value']]
#             ax.barh(shap_df['feature'], shap_df['shap_value'], color=colors)
#
#             ax.set_title(f'Why AI predicted: {result}', fontsize=14, color='#06A3DA', pad=20)
#             ax.set_xlabel('Impact on Prediction (SHAP Value)')
#             ax.spines['top'].set_visible(False)
#             ax.spines['right'].set_visible(False)
#
#             plt.tight_layout()
#
#             # Save plot to base64
#             buffer = BytesIO()
#             plt.savefig(buffer, format='png', bbox_inches='tight', facecolor='#11233E')
#             image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
#             plt.close(fig)
#
#             return render(request, 'users/randomupload.html', {
#                 'result': result,
#                 'explanation_plot': image_base64
#             })
#
#         except Exception as e:
#             import traceback
#             print(traceback.format_exc())  # Print full error to console for debugging
#             return render(request, 'users/randomupload.html', {'result': f"Error: {str(e)}"})
#
#     return render(request, 'users/randomupload.html')
import numpy as np
import joblib
import shap
import matplotlib

matplotlib.use('Agg')  # Prevents GUI errors on servers
import matplotlib.pyplot as plt
import pandas as pd
import base64
from io import BytesIO
from django.shortcuts import render


def upload_logs_post(request):
    if request.method == 'POST':
        try:
            def to_num(val):
                if val is None or val == '': return 0
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return 0

            # 21 Features in the EXACT order shown in the dataset image
            # Matches: B:HighBP, C:HighChol, D:CholCheck, E:BMI, F:Smoker, G:Stroke...
            feature_names = [
                'HighBP', 'HighChol', 'CholCheck', 'BMI', 'Smoker', 'Stroke',
                'HeartDiseaseorAttack', 'PhysActivity', 'Fruits', 'Veggies',
                'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost', 'GenHlth',
                'MentHlth', 'PhysHlth', 'DiffWalk', 'Sex', 'Age', 'Education', 'Income'
            ]

            # Extract data from POST in the correct sequence
            data = [to_num(request.POST.get(f)) for f in feature_names]
            input_data = np.array([data])

            # Load the Random Forest Model
            model_path = r'D:\diabeticdistress-master-01-03-26\diabeticdistress-master\myapp\diabetes_rf_model1.pkl'
            model = joblib.load(model_path)

            # Prediction logic
            prediction_idx = int(model.predict(input_data)[0])
            label_map = {0: "Low Distress", 1: "Moderate Distress", 2: "High Distress"}
            result = label_map.get(prediction_idx, "Unknown")

            # SHAP Explanation logic for multi-class
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(input_data)

            # Extract contributions for the specific class predicted
            if isinstance(shap_values, list):
                # SHAP returns a list of arrays (one per class)
                shap_contrib = shap_values[prediction_idx][0]
            else:
                # SHAP returns a 3D array [samples, features, classes]
                if len(shap_values.shape) == 3:
                    shap_contrib = shap_values[0, :, prediction_idx]
                else:
                    shap_contrib = shap_values[0]

            # Prepare data for visualization
            shap_df = pd.DataFrame({
                'feature': feature_names,
                'shap_value': shap_contrib
            })

            # Sort for a clean horizontal bar chart (lowest impact to highest)
            shap_df = shap_df.reindex(shap_df['shap_value'].abs().sort_values(ascending=True).index)

            # Visualization styling
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(10, 8))

            # Red for positive impact (increasing distress), Blue for negative
            colors = ['#FF4136' if v > 0 else '#0074D9' for v in shap_df['shap_value']]
            ax.barh(shap_df['feature'], shap_df['shap_value'], color=colors)

            ax.set_title(f'AI Decision Factors: {result}', fontsize=14, color='#06A3DA', pad=20)
            ax.set_xlabel('SHAP Value (Impact on prediction)')

            # Use True/False (Capitalized) to avoid NameErrors
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            plt.tight_layout()

            # Encode image to Base64 for the template
            buffer = BytesIO()
            # Match the background color to your CSS card-bg
            plt.savefig(buffer, format='png', bbox_inches='tight', facecolor='#11233E')
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close(fig)

            return render(request, 'users/randomupload.html', {
                'result': result,
                'explanation_plot': image_base64
            })

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return render(request, 'users/randomupload.html', {'result': f"Error: {str(e)}"})

    return render(request, 'users/randomupload.html')
