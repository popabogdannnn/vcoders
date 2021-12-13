from django.shortcuts import render

import problem

# Create your views here.
from .models import *


def view_all_submissions(request):

    submission_list_query_set = Submission.objects.all()

    context = {
        "submission_list": submission_list_query_set
    }
    return render(request, "submissions.html", context)

def view_problem_submissions(request):
    pass