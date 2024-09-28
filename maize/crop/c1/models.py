from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Prediction(models.Model):
    created_at = models.DateTimeField(default=datetime.now)
    disease = models.CharField(max_length=100)
    image = models.ImageField(upload_to='predictions/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link predictions to a user

    def _str_(self):
        return f"{self.created_at} - {self.disease}"