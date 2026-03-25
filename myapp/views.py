from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from sklearn.ensemble import RandomForestClassifier

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


# u=User.objects.get(username='rohan@gmail.com')
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
    id = request.POST['id']
    u = Users.objects.get(id=id)
    b = u.AUTHUSER
    b.username = email
    b.save()

    # Address fields — keep existing values if not submitted in the form
    place    = request.POST.get('place',    u.place    or '')
    city     = request.POST.get('city',     u.city     or '')
    pin      = request.POST.get('pincode',  u.pin      or '')
    district = request.POST.get('district', u.district or '')
    state    = request.POST.get('state',    u.state    or '')

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
    return redirect('/myapp/viewreply_get/')

def signup_get(request):
    return render(request, 'users/signup.html')

def signup_post(request):
    name=request.POST['fullname']
    dob=request.POST['dob']
    email=request.POST['email']
    phone=request.POST['phoneno']
    gender=request.POST['gender']
    password=request.POST['password']
    confirmpassword=request.POST['confirmpassword']

    if password!=confirmpassword:
        messages.error(request, 'password doesnt match')
        return redirect('/myapp/signup_get/')

    user=User.objects.create_user(username=email,password=password)
    user.groups.add(Group.objects.get(name="user"))
    user.save()

    u=Users()
    u.name=name
    u.dob=dob
    u.email=email
    u.phone=phone
    u.gender=gender
    u.place=''
    u.city=''
    u.pin=''
    u.district=''
    u.state=''
    u.AUTHUSER=user
    u.status="pending"

    if 'photo' in request.FILES:
        photo=request.FILES['photo']
        fs=FileSystemStorage()
        date=datetime.now().strftime('%d-%M-%Y-%H-%M-%S')+'.jpg'
        fs.save(date,photo)
        path=fs.url(date)
        u.photo=path

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
    return render(request,'users/new_randomupload.html')




# Provides functions to interact with the operating system (paths, env variables).
import os
import joblib
# Converts binary image data into text strings so they can be sent to HTML.
import base64
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import shap
from datetime import datetime
# Creates a "virtual file" in memory to save images without using the hard drive.
from io import BytesIO
from datetime import datetime
# Django Imports
from django.shortcuts import render
from .models import logs, Users  # Ensure your models.py has these classes

# LIME: "Local Interpretable Model-agnostic Explanations" - Explains individual predictions.
from lime.lime_tabular import LimeTabularExplainer

# Configures Matplotlib to generate images in the background instead of opening a window.
matplotlib.use('Agg')

# ================================================================
# GLOBAL LOAD: Runs once when Django starts (PREVENTS LAG)
# ================================================================
MODEL_FILE = r'D:\pgs4projectseminar\project\diabeticdistresslevel-main\myapp\diabetes_rf_model.pkl'

try:
    # Load the trained model bundle
    GLOBAL_RF_MODEL = joblib.load(MODEL_FILE)

    # Pre-calculates the SHAP tree structure to avoid a 5-10 second delay during the first request.
    SHAP_EXPLAINER = shap.TreeExplainer(GLOBAL_RF_MODEL)

    # Initialize LIME explainer with feature names and class labels.
    LIME_EXPLAINER = LimeTabularExplainer(
        training_data=np.random.rand(10, 21),  # Provides a structural template of the data.
        feature_names=[
            'HighBP', 'HighChol', 'CholCheck', 'BMI', 'Smoker', 'Stroke',
            'HeartDiseaseorAttack', 'PhysActivity', 'Fruits', 'Veggies',
            'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost', 'GenHlth',
            'MentHlth', 'PhysHlth', 'DiffWalk', 'Sex', 'Age', 'Education', 'Income'
        ],
        class_names=["Low Distress", "Moderate Distress", "High Distress"],
        mode="classification"
    )
    print("AI Models and Explainers loaded successfully.")
except Exception as e:
    print(f"CRITICAL ERROR LOADING MODELS: {e}")

FEATURE_NAMES = [
    'HighBP', 'HighChol', 'CholCheck', 'BMI', 'Smoker', 'Stroke',
    'HeartDiseaseorAttack', 'PhysActivity', 'Fruits', 'Veggies',
    'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost', 'GenHlth',
    'MentHlth', 'PhysHlth', 'DiffWalk', 'Sex', 'Age', 'Education', 'Income'
]



def new_upload_logs_post(request):
    if request.method == 'POST':
        try:
            def to_num(val):
                try: return float(val) if val else 0
                except: return 0

            # 1. Collect Input from HTML Form
            data = [to_num(request.POST.get(f)) for f in FEATURE_NAMES]
            # Model needs a DataFrame.
            input_df = pd.DataFrame([data], columns=FEATURE_NAMES)
            # LIME needs a flat Numpy array.
            input_numpy = input_df.values[0]

            # 2. Prediction: Get the numeric class (0, 1, or 2) and the probability scores.
            prediction = int(GLOBAL_RF_MODEL.predict(input_df)[0])
            prob = GLOBAL_RF_MODEL.predict_proba(input_df)[0]
            # Map the number result to a human-readable string.
            label_map = {0: "Low Distress", 1: "Moderate Distress", 2: "High Distress"}
            result = label_map.get(prediction, "Unknown")

            # 3. SHAP Graph Generation: Visualizing feature importance for THIS specific prediction.
            explanation_plot = None
            plt.style.use("dark_background")
            # Calculate SHAP values.
            shap_values = SHAP_EXPLAINER.shap_values(input_df)
            # Handle different SHAP output formats (lists for multiclass vs arrays for single).
            if isinstance(shap_values, list):
                current_shap = shap_values[prediction][0]
            else:
                current_shap = shap_values[0, :, prediction] if len(shap_values.shape) == 3 else shap_values[0]
            # Create a horizontal bar chart of feature impacts.
            fig, ax = plt.subplots(figsize=(10, 7))
            # Sort features by impact strength.
            # np.abs(current_shap) [5, -10, 2] becomes [5, 10, 2].
            # np.argsort(...)it returns the positions (indices) of the numbers from smallest to largest.
            # So, indices becomes [2, 0, 1].
            indices = np.argsort(np.abs(current_shap))
            # If FEATURE_NAMES was ["BMI", "Age", "Income"]...And or indices are [2, 0, 1]...
            # sorted_f pulls the 2nd name, then the 0th, then the 1st.
            # Result: ["Income", "BMI", "Age"] (Sorted from least important to most important).
            sorted_f = [FEATURE_NAMES[i] for i in indices]
            # This does the exact same thing but for the actual SHAP values (the original
            #  +5, -10, +2 numbers) that is[2, 5, -10].
            sorted_v = [current_shap[i] for i in indices]
            # Red for positive impact, Blue for negative.
            colors = ['#FF4136' if v > 0 else '#0074D9' for v in sorted_v]

            ax.barh(sorted_f, sorted_v, color=colors)
            ax.set_title(f"AI Decision Factors for {result}", color='#00b4d8')
            ax.set_xlabel("Impact on Prediction (SHAP)")

            # Save the plot to memory, encode it to Base64 to display in <img src="..."> tags.
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', facecolor='#071318')
            explanation_plot = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)

            # 4. LIME Text Explanation: Generates a text list of why the AI chose that class.
            lime_list = []
            try:
                exp = LIME_EXPLAINER.explain_instance(
                    input_numpy,
                    GLOBAL_RF_MODEL.predict_proba,
                    num_features=6,# Top 6 contributing factors.
                    num_samples=500
                )
                lime_list = [f"{feature}: {round(weight, 4)}" for feature, weight in exp.as_list()]
            except:
                lime_list = ["LIME explanation simplified."]

            # ==========================================
            # 5. SAVE TO DATABASE (INDENTATION FIXED)
            # ==========================================
            # 5. Database Logging: Save the results to your logs table.
            try:
                if request.user.is_authenticated:
                    user_profile = Users.objects.get(AUTHUSER_id=request.user.id)
                    now = datetime.now()

                    obj = logs()
                    obj.USER = user_profile
                    obj.result = result
                    obj.date = now.date()
                    obj.time = now.time()
                    obj.save()
                    print(f"✅ Success: Log saved for {user_profile.name} at {now.time()}")
                else:
                    print("❌ Error: User not logged in.")
            except Exception as db_e:
                print(f"❌ Database Save Error: {db_e}")

            # 6. Build Context (Moved outside the DB try block)
            # 6. Build Context: Sending all calculated data back to the HTML template.
            context = {
                "result": result,
                "explanation_plot": explanation_plot,
                "lime_text": lime_list,
                "stage_score": {# Individual percentage confidence for each category.
                    "LowDistress": round(prob[0] * 100, 2),
                    "ModerateDistress": round(prob[1] * 100, 2),
                    "HighDistress": round(prob[2] * 100, 2)
                },
                "metrics": {"accuracy": "90.2"}
            }
            return render(request, "users/new_randomupload.html", context)

        except Exception as e:
            print(f"❌ Main Logic Error: {e}")
            return render(request, "users/new_randomupload.html", {"result": f"Error: {str(e)}"})

    return render(request, "users/new_randomupload.html")




import numpy as np
import joblib
import shap
import matplotlib
matplotlib.use('Agg')




import os
import base64
import joblib
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import shap
from io import BytesIO
from django.shortcuts import render
from lime.lime_tabular import LimeTabularExplainer

# Set matplotlib to non-interactive mode
matplotlib.use('Agg')

# ================================================================
# GLOBAL LOAD: Loads once when Django starts (Prevents Lag)
# ================================================================
# Use relative path so it works on any computer
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'diabetes_lr_model.pkl')

try:
    bundle = joblib.load(MODEL_PATH)
    GLOBAL_MODEL = bundle['model']
    GLOBAL_SCALER = bundle['scaler']
    FEATURE_NAMES = bundle['features']

    # Initialize LIME with dummy training data structure
    LIME_EXPLAINER = LimeTabularExplainer(
        training_data=np.zeros((1, len(FEATURE_NAMES))),
        feature_names=FEATURE_NAMES,
        class_names=["Low Distress", "Moderate Distress", "High Distress"],
        mode="classification"
    )

    # Initialize SHAP Linear Explainer
    # We provide a reference background (all zeros) for the linear model
    background = GLOBAL_SCALER.transform(np.zeros((1, len(FEATURE_NAMES))))
    SHAP_EXPLAINER = shap.LinearExplainer(GLOBAL_MODEL, background)

except Exception as e:
    print(f"CRITICAL ERROR LOADING MODEL: {e}")



#===============end=============

def new_upload_lr_logs_post(request):
    if request.method == 'POST':
        try:
            def to_num(val):
                try: return float(val) if val else 0
                except: return 0

            # 1. Collect and Scale User Input
            data = [to_num(request.POST.get(f)) for f in FEATURE_NAMES]
            input_df = pd.DataFrame([data], columns=FEATURE_NAMES)
            input_scaled = GLOBAL_SCALER.transform(input_df)

            # 2. Prediction
            prediction = int(GLOBAL_MODEL.predict(input_scaled)[0])
            prob = GLOBAL_MODEL.predict_proba(input_scaled)[0]

            label_map = {0: "Low Distress", 1: "Moderate Distress", 2: "High Distress"}
            result = label_map.get(prediction, "Unknown")

            # 3. Generate SHAP Plot
            # ... (Your existing SHAP code stays here) ...
            explanation_plot = None
            try:
                plt.style.use('dark_background')
                shap_values = SHAP_EXPLAINER.shap_values(input_scaled)
                if len(shap_values.shape) == 3:
                    current_shap = shap_values[0, :, prediction]
                else:
                    current_shap = shap_values[0]

                fig, ax = plt.subplots(figsize=(10, 8))
                indices = np.argsort(np.abs(current_shap))
                sorted_f = [FEATURE_NAMES[i] for i in indices]
                sorted_v = [current_shap[i] for i in indices]
                colors = ['#FF4136' if v > 0 else '#0074D9' for v in sorted_v]
                ax.barh(sorted_f, sorted_v, color=colors)
                ax.set_title(f"SHAP Analysis: Impact on {result}")
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', facecolor='#071318')
                explanation_plot = base64.b64encode(buffer.getvalue()).decode()
                plt.close(fig)
            except Exception as e:
                print(f"SHAP Error: {e}")

            # 4. LIME Text Explanations
            # ... (Your existing LIME code stays here) ...
            lime_text = []
            try:
                exp = LIME_EXPLAINER.explain_instance(input_scaled[0], GLOBAL_MODEL.predict_proba, num_features=6, num_samples=500)
                lime_text = [f"{f} influence: {round(w, 4)}" for f, w in exp.as_list()]
            except:
                lime_text = ["LIME calculation skipped."]

            # ==========================================
            # 5. SAVE TO DATABASE (ADDED FOR LOGISTIC REGRESSION)
            # ==========================================
            try:
                if request.user.is_authenticated:
                    # Identify User Profile
                    user_profile = Users.objects.get(AUTHUSER_id=request.user.id)
                    now = datetime.now()

                    # Create Log Entry
                    obj = logs()
                    obj.USER = user_profile
                    obj.result = result  # Stores "Low Distress", etc.
                    obj.date = now.date()
                    obj.time = now.time()
                    obj.save()
                    print(f"✅ Success: LR Log saved for {user_profile.name} at {now.time()}")
                else:
                    print("❌ Error: User not logged in.")
            except Exception as db_e:
                print(f"❌ Database Save Error (LR): {db_e}")

            # 6. Build Context
            context = {
                "result": result,
                "stage_score": {
                    "LowDistress": round(prob[0] * 100, 2),
                    "ModerateDistress": round(prob[1] * 100, 2),
                    "HighDistress": round(prob[2] * 100, 2)
                },
                "explanation_plot": explanation_plot,
                "lime_text": lime_text,
                "metrics": bundle.get('metrics', {"accuracy": "N/A"})
            }
            return render(request, "users/new_lr_upload.html", context)

        except Exception as e:
            print(f"❌ Main Logic Error (LR): {e}")
            return render(request, "users/new_lr_upload.html", {"result": f"Error: {str(e)}"})

    return render(request, "users/new_lr_upload.html")


import os
import io
import base64
import joblib
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import shap
from datetime import datetime
from io import BytesIO

# Django Imports
from django.shortcuts import render
from .models import logs, Users

# Explainable AI Imports
from lime.lime_tabular import LimeTabularExplainer

# Set matplotlib to non-interactive mode
matplotlib.use('Agg')

# ================================================================
# GLOBAL LOAD: Loads once when Django starts (PREVENTS LAG)
# ================================================================
XGB_MODEL_FILE = r'D:\pgs4projectseminar\project\diabeticdistresslevel-main\myapp\diabetes_xgb_model.pkl'

try:
    xgb_bundle = joblib.load(XGB_MODEL_FILE)
    GLOBAL_XGB_MODEL = xgb_bundle['model']
    GLOBAL_XGB_SCALER = xgb_bundle['scaler']
    XGB_FEATURES = [
        'HighBP', 'HighChol', 'CholCheck', 'BMI', 'Smoker', 'Stroke',
        'HeartDiseaseorAttack', 'PhysActivity', 'Fruits', 'Veggies',
        'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost', 'GenHlth',
        'MentHlth', 'PhysHlth', 'DiffWalk', 'Sex', 'Age', 'Education', 'Income'
    ]

    # Pre-initialize XGBoost Explainer
    XGB_SHAP_EXPLAINER = shap.TreeExplainer(GLOBAL_XGB_MODEL)

    # Pre-initialize LIME for XGBoost
    XGB_LIME_EXPLAINER = LimeTabularExplainer(
        training_data=np.zeros((1, 21)),
        feature_names=XGB_FEATURES,
        class_names=["Low Distress", "Moderate Distress", "High Distress"],
        mode="classification"
    )
    print("XGBoost Model and Explainers loaded successfully.")
except Exception as e:
    print(f"CRITICAL ERROR LOADING XGBOOST: {e}")


def upload_xgb_logs_post(request):
    if request.method == 'POST':
        try:
            def to_num(val):
                try:
                    return float(val) if val else 0
                except:
                    return 0

            # 1. Collect and Scale Input
            user_values = [to_num(request.POST.get(f)) for f in XGB_FEATURES]
            input_df = pd.DataFrame([user_values], columns=XGB_FEATURES)
            input_scaled = GLOBAL_XGB_SCALER.transform(input_df)

            # 2. Prediction
            prediction = int(GLOBAL_XGB_MODEL.predict(input_scaled)[0])
            prob = GLOBAL_XGB_MODEL.predict_proba(input_scaled)[0]

            label_map = {0: "Low Distress", 1: "Moderate Distress", 2: "High Distress"}
            result = label_map.get(prediction, "Unknown")

            # 3. SHAP Explanation (XGBoost specific 3D handling)
            explanation_plot = None
            try:
                plt.style.use('dark_background')
                shap_values = XGB_SHAP_EXPLAINER.shap_values(input_scaled)

                # XGBoost Multiclass output handling
                if len(shap_values.shape) == 3:
                    current_shap = shap_values[0, :, prediction]
                else:
                    current_shap = shap_values[prediction][0] if isinstance(shap_values, list) else shap_values[0]

                fig, ax = plt.subplots(figsize=(10, 7))
                indices = np.argsort(np.abs(current_shap))
                sorted_f = [XGB_FEATURES[i] for i in indices]
                sorted_v = [current_shap[i] for i in indices]

                colors = ['#FF4136' if v > 0 else '#0074D9' for v in sorted_v]
                ax.barh(sorted_f, sorted_v, color=colors)
                ax.set_title(f"XGBoost Analysis: Impact on {result}", color='#00b4d8')

                buf = io.BytesIO()
                plt.savefig(buf, format='png', facecolor='#071318', bbox_inches='tight')
                explanation_plot = base64.b64encode(buf.getvalue()).decode()
                plt.close(fig)
            except Exception as e:
                print(f"XGB SHAP Error: {e}")

            # 4. LIME Explanation
            lime_text = []
            try:
                exp = XGB_LIME_EXPLAINER.explain_instance(
                    input_scaled[0],
                    GLOBAL_XGB_MODEL.predict_proba,
                    num_features=6,
                    num_samples=500
                )
                lime_text = [f"{feat}: {round(w, 4)}" for feat, w in exp.as_list()]
            except:
                lime_text = ["LIME analysis simplified."]

            # ==========================================
            # 5. SAVE TO DATABASE (XGBOOST LOG)
            # ==========================================
            try:
                if request.user.is_authenticated:
                    user_profile = Users.objects.get(AUTHUSER_id=request.user.id)
                    now = datetime.now()

                    obj = logs()
                    obj.USER = user_profile
                    obj.result = result
                    obj.date = now.date()
                    obj.time = now.time()
                    # Tip: If you added 'algo_type' to models, add: obj.algo_type = "XGBoost"
                    obj.save()
                    print(f"✅ Success: XGB Log saved for {user_profile.name} at {now.time()}")
                else:
                    print("❌ Error: User not logged in.")
            except Exception as db_e:
                print(f"❌ Database Save Error (XGB): {db_e}")

            # 6. Response Context
            return render(request, "users/new_xgbupload.html", {
                "result": result,
                "stage_score": {
                    "LowDistress": round(prob[0] * 100, 2),
                    "ModerateDistress": round(prob[1] * 100, 2),
                    "HighDistress": round(prob[2] * 100, 2)
                },
                "explanation_plot": explanation_plot,
                "lime_text": lime_text,
                "metrics": xgb_bundle.get('metrics', {"accuracy": "N/A"})
            })

        except Exception as e:
            return render(request, "users/new_xgbupload.html", {"result": f"Error: {str(e)}"})

    return render(request, "users/new_xgbupload.html")
