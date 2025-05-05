from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from .models import Student

from .utils import fetch_emails, process_email
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Chercher l'utilisateur par l'email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user is not None and user.check_password(password):
            login(request, user)
            return redirect('handle_emails')  # Redirection vers la page souhaitée après connexion
        else:
            return render(request, 'login.html', {'error': 'Invalid email or password. Please try again.'})

    return render(request, 'login.html')

@login_required
def handle_emails(request):
    emails = fetch_emails()
    results = []  # Liste pour stocker les réponses au traitement des emails

    for email_content in emails:
        response = process_email(email_content)
        results.append({"email": email_content, "response": response})

    # Si aucun email n'a été trouvé
    if not emails:
        results.append({"email": None, "response": "Aucun email non lu trouvé."})

    # Rendre un template pour afficher les résultats
    return render(request, 'handle_emails.html', {"results": results})
def student_list(request):
    students = Student.objects.all()
    return render(request, 'student_list.html', {'students': students})

def logout_view(request):
    logout(request)  # Déconnexion de l'utilisateur
    return redirect('login')