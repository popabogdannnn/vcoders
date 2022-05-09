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
    test_list = load_tests(f"{path}/tests")
    os.system(f"mkdir {path}/aux")

    for tag in test_list:
        os.system(f"dos2unix {path}/tests/{tag}.in 2> /dev/null")
        os.system(f"dos2unix {path}/tests/{tag}.ok 2> /dev/null")
        os.system(f"cp {path}/tests/{tag}.in {path}/aux/")
        os.system(f"cp {path}/tests/{tag}.ok {path}/aux/")
    
    os.system(f"rm -rf {path}/tests")
    os.system(f"mv {path}/aux {path}/tests")

def check_subtask_array(array_as_string, path):
    with open(f"{path}/aux.json", "w") as f:
        f.write(array_as_string)
    ret = []
    test_list = load_tests(f"{path}/tests")
    #os.system(f"rm {path}/scoring.json 2> /dev/null")
    try:
        arr = load_json(f"{path}/aux.json")
        os.system(f"rm {path}/aux.json 2> /dev/null")
        if not isinstance(arr, list):
            raise NameError("Șirul nu descrie corect un array")
        if len(arr) != 2:
            raise NameError("Array-ul nu are lungime 2")
        
        subtask_distribution = arr[0]
        subtask_scores = arr[1]

        if(not isinstance(subtask_distribution, list)):
            raise NameError("Prima componentă nu este un array")

        if(not isinstance(subtask_scores, list)):
            raise NameError("A doua componentă nu este un array")

        if(len(test_list) != len(subtask_distribution)):
            raise NameError("Numărul de teste nu este egal cu lungimea distribuției pe subtask-uri")

        score = 0
        for x in subtask_scores:
            if not isinstance(x, int):
                raise NameError("Scorurile subtask-urilor nu sunt numere naturale")
            if x <= 0:
                raise NameError("Scorurile subtaskurilor sunt <= 0")
            score += x
        if score != 100: 
            raise NameError("Suma scorurilor subtask-urilor nu este egală cu 100p")
        for d in subtask_distribution:
            if not isinstance(d, list):
                raise NameError("Elementele din distribuția pe subtask-uri nu sunt array-uri")
            if(len(d) == 0):
                raise NameError("Există cel puțin un test neasociat cu niciun subtask")
            for x in d:
                if not isinstance(x, int) or x <= 0 or x > len(subtask_scores):
                    raise NameError("Subtask non-existent")

    except NameError as error:
        return error.__str__() 
    except json.decoder.JSONDecodeError:
        os.system(f"rm {path}/aux.json 2> /dev/null")
        return "Șirul nu descrie corect un array"
    ret = {
        "type": "subtask",
        "scoring": arr
    }
    with open(f"{path}/scoring.json", "w") as f:
        json.dump(ret, f, indent = 4)
    return ret

def check_score_per_test_array(array_as_string, path):
    with open(f"{path}/aux.json", "w") as f:
        f.write(array_as_string)
    ret = []
    test_list = load_tests(f"{path}/tests")
    #os.system(f"rm {path}/scoring.json 2> /dev/null")
    try:
        arr = load_json(f"{path}/aux.json")
        os.system(f"rm {path}/aux.json 2> /dev/null")
        if not isinstance(arr, list):
            raise NameError("Șirul nu descrie corect un array")
        if(len(arr) != len(test_list)):
            raise NameError("Lungimea array-ului de punctare al testelor și numărul de teste nu sunt egale")
        
        score = 0
        for x in arr:
            if not isinstance(x, int) or x <= 0:
                raise NameError("Un test este punctat cu <= 0")
            score += x
        if score != 100:
            raise NameError("Suma punctajelor pe teste nu face 100p")
        
    except NameError as error:
        return error.__str__() 
    except json.decoder.JSONDecodeError:
        os.system(f"rm {path}/aux.json 2> /dev/null")
        return "Șirul nu descrie corect un array"

    ret = {
        "type":"score_per_test",
        "scoring":arr
    }

    with open(f"{path}/scoring.json", "w") as f:
        json.dump(ret, f, indent = 4)
    return ret
