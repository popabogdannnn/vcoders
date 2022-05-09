from datetime import datetime
from gettext import NullTranslations
import json
from multiprocessing import parent_process
from django.shortcuts import render
from django.http import HttpResponse
from pathlib import Path
# Create your views here.
from .auxiliary_functions import BASE_DIR, check_score_per_test_array, check_subtask_array, load_tests, read_json, save_tests_seen
from .models import Problem, Contest, SubContest, SubContestLevel
from .decorators import *
import re
from django.core.files.storage import FileSystemStorage
import os 

def problems_view(request):
    problem_list = Problem.objects.all()
    context = {
        "title": "Probleme",
        "problem_list" : problem_list
    }
    return render(request, "problems.html", context)


def problem_view(request, problem_id):
    problem = Problem.objects.get(title_id=problem_id)
    
    if (problem == None):
        return HttpResponse("Problema nu există")
    
    if (not problem.accepted and not (request.user.is_superuser or request.user == problem.posted_by)):
        return HttpResponse("Problema nu există")
    context = {
        "problem" : problem
    }

    if request.user.is_superuser or request.user == problem.posted_by:
        context["user_can_edit"] = True
    else:
        context["user_can_edit"] = False
    
    constraints = read_json(f"{BASE_DIR}/problems/{problem.title_id}/submission_data.json")
    statement = read_json(f"{BASE_DIR}/problems/{problem.title_id}/{problem.title_id}.json")
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
        title               = request.POST.get("title")
        in_contest          = request.POST.get("in_contest")
        contest             = request.POST.get("contest")
        sub_contest_level   = request.POST.get("sub_contest_level")
        if(len(title) > 0):
            title = " ".join(title.split())
            title_id = "_".join(title.lower().split())

            if len(title) <= 64 and not Problem.objects.filter(title_id=title_id).exists():
                Problem.objects.create(title=title, title_id=title_id, posted_by=request.user)
                if(in_contest):
                    contest = Contest.objects.get(id=contest)
                    sub_contest_level = SubContestLevel.objects.get(id=sub_contest_level)
                    if(not SubContest.objects.filter(parent_contest = contest, sub_contest_level = sub_contest_level).exists()):
                        SubContest.objects.create(parent_contest = contest, sub_contest_level = sub_contest_level)
                    sub_contest = SubContest.objects.get(parent_contest = contest, sub_contest_level = sub_contest_level)
                    sub_contest.problem_list.add(Problem.objects.get(title_id=title_id))
                    sub_contest.save()
                if(not os.path.exists(f"{BASE_DIR}/problems/{title_id}")):
                    #print("SALUTARE LUME")
                    os.mkdir(f"{BASE_DIR}/problems/{title_id}")
                    os.system(f"cp -r {BASE_DIR}/problems/sumab/. {BASE_DIR}/problems/{title_id}/")
                
                    restrictions = read_json(f"{BASE_DIR}/problems/{title_id}/submission_data.json")
                    restrictions["io_filename"] = title_id
                    with open(f"{BASE_DIR}/problems/{title_id}/submission_data.json", "w") as f:
                        json.dump(restrictions, f)
                    os.system(f"mv {BASE_DIR}/problems/{title_id}/sumab.json {BASE_DIR}/problems/{title_id}/{title_id}.json")
                    
                return redirect("edit_problem", title_id)
    context = {
        "contests": Contest.objects.all(),
        "sub_contest_levels": SubContestLevel.objects.all(),
    }
    return render(request, "add_problem.html", context)


@authorized_users(authorized_roles=["proponent"])
def edit_problem_view(request, title_id):
    problem = Problem.objects.get(title_id = title_id)
    if(problem.posted_by != request.user and not request.user.is_superuser):
        return HttpResponse("Nu ai acces la această resursă")
    scoring = None
    errors = []
    if request.method == "POST":
        if "tests" in request.FILES:
            tests = request.FILES['tests']
            if(tests.size <= 500000000 and os.path.splitext(tests.name)[1] == ".zip"):
                fs = FileSystemStorage(location=f"{BASE_DIR}/garbage_folder/{title_id}")
                fs.save(tests.name, tests)
                os.system(f'unzip {BASE_DIR}/garbage_folder/{title_id}/"{tests.name}" -d {BASE_DIR}/garbage_folder/{title_id} > /dev/null')
                if(os.path.exists(f"{BASE_DIR}/garbage_folder/{title_id}/tests")):
                    #print("DA")
                    os.system(f"rm -rf {BASE_DIR}/problems/{title_id}/tests")
                    os.system(f"cp -r {BASE_DIR}/garbage_folder/{title_id}/tests {BASE_DIR}/problems/{title_id}/tests")
                os.system(f"rm -rf {BASE_DIR}/garbage_folder/{title_id}")
                save_tests_seen(f"{BASE_DIR}/problems/{title_id}")
        statement = read_json(f"{BASE_DIR}/problems/{title_id}/{title_id}.json")
        restrictions = read_json(f"{BASE_DIR}/problems/{title_id}/submission_data.json")
        
        checker         = request.POST.get("checker")
        io_filename     = request.POST.get("io_filename")
        execution_time  = request.POST.get("execution_time")
        memory          = request.POST.get("memory")
        stack_memory    = request.POST.get("stack_memory")
        p_statement     = request.POST.get("statement")
        input_data      = request.POST.get("input")
        output_data     = request.POST.get("output")
        remarks         = request.POST.get("remarks")
        examples        = request.POST.get("examples")
        hint            = request.POST.get("hint")
        scoring_array   = request.POST.get("scoring")
        scoring_type    = request.POST.get("type")
        
        if(scoring_type == "score_per_test"):
            verdict = check_score_per_test_array(scoring_array, f"{BASE_DIR}/problems/{title_id}")
            if(not isinstance(verdict, dict)):
                errors.append(verdict)
                scoring = {
                    "type": scoring_type,
                    "scoring": scoring_array
                }
            else:
                scoring = verdict
                problem.can_submit = True
        elif(scoring_type == "subtask"):
            verdict = check_subtask_array(scoring_array, f"{BASE_DIR}/problems/{title_id}")
            if(not isinstance(verdict, dict)):
                errors.append(verdict)
                scoring = {
                    "type": scoring_type,
                    "scoring": scoring_array
                }
            else:
                scoring = verdict
                problem.can_submit = True

        if(checker == "on"):
            checker = True
        else:
            checker = False
        if(io_filename == ""):
            stdio = True
            io_filename = title_id
        else:
            stdio = False

        restrictions["checker"] = checker
        restrictions["stdio"] = stdio
        restrictions["io_filename"] = io_filename
        restrictions["execution_time"] = max(int(execution_time), 50)
        restrictions["memory"] = int(memory)
        restrictions["stack_memory"] = int(stack_memory)
        
        p_statement = p_statement.split("\n")
        remarks = remarks.split("\n")

        examples_dict = {

        }
        examples = examples.split("@-nou_exemplu-@")
        tag = 0
        for example in examples:
            if isinstance(example, str):
                if example.find("@-input-@"):
                    p_input = ""
                    p_output = ""
                    r = re.split("@-input-@|@-output-@", example)
                    if(len(r) == 3):
                        tag += 1
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
        statement["statement"] = p_statement
        statement["remarks"] = remarks
        
        with open(f"{BASE_DIR}/problems/{title_id}/{title_id}.json", "w") as f:
            json.dump(statement, f, indent=4)
        with open(f"{BASE_DIR}/problems/{title_id}/submission_data.json", "w") as f:
            json.dump(restrictions, f)
        
        problem.accepted = False
        problem.save()
    #problem = Problem.objects.get(title_id = title_id)
    statement = read_json(f"{BASE_DIR}/problems/{title_id}/{title_id}.json")
    restrictions = read_json(f"{BASE_DIR}/problems/{title_id}/submission_data.json")
    
    if(scoring == None):
        scoring = read_json(f"{BASE_DIR}/problems/{title_id}/scoring.json")
        
    if(scoring["type"] == "score_per_test"):
        verdict = check_score_per_test_array(str(scoring["scoring"]), f"{BASE_DIR}/problems/{title_id}")
        if(not isinstance(verdict, dict)):
            errors.append(verdict)
            problem.can_submit = False
            problem.save()
    elif(scoring["type"] == "subtask"):
        verdict = check_subtask_array(str(scoring["scoring"]), f"{BASE_DIR}/problems/{title_id}")
        
        if(not isinstance(verdict, dict)):
            errors.append(verdict)
            problem.can_submit = False
            problem.save()
    
    statement["statement"] = "\n".join(statement["statement"])
    statement["remarks"] = "\n".join(statement["remarks"])
    
    if(restrictions["stdio"]):
        restrictions["io_filename"] = ""
    context = {
        "problem": problem,
        "statement": statement,
        "restrictions": restrictions,
        "tests_seen": [],
        "scoring": scoring,
        "errors": errors,
    }
    
    context["tests_seen"] = load_tests(f"{BASE_DIR}/problems/{title_id}/tests")
    
    return render(request, "edit_problem.html", context)

def contests_view(request):
    contests = Contest.objects.all().order_by("-date")
    contest_dict = {

    }
    
    for x in contests:
        contest_dict[x.date.year] = []
    for x in contests:
        contest_dict[x.date.year].append({
            "obj": x,
            "sub_contests": SubContest.objects.filter(parent_contest=x)
        })
    
    context = {
        "contest_dict": contest_dict
    }
    return render(request, "contest_archive.html", context)

def sub_contest_view(request, sub_contest_id):
    sub_contest = SubContest.objects.get(id=sub_contest_id)
    context = {
        "title": sub_contest,
        "problem_list": sub_contest.problem_list.filter()
    }
    return render(request, "problems.html", context)



