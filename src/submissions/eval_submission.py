import time
import os
from .models import Submission
from pathlib import Path
import json
BASE_DIR = str(Path(__file__).resolve().parent.parent.parent)

def read_json(file_name):
    file_submission_data = open(file_name)
    return json.load(file_submission_data)

def eval_submission(submission_id, extension, problem, compiler_type):
    submission_path = BASE_DIR + "/source_code/" + str(submission_id) 
    submissions_app_path = BASE_DIR + "/src/submissions/server_to_mid"
    problems_path = BASE_DIR + "/problems/" + problem.title_id
    garbage_folder_path = BASE_DIR + "/garbage_folder/" + str(submission_id)
    
    os.mkdir(garbage_folder_path)
    os.system(f"cp -r {problems_path} {garbage_folder_path}/submission")
    os.system(f"cp {submission_path}/main{extension} {garbage_folder_path}/submission")
    os.chdir(garbage_folder_path + "/submission")

    submission_data = read_json("submission_data.json")
    submission_data["compiler_type"] = compiler_type
    submission_data["submission_id"] = str(submission_id)

    with open("submission_data.json", "w") as f:
        json.dump(submission_data, f)
    
    os.chdir("../")
    os.system(f"zip -r {submission_id}.zip submission > /dev/null")
    os.system(f"cp {submission_id}.zip {submissions_app_path}")
    os.chdir("../")
    os.system(f"rm -rf {submission_id}")
    os.chdir(submissions_app_path)

    os.system(f"python3 server.py {submission_id}.zip")

    os.system(f"cp {submission_id}.json {submission_path}")

    os.system(f"rm {submission_id}.json")
    os.system(f"rm {submission_id}.zip")
    os.chdir(submission_path)

    evaluation = read_json(f"{submission_id}.json")

    evaluation.pop("submission_id")
    compilation_result = evaluation["compilation"]
    evaluation.pop("compilation")
    checker_compilation = evaluation["checker-compilation"]
    evaluation.pop("checker-compilation")

    ok = True
    if(compilation_result["error"] != "success"):
        ok = False
    if(submission_data["checker"] == True):
        if(checker_compilation["error"] != "success"):
            ok = False

    if(ok):
        verdict = 0.0
        for tag, test_run in evaluation.items():
            verdict += test_run["verdict"]["points_awarded"]
        verdict = round(verdict, 2)
    else:
        if(compilation_result["error"] != "success"):
            verdict = compilation_result["error"]
        else:
            verdict = checker_compilation["error"]

    curr_submission = Submission.objects.get(id = submission_id)
    curr_submission.verdict = str(verdict)
    curr_submission.save()

    