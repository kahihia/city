from django.db import models

# Create your models here.

class Feedback(models.Model):
    TYPE_CHOICES = (
        ('contact', 'Feedback/Contact'),
        ('suggestion', 'Suggestion'),
    )

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='contact')
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    comments = models.TextField()
