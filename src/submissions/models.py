from django.contrib.auth.models import User

from django.db import models
from datetime import datetime 
from problem import models as ProblemModels
# Create your models here.

class Submission(models.Model):
    problem = models.ForeignKey(ProblemModels.Problem, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    verdict = models.CharField(max_length=10, default="-")
    date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"#{self.id}" 