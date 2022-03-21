import json
from pathlib import Path
import os, glob

BASE_DIR = str(Path(__file__).resolve().parent.parent.parent)

def read_json(file_name):
    file_submission_data = open(file_name)
    return json.load(file_submission_data)
def load_json(file_name):
    with open(file_name, "r") as f:
        return json.load(f)

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
    
def save_tests_seen(path):
    test_list = load_tests(path)
    os.system("mkdir aux")

    for tag in test_list:
        os.system(f"cp tests/{tag}.in aux/")
        os.system(f"cp tests/{tag}.ok aux/")
    
    os.system("rm -rf tests")
    os.system(f"mv aux tests")

def check_subtask_array(array_as_string):
    with open("aux.json", "w") as f:
        f.write(array_as_string)
    ret = []
    test_list = load_tests()
    os.system("rm scoring.json 2> /dev/null")
    try:
        arr = load_json("aux.json")
        os.system("rm aux.json 2> /dev/null")
        if not isinstance(arr, list):
            raise NameError("Not an array")
        if len(arr) != 2:
            raise NameError("Array length not 2")
        
        subtask_distribution = arr[0]
        subtask_scores = arr[1]

        if(not isinstance(subtask_distribution, list)):
            raise NameError("First component not an array")

        if(not isinstance(subtask_scores, list)):
            raise NameError("Second component not an array")

        if(len(test_list) != len(subtask_distribution)):
            raise NameError("Number of tests does not match with length of subtask distribution")

        score = 0
        for x in subtask_scores:
            if not isinstance(x, int):
                raise NameError("Subtask scores not integers")
            if x <= 0:
                raise NameError("Subtask scores are <= 0")
            score += x
        if score != 100: 
            raise NameError("Subtask scores do not add up to 100p")
        for d in subtask_distribution:
            if not isinstance(d, list):
                raise NameError("Elements from subtask distribution are not arrays")
            if(len(d) == 0):
                raise NameError("Test not associated with any subtask")
            for x in d:
                if not isinstance(x, int) or x <= 0 or x > len(subtask_scores):
                    raise NameError("Subtask non-existent")

    except NameError as error:
        return error.__str__() 
    except json.decoder.JSONDecodeError:
        os.system("rm aux.json 2> /dev/null")
        return "String does not correctly describe an array"
    ret = {
        "type": "subtask",
        "scoring": arr
    }
    with open("scoring.json", "w") as f:
        json.dump(ret, f, indent = 4)
    return True

def check_score_per_test_array(array_as_string):
    with open("aux.json", "w") as f:
        f.write(array_as_string)
    ret = []
    test_list = load_tests()
    os.system("rm subtasks.json 2> /dev/null")
    try:
        arr = load_json("aux.json")
        os.system("rm aux.json 2> /dev/null")
        if not isinstance(arr, list):
            raise NameError("Not an array")
        if(len(arr) != len(test_list)):
            raise NameError("Test scoring array not the same length as number of tests")
        
        score = 0
        for x in arr:
            if not isinstance(x, int) or x <= 0:
                raise NameError("Test is scored with <= 0")
            score += x
        if score != 100:
            raise NameError("Test scores do not add up to 100p")
        
    except NameError as error:
        return error.__str__() 
    except json.decoder.JSONDecodeError:
        os.system("rm aux.json 2> /dev/null")
        return "String does not correctly describe an array"

    ret = {
        "type":"score_per_test",
        "scoring":arr
    }

    with open("scoring.json", "w") as f:
        json.dump(ret, f, indent = 4)
    return True
