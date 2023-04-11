from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Problem(models.Model):
    title = models.CharField(max_length=64)
    title_id = models.CharField(max_length=64)
    accepted = models.BooleanField(default=False)
    can_submit = models.BooleanField(default=False)
    author = models.CharField(max_length=128, default="-")
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.title}" 

class Contest(models.Model):
    title = models.CharField(max_length=64) 
    date = models.DateField(blank=False, auto_now_add=False, auto_now=False)
    def __str__(self):
        return f"{self.title} {self.date.year}"

class SubContestLevel(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.title}"

class SubContest(models.Model):
    sub_contest_level = models.ForeignKey(SubContestLevel, on_delete=models.SET_NULL, null=True)
    problem_list = models.ManyToManyField(Problem)
    parent_contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    def __str__(self):
        return f"{str(self.parent_contest)} {str(self.sub_contest_level)}"



