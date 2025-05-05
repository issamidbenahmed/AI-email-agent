"""
URL configuration for email_agent project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.views.generic import RedirectView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from email_processor import views
from email_processor.views import student_list

urlpatterns = [
    #path('admin/', admin.site.urls),
    #path('handle-emails/', views.handle_emails, name='handle_emails'),
    #path('', RedirectView.as_view(url='/students/')),
    #path('students/', student_list, name='student_list'),
    path('admin/', admin.site.urls),  # Optionnel si vous utilisez l'admin Django
    path('', RedirectView.as_view(url='/login/')),  # Redirige vers la page de login
    path('login/', views.login_view, name='login'),  # Utiliser ta vue personnalisée
    path('logout/', views.logout_view, name='logout'),
    path('handle-emails/', views.handle_emails, name='handle_emails'),
    path('students/', views.student_list, name='student_list'),

]
