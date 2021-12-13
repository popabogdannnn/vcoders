from django.shortcuts import redirect, render
from .eval_submission import eval_submission
import problem
from multiprocessing import Process
from pathlib import Path
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
            with open(str(BASE_DIR) + "/source_code/" + str(new_submission.id) + extension, "w") as f:
                f.write(source_code)
            evaluation_process = Process(target=eval_submission, args=(new_submission.id, extension, problem))
            evaluation_process.start()
        return redirect("problem", problem.title_id)
    return redirect("home")

def view_all_submissions(request):

    submission_list_query_set = Submission.objects.all()

    context = {
        "submission_list": submission_list_query_set
    }
    return render(request, "submissions.html", context)

def view_problem_submissions(request):
    pass