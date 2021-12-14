from django.shortcuts import redirect, render

from problem.views import test
from .eval_submission import eval_submission, read_json
import problem
from multiprocessing import Process
from pathlib import Path
import os
# Create your views here.
from .models import *
from problem.models import *
MAX_CODE_SIZE = 20 * 1024

BASE_DIR = Path(__file__).resolve().parent.parent.parent

extension_by_compiler = {
    "c++64" : ".cpp",
    "c++32" : ".cpp",
    "c64" : ".c",
    "c32" : ".c",
}

def send_submission(request):
    if request.method == "POST" and request.user.is_authenticated:
        
        problem_id = request.POST.get("problem_id")
        problem = Problem.objects.get(id = problem_id)
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
        evaluation = read_json(f"{submission_path}/{submission_id}.json")
    except:
        pass
    
    context = {
        "submission" : submission
        
    }
    print(submission_path)
    if evaluation != None:
        evaluation.pop("submission_id")

        compilation_result = evaluation["compilation"]
        evaluation.pop("compilation")
        context["compilation_warnings"] = compilation_result["warnings"]
        context["compilation_error"] = compilation_result["error"]
        print(compilation_result["warnings"])
        checker_compilation = evaluation["checker-compilation"]
        evaluation.pop("checker-compilation")

        context["test_runs"] = {

        }
        for tag, test_run in evaluation.items():
            points_awarded = float(test_run["verdict"]["points_awarded"])
            eval_message = test_run["verdict"]["reason"]
            time_seconds = test_run["usage"]["user_time"]["secs"]
            time_nanos = test_run["usage"]["user_time"]["nanos"]
            time_nanos /= 1e9
            time_seconds += time_nanos
            time_seconds = round(time_seconds, 3)
            memory = f'{int(test_run["usage"]["memory"] / 1000)}kB'
            context["test_runs"][tag] = {
                "eval_message" : eval_message,
                "time_seconds" : time_seconds,
                "memory" : memory,
                "points_awarded" : points_awarded,
            }
    
    return render(request, "submission_at_id.html", context)

def view_problem_submissions(request):
    pass