import json
from pathlib import Path
import os
import glob
import copy

from django import test 

BASE_DIR = str(Path(__file__).resolve().parent.parent.parent)

def read_json(file_name):
    file_submission_data = open(file_name)
    return json.load(file_submission_data)

def load_tests(path):
    curr = os.getcwd()
    os.chdir(path)
    test_list = []
    for file in glob.glob("*.in"):
        test_tag = file.split(".")[0]
        if(os.path.exists(f"{test_tag}.ok")):
            test_list.append(test_tag)
    test_list.sort()
    os.chdir(curr)
    return test_list


def score_submission(submission_id, problem_id):
    submission_path = BASE_DIR + "/source_code/" + str(submission_id)
    
    PROBLEM_DIRECTORY =  f"{BASE_DIR}/problems/{problem_id}"
    evaluation = read_json(f"{submission_path}/{submission_id}.json")
    submission_data = read_json(f"{PROBLEM_DIRECTORY}/submission_data.json")
    scoring = read_json(f"{PROBLEM_DIRECTORY}/scoring.json")
    
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
        tests = load_tests(f"{BASE_DIR}/problems/{problem_id}/tests")
        verdict = 0
        if(scoring["type"] == "subtask"):
            subtasks = scoring["scoring"]
            subtask_scores = subtasks[1]
            subtask_max_scores = copy.copy(subtasks[1])
            subtask_distribution = subtasks[0]
            subtask_percent_awarded = [100] * len(subtask_scores)

            test_summary = []
            for i in range(len(tests)):
                for subtask in subtask_distribution[i]:
                    subtask_percent_awarded[subtask - 1] = min(subtask_percent_awarded[subtask - 1], evaluation[str(i)]["verdict"]["points_awarded"])
                test_summary.append({
                    "reason": evaluation[str(i)]["verdict"]["reason"],
                    "usage": evaluation[str(i)]["usage"],
                    "subtask": subtask_distribution[i]
                })
            
            for i in range(len(subtask_scores)):
                subtask_scores[i] *= subtask_percent_awarded[i] / 100
                verdict += subtask_scores[i]
                subtask_scores[i] = round(subtask_scores[i], 2)
            
            verdict = round(verdict, 2)

            return {
                "compilation_warnings": compilation_result["warnings"],
                "verdict" : verdict,
                "subtask_scores" : zip(subtask_scores, subtask_max_scores),
                "test_summary": test_summary
            }
        else:
            
            test_scores = scoring["scoring"]
            test_summary = []
            for i in range(len(test_scores)):
                verdict += test_scores[i] * evaluation[str(i)]["verdict"]["points_awarded"] / 100
                #print(1)
                test_summary.append({
                    "reason": evaluation[str(i)]["verdict"]["reason"],
                    "usage": evaluation[str(i)]["usage"],
                    "score": round(test_scores[i] * evaluation[str(i)]["verdict"]["points_awarded"] / 100, 2)
                })
            
            verdict = round(verdict, 2)
            
            return {
                "compilation_error": compilation_result["error"],
                "compilation_warnings": compilation_result["warnings"],
                "verdict": verdict,
                "test_summary": test_summary
            }
    else:
        if(compilation_result["error"] != "success"):
            verdict = compilation_result["error"]
        else:
            verdict = checker_compilation["error"]

    return {
        "compilation_error": checker_compilation["error"],
        "compilation_warnings": compilation_result["warnings"],
        "verdict": verdict
    }