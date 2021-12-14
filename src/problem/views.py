from django.shortcuts import render
from django.http import HttpResponse
from pathlib import Path
# Create your views here.
from .auxiliary_functions import BASE_DIR, read_json
from .models import Problem

def problems_view(request):
    problem_list = [problem for problem in Problem.objects.all()]
    context = {
        "problem_list" : problem_list
    }
    return render(request, "problems.html", context)


def problem_view(request, problem_id):
    problem = Problem.objects.get(title_id=problem_id)
    context = {
        "problem" : problem
    }
    constraints = read_json(f"{BASE_DIR}/problems/{problem.title_id}/submission_data.json")
    statement = read_json(f"{BASE_DIR}/statements/{problem.title_id}.json")
    context["memory_constraints"] = f"{round(constraints['memory'] / 1000, 2)}MB/{round(constraints['stack_memory'] / 1000, 2)}MB"
    context["time_limit_constraint"] = f"{round(constraints['execution_time'] / 1000, 2)}s"
    if(constraints["stdio"]):
        context["io_files"] = "stdin/stdout"
    else:
        context["io_files"] = f"{constraints['io_filename']}.in/{constraints['io_filename']}.out"
    context["statement"] = statement
    return render(request, "problem.html", context)
    

def test(request, *args, **kwargs):
    return HttpResponse("TEST")