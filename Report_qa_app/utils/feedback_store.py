import json
import os
from typing import List

FEEDBACK_DIR = os.path.join("feedback")
if not os.path.exists(FEEDBACK_DIR):
    os.makedirs(FEEDBACK_DIR, exist_ok=True)


def save_feedback(report_name: str, ignored_issue_ids: List[int]):
    path = os.path.join(FEEDBACK_DIR, f"{report_name}_feedback.json")
    payload = {"ignored": ignored_issue_ids}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return path


def load_feedback(report_name: str):
    path = os.path.join(FEEDBACK_DIR, f"{report_name}_feedback.json")
    if not os.path.exists(path):
        return {"ignored": []}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)
