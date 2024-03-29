from django.shortcuts import redirect, render
from .eval_submission import eval_submission, read_json
import problem
from multiprocessing import Process
import os
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .auxiliary_functions import read_json, BASE_DIR, score_submission
# Create your views here.
from .models import *
from problem.models import *
MAX_CODE_SIZE = 64 * 1024

extension_by_compiler = {
    "c++64" : ".cpp",
    "c++32" : ".cpp",
    "c64" : ".c",
    "c32" : ".c",
}

@csrf_exempt
@login_required(login_url = 'login')
def send_submission(request):
    if request.method == "POST" and request.user.is_authenticated:
        problem_id = request.POST.get("problem_id")
        problem = Problem.objects.get(id = problem_id)
        if(not problem.can_submit):
            redirect("home")
        compiler_type = request.POST.get("compiler_type")
        source_code = request.POST.get("source_code")

        if(len(source_code) <= MAX_CODE_SIZE and len(source_code) > 0):
            extension = extension_by_compiler[compiler_type]
            new_submission = Submission.objects.create(problem = problem, user = request.user, compiler_type=compiler_type)
            new_submission.save()
            
            submission_path = str(BASE_DIR) + "/source_code/" + str(new_submission.id) 
            os.mkdir(submission_path)
            with open(submission_path + "/main" + extension, "w") as f:
                f.write(source_code)
            evaluation_process = Process(target=eval_submission, args=(new_submission.id, extension, problem, compiler_type))
            evaluation_process.start()
        return redirect("problem", problem.title_id)
    return redirect("home")

def view_all_submissions(request):

    submission_list_query_set = Submission.objects.all()

    context = {
        "submission_list": submission_list_query_set
    }
    return render(request, "submissions.html", context)

def view_submission(request, submission_id):
    submission = Submission.objects.get(id=submission_id)
    submission_path = str(BASE_DIR) + "/source_code/" + str(submission_id)
    evaluation = None
    try:
        evaluation = score_submission(submission_id, submission.problem.title_id)
    except:
        pass
    
    context = {
        "submission" : submission
    }

   

    #print(submission_path)
    if evaluation != None:
        if("subtask_scores" in evaluation.keys()):
            context["subtask_problem"] = True
        else:
            context["subtask_problem"] = False
        context["compilation_warnings"] = evaluation["compilation_warnings"]
        context["compilation_error"] = evaluation["compilation_error"]
        #print(compilation_result["warnings"])
        #checker_compilation = evaluation["checker-compilation"]
        #evaluation.pop("checker-compilation")
        #!!! --- TO ADD CHECKER ---- !!!#


        context["test_runs"] = {
            
        }
        if context["compilation_error"] != "success":
            pass
        elif(context["subtask_problem"]):
            test_summary = evaluation["test_summary"]
            for i in range(len(test_summary)):
                eval_message = test_summary[i]["reason"]
                time_seconds = test_summary[i]["usage"]["user_time"]["secs"]
                time_nanos = test_summary[i]["usage"]["user_time"]["nanos"]
                time_nanos /= 1e9
                time_seconds += time_nanos
                time_seconds = round(time_seconds, 3)
                if(int(test_summary[i]["usage"]["memory"] / 1000) < 1000):
                    memory = f'{int(test_summary[i]["usage"]["memory"] / 1000)}KB'
                else:
                    memory = f'{round(test_summary[i]["usage"]["memory"] / 1e6, 2)}MB'
                context["test_runs"][str(i + 1)] = {
                    "eval_message" : eval_message,
                    "time_seconds" : time_seconds,
                    "memory" : memory,
                    "subtask": test_summary[i]["subtask"]
                }
            context["subtask_scores"] = evaluation["subtask_scores"]
        else:
            test_summary = evaluation["test_summary"]
            for i in range(len(test_summary)):
                points_awarded = float(test_summary[i]["score"])
                eval_message = test_summary[i]["reason"]
                time_seconds = test_summary[i]["usage"]["user_time"]["secs"]
                time_nanos = test_summary[i]["usage"]["user_time"]["nanos"]
                time_nanos /= 1e9
                time_seconds += time_nanos
                time_seconds = round(time_seconds, 3)
                if(int(test_summary[i]["usage"]["memory"] / 1000) < 1000):
                    memory = f'{int(test_summary[i]["usage"]["memory"] / 1000)}KB'
                else:
                    memory = f'{round(test_summary[i]["usage"]["memory"] / 1e6, 2)}MB'
                context["test_runs"][str(i + 1)] = {
                    "eval_message" : eval_message,
                    "time_seconds" : time_seconds,
                    "memory" : memory,
                    "points_awarded" : points_awarded,
                }
    context["user"] = submission.user
    context["problem"] = submission.problem
    context["can_see_code"] = False
    if request.user == submission.user or request.user.is_superuser:
        source_code = ""
        with open(f"{submission_path}/main{extension_by_compiler[submission.compiler_type]}") as f:
            source_code = f.read()
        context["source_code"] = source_code
        context["can_see_code"] = True

    return render(request, "submission_at_id.html", context)

def view_problem_submissions(request, problem_id):
    problem = Problem.objects.get(title_id = problem_id)
    username = request.GET.get("user_id")
    if(username):
        user = User.objects.get(username=username)
        submission_list_query_set = Submission.objects.filter(problem = problem, user = user)
    else:
        submission_list_query_set = Submission.objects.filter(problem = problem)
    context = {
        "submission_list": submission_list_query_set
    }
    return render(request, "submissions.html", context)