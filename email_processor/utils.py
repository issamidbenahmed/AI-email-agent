import imaplib
import email
from email.header import decode_header
import re
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage
from django.conf import settings
import os
from .models import Student

# Fonction pour récupérer les emails non lus
def fetch_emails(max_emails=10):
    """Récupère les emails non lus depuis la boîte de réception et limite à 'max_emails' emails"""
    try:
        # Connexion à la boîte IMAP
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        imap.select("inbox")

        # Chercher les emails non lus
        status, messages = imap.search(None, 'UNSEEN')
        if status != "OK":
            print("Erreur lors de la recherche des emails.")
            return []

        email_ids = messages[0].split()
        print(f"Emails non lus récupérés: {email_ids}")

        emails = []

        # Limiter le nombre d'emails à récupérer
        for idx, email_id in enumerate(email_ids):
            if idx >= max_emails:  # Vérifie si le nombre d'emails récupérés dépasse la limite
                break

            status, msg_data = imap.fetch(email_id, "(RFC822)")
            if status != "OK":
                print(f"Erreur lors de la récupération de l'email {email_id}")
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    # Décoder l'objet de l'email
                    subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode()

                    # Extraire le corps de l'email en fonction du type
                    if msg.is_multipart():
                        body = None
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            # Vérifier si cette partie est du texte
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                body = part.get_payload(decode=True)
                                if body:
                                    body = body.decode(errors='replace')  # Gérer les erreurs de décodage
                                break
                    else:
                        body = msg.get_payload(decode=True)
                        if body:
                            body = body.decode(errors='replace')  # Gérer les erreurs de décodage

                    # Ajouter l'email à la liste
                    emails.append({"subject": subject, "body": body})

        # Déconnexion du serveur IMAP
        imap.close()
        imap.logout()

        print(f"Emails récupérés: {emails}")
        return emails

    except Exception as e:
        print(f"Erreur lors de la récupération des emails: {e}")
        return []


# Fonction pour traiter une demande d'attestation
# Fonction pour traiter une demande d'attestation
def process_email(email_content):
    """Traite le contenu d'un email et génère l'attestation si les informations sont valides"""

    print(f"Traitement de l'email: {email_content['subject']}")

    # Vérifier si l'email est une demande d'attestation
    if "attestation" not in email_content["subject"].lower():
        print("Ce n'est pas une demande d'attestation.")
        return "Nous traitons uniquement les demandes d'attestation."

    # Extraire les informations de l'email (Nom, Prénom, CNE, CIN)
    body = email_content.get("body", "")
    if not body:
        print("Le corps de l'email est vide.")
        return "Le corps de l'email est vide."

    # Expression régulière pour extraire les informations
    info_pattern = r"Nom:\s*(?P<first_name>[^\n]+)\s*Prénom:\s*(?P<last_name>[^\n]+)\s*CNE:\s*(?P<cne>\d+)\s*CIN:\s*(?P<cin>[^\n]+)"
    match = re.search(info_pattern, body)

    if not match:
        print("Les informations sont incomplètes ou mal formatées.")
        return "Les informations fournies sont incomplètes ou mal formatées."

    # Nettoyer les données extraites
    data = {key: value.strip() for key, value in match.groupdict().items()}
    print(f"Informations extraites: {data}")

    # Vérifier si l'étudiant existe dans la base de données
    student, created = Student.objects.get_or_create(
        cne=data["cne"],
        cin=data["cin"],
        defaults={
            "first_name": data["first_name"],
            "last_name": data["last_name"]
        }
    )

    if created:
        print(f"Étudiant ajouté à la base de données : {student}")
    else:
        print(f"Étudiant trouvé : {student}")

    # Générer un PDF pour l'attestation
    pdf_file_path = os.path.join(settings.MEDIA_ROOT, f"{student.cne}_attestation.pdf")
    # Vérifier si le répertoire MEDIA_ROOT existe, sinon le créer
    os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)
    c = canvas.Canvas(pdf_file_path)

    # Ajouter le logo de l'université
    logo_path = os.path.join(settings.MEDIA_ROOT,"logo_university.png")  # Chemin vers le logo
    c.drawImage(logo_path, 50, 750, width=100, height=100)  # Positionner et redimensionner le logo

    # Titre de l'attestation
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "Attestation de scolarité")

    # Texte formel de l'attestation
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, "L'université CADI AYYAD")
    c.drawString(100, 680, f"certifie que l'étudiant(e) : {student.first_name} {student.last_name}")
    c.drawString(100, 660, f"CNE : {student.cne} - CIN : {student.cin}")
    c.drawString(100, 640, "poursuit ses études au sein de La Faculté des Sciences et Techniques de Gueliz.")

    # Date et signature (à personnaliser selon les besoins)
    c.drawString(100, 600, "Fait à FST GUELIZ, le 15 Décembre 2024")
    c.drawString(100, 580, "Signature du responsable:")

    # Ajouter une ligne pour la signature
    c.line(100, 570, 300, 570)

    # Sauvegarder le fichier PDF
    c.save()

    # Envoyer l'email avec l'attestation en pièce jointe
    email_message = EmailMessage(
        subject="Votre attestation de scolarité",
        body="Veuillez trouver ci-joint votre attestation de scolarité.",
        from_email=settings.EMAIL_HOST_USER,
        to=[settings.EMAIL_HOST_USER],  # Assurez-vous que l'étudiant a un email enregistré
    )
    email_message.attach_file(pdf_file_path)
    email_message.send()

    # Supprimer le fichier PDF après envoi
    os.remove(pdf_file_path)

    print("Attestation générée et envoyée avec succès.")
    return "Attestation générée et envoyée avec succès."

