import csv
import os
from datetime import datetime
from typing import List

CSV_HEADER = ["subject", "date", "content", "tags"]

class HomeworkItem:
    def __init__(self, subject, date, content, tags):
        self.subject = subject
        self.date = date
        self.content = content
        self.tags = tags

def get_today_csv_path() -> str:
    today = datetime.now()
    today_str = f"{today.year}-{today.month}-{today.day}"
    data_dir = os.path.join(os.path.dirname(__file__), "homework_datas")
    return os.path.join(data_dir, f"{today_str}.csv")

def read_homework_from_csv(filepath:str) -> List[HomeworkItem]:
    if not os.path.exists(filepath):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(CSV_HEADER)
        return []
    items = []
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("subject") or not row.get("content"):
                continue
            items.append(HomeworkItem(
                subject=row["subject"],
                date=row.get("date", ""),
                content=row["content"],
                tags=row.get("tags", "")
            ))
    return items

def write_homework_to_csv(filepath: str, items: List[HomeworkItem]):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for i in items:
            writer.writerow({
                "subject": i.subject,
                "date": i.date,
                "content": i.content,
                "tags": i.tags
            })
