from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Problem(models.Model):
    title = models.CharField(max_length=64)
    title_id = models.CharField(max_length=64)
    accepted = models.BooleanField(default=False)
    author = models.CharField(max_length=128, default="-")
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"#{self.id} {self.title}" 