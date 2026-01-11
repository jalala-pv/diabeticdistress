from django.shortcuts import render

# Create your views here.
def login_get(request):
    return render(request,'login.html')

def login_post(request):
    return

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
    return


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


