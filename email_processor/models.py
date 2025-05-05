from django.db import models

class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    cne = models.CharField(max_length=10, unique=True)
    cin = models.CharField(max_length=10, unique=True)
    email = models.EmailField()  # Assurez-vous que ce champ est là

    def __str__(self):
        return f"{self.first_name} {self.last_name} - CNE: {self.cne} - Email: {self.email}"
