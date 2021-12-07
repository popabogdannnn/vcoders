from django.db import models

# Create your models here.
class Problem(models.Model):
    title = models.CharField(max_length=32)
    statement = models.TextField(null = True)

    def __str__(self):
        return f"#{self.id} {self.title}" 