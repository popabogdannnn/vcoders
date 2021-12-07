from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

from .models import Problem

def problems_view(request):
    problem_list = [problem for problem in Problem.objects.all()]
    context = {
        "problem_list" : problem_list
    }
    return render(request, "problems.html", context)


def problem_view(request, problem_id):
    
    problem = Problem.objects.get(id=problem_id)
    context = {
        "problem" : problem
    }

    return render(request, "problem.html", context)
    

def test(request, *args, **kwargs):
    return HttpResponse("TEST")