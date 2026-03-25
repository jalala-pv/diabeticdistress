"""
URL configuration for diabeticdistress project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path

from myapp import views

urlpatterns = [
    path('login_get/',views.login_get),
    path('login_post/',views.login_post),

    path('forgetpassword_get/',views.forgetpassword_get),
    path('forgetpassword_post/',views.forgetpassword_post),

    path('changepassword_get/',views.changepassword_get),
    path('changepassword_post/',views.changepassword_post),

    path('sentreply_get/<id>',views.sentreply_get),
    path('sentreply_post/',views.sentreply_post),

    path('viewblockeduser_get/',views.viewblockeduser_get),

    path('blockeduser/<id>',views.blockeduser),
    path('unblockeduser/<id>',views.unblockeduser),

    path('viewcomplaint_get/',views.viewcomplaint_get),

    path('viewlogs_get/',views.viewlogs_get),

    path('viewuser_get/',views.viewuser_get),
    path('adm_view_feedback/',views.adm_view_feedback),
    #U S E R
    path('editprofile_get/<id>',views.editprofile_get),
    path('editprofile_post/',views.editprofile_post),

    path('sentcomplaint_get/',views.sentcomplaint_get),
    path('sentcomplaint_post/',views.sentcomplaint_post),
    path('upload_xgb_logs_post/',views.upload_xgb_logs_post),

    path('signup_get/',views.signup_get),
    path('signup_post/',views.signup_post),

    path('viewprofile_get/',views.viewprofile_get),

    path('user_home/',views.user_home),

    path('viewreply_get/',views.viewreply_get),

    path('logout_get/',views.logout_get),


    path('ratingandreview_get/',views.ratingandreview_get),
    path('ratingandreview_post/', views.ratingandreview_post),
    path('view_rating/', views.view_rating),

    path('u_changepassword_get/', views.u_changepassword_get),
    path('u_changepassword_post/', views.u_changepassword_post),

    path('admin_home/',views.admin_home),
    path('upload_logs/',views.upload_logs),
    # path('upload_logs_post/',views.upload_logs_post),
    path('new_upload_logs_post/',views.new_upload_logs_post),
    path('new_upload_lr_logs_post/',views.new_upload_lr_logs_post),
    # path('new_upload_xgb_logs_post/',views.new_upload_xgb_logs_post),
]
