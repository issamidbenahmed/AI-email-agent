from django.urls import path
from django.contrib import admin
from django.views.generic import RedirectView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views
from .views import student_list

urlpatterns = [
    path('admin/', admin.site.urls),  # Optionnel si vous utilisez l'admin Django
    path('', RedirectView.as_view(url='/login/')),  # Redirige vers la page de login
    path('login/', views.login_view, name='login'),  # Utiliser ta vue personnalisée
    path('logout/', views.logout_view, name='logout'),
    path('handle-emails/', views.handle_emails, name='handle_emails'),
    path('students/', views.student_list, name='student_list'),
]
