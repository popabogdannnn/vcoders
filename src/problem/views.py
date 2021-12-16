import json
from django.shortcuts import render
from django.http import HttpResponse
from pathlib import Path
# Create your views here.
from .auxiliary_functions import BASE_DIR, read_json
from .models import Problem
from .decorators import *
import re
from django.core.files.storage import FileSystemStorage
import os 
def problems_view(request):
    problem_list = [problem for problem in Problem.objects.filter(accepted=True)]
    context = {
        "problem_list" : problem_list
    }
    return render(request, "problems.html", context)


def problem_view(request, problem_id):
    problem = Problem.objects.get(title_id=problem_id)
    if (problem == None or not problem.accepted) and not request.user.is_superuser:
        return HttpResponse("Problema nu există")
    context = {
        "problem" : problem
    }
    constraints = read_json(f"{BASE_DIR}/problems/{problem.title_id}/submission_data.json")
    statement = read_json(f"{BASE_DIR}/statements/{problem.title_id}.json")
    context["memory_constraints"] = f"{round(constraints['memory'] / 1000, 2)}MB/{round(constraints['stack_memory'] / 1000, 2)}MB"
    context["time_limit_constraint"] = f"{round(constraints['execution_time'] / 1000, 2)}s"
    if(constraints["stdio"]):
        context["in_file"] = "stdin"
        context["out_file"] = "stdout"
    else:
        context["in_file"] = f"{constraints['io_filename']}.in"
        context["out_file"] = f"{constraints['io_filename']}.out"

    context["statement"] = statement
    return render(request, "problem.html", context)

@authorized_users(authorized_roles=["proponent"])
def add_problem_view(request):
    if request.method == "POST":
        title = request.POST.get("title")

        title = " ".join(title.split())
        title_id = "-".join(title.lower().split())
        if len(title) <= 64 and not Problem.objects.filter(title_id=title_id).exists():
            Problem.objects.create(title=title, title_id=title_id)
            if(not os.path.exists(f"{BASE_DIR}/problems/{title_id}")):
                os.mkdir(f"{BASE_DIR}/problems/{title_id}")
                os.system(f"cp -r {BASE_DIR}/problems/sumab/. {BASE_DIR}/problems/{title_id}/")
                restrictions = read_json(f"{BASE_DIR}/problems/{title_id}/submission_data.json")
                restrictions["io_filename"] = title_id
                with open(f"{BASE_DIR}/problems/{title_id}/submission_data.json") as f:
                    json.dump(restrictions, f)
            if(not os.path.exists(f"{BASE_DIR}/statements/{title_id}.json")):
                os.system(f"cp {BASE_DIR}/statements/sumab.json {BASE_DIR}/statements/{title_id}.json")
            return redirect("edit_problem", title_id)
    context = {

    }
    return render(request, "add_problem.html", context)


@authorized_users(authorized_roles=["proponent"])
def edit_problem_view(request, title_id):
    if request.method == "POST":
        if "tests" in request.FILES:
            tests = request.FILES['tests']
            if(tests.size <= 200000000 and os.path.splitext(tests.name)[1] == ".zip"):
                fs = FileSystemStorage(location=f"{BASE_DIR}/garbage_folder/{title_id}")
                fs.save(tests.name, tests)
                os.system(f'unzip {BASE_DIR}/garbage_folder/{title_id}/"{tests.name}" -d {BASE_DIR}/garbage_folder/{title_id} > /dev/null')
                if(os.path.exists(f"{BASE_DIR}/garbage_folder/{title_id}/tests")):
                    #print("DA")
                    os.system(f"rm -rf {BASE_DIR}/problems/{title_id}/tests")
                    os.system(f"cp -r {BASE_DIR}/garbage_folder/{title_id}/tests {BASE_DIR}/problems/{title_id}/tests")
                os.system(f"rm -rf {BASE_DIR}/garbage_folder/{title_id}")
        statement = read_json(f"{BASE_DIR}/statements/{title_id}.json")
        restrictions = read_json(f"{BASE_DIR}/problems/{title_id}/submission_data.json")
        
        checker         = request.POST.get("checker")
        stdio           = request.POST.get("stdio")
        execution_time  = request.POST.get("execution_time")
        memory          = request.POST.get("memory")
        stack_memory    = request.POST.get("stack_memory")
        p_statement     = request.POST.get("statement")
        input_data      = request.POST.get("input")
        output_data     = request.POST.get("output")
        examples        = request.POST.get("examples")
        hint            = request.POST.get("hint")

        if(checker == "on"):
            checker = True
        else:
            checker = False
        if(stdio == "on"):
            stdio = True
        else:
            stdio = False

        restrictions["checker"] = checker
        restrictions["stdio"] = stdio
        restrictions["execution_time"] = int(execution_time)
        restrictions["memory"] = int(memory)
        restrictions["stack_memory"] = int(stack_memory)
        
        p_statement = p_statement.split("\n")
        examples_dict = {

        }
        examples = examples.split("@-nou_exemplu-@")
        tag = 0
        for example in examples:
            if isinstance(example, str):
                if example.find("@-input-@"):
                    tag += 1
                    p_input = ""
                    p_output = ""
                    r = re.split("@-input-@|@-output-@", example)
                    if(len(r) == 3):
                        p_input = r[1].strip()
                        p_output = r[2].strip()
                        examples_dict[str(tag)] = {
                            "input" : p_input,
                            "output": p_output
                        }
        
        statement["input"] = input_data
        statement["output"] = output_data
        statement["hint"] = hint
        statement["examples"] = examples_dict
        
        with open(f"{BASE_DIR}/statements/{title_id}.json", "w") as f:
            json.dump(statement, f)
        with open(f"{BASE_DIR}/problems/{title_id}/submission_data.json", "w") as f:
            json.dump(restrictions, f)
        problem = Problem.objects.get(title_id = title_id)
        problem.accepted = False
        problem.save()

    problem = Problem.objects.get(title_id = title_id)
    statement = read_json(f"{BASE_DIR}/statements/{title_id}.json")
    restrictions = read_json(f"{BASE_DIR}/problems/{title_id}/submission_data.json")
    statement["statement"] = "\n".join(statement["statement"])

    context = {
        "problem": problem,
        "statement": statement,
        "restrictions": restrictions,
        "tests_seen": [],
    }
    
    if os.path.exists(f"{BASE_DIR}/problems/{title_id}/tests/tests.txt"):
        with open(f"{BASE_DIR}/problems/{title_id}/tests/tests.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.split()
                if(len(line) == 2):
                    if(os.path.exists(f"{BASE_DIR}/problems/{title_id}/tests/{line[0]}-{title_id}.in" and os.path.exists(f"{BASE_DIR}/problems/{title_id}/tests/{line[0]}-{title_id}.ok"))):
                        context["tests_seen"].append(line[0])
    return render(request, "edit_problem.html", context)