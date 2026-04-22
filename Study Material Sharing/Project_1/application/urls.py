"""
URL configuration for Project_1 project.

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
from django.urls import path ,include
#from application import views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('browse/', views.browse_materials, name='browse'),
    path('upload/', views.upload_material, name='upload'),
    path('view/<int:pk>/', views.view_material, name='view_material'),
    path('superuser/portal/', views.admin_main_dashboard, name='admin-dashboard'),
    path('superuser/reports/', views.admin_report_generation, name='admin-reports'),
    path('superuser/work/', views.admin_work_page, name='admin-work-page'),
    path('superuser/manage-users/', views.admin_manage_users, name='admin-manage-users'),
    path('superuser/security/change-password/', views.admin_change_password, name='admin-change-password'),
]
