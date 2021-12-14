import json
from pathlib import Path

BASE_DIR = str(Path(__file__).resolve().parent.parent.parent)

def read_json(file_name):
    file_submission_data = open(file_name)
    return json.load(file_submission_data)