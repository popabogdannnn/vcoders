import time
import os
from .models import Submission
import json
from .auxiliary_functions import read_json, BASE_DIR, score_submission


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
    
    result = score_submission(submission_id, problem.title_id)

    curr_submission = Submission.objects.get(id = submission_id)
    curr_submission.verdict = str(result["verdict"])
    curr_submission.save()

    