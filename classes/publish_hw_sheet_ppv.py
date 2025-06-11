import gspread
from google.oauth2.service_account import Credentials

import settings

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
key = Credentials.from_service_account_file("sheets/sheet-key.json", scopes=scopes)
client = gspread.authorize(key)

workbook = client.open_by_key(settings.TRAIN_HW_SHEET)

ppvSheet = workbook.get_worksheet(0)

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import List

from typing import List
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class HomeworkSubmission:
    date: str
    img_id: str
    discord_name: str
    completion_time: str
    response: str
    self_rate: str
    grade: str
    notes: str
    trainee_id: str

def fetch_rows_by_date(target_date: str) -> List[HomeworkSubmission]:
    matched_rows = []

    col_a = ppvSheet.col_values(1)

    for idx in range(1, len(col_a)):
        date_str = col_a[idx].strip()

        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

        if dt.date().isoformat() == target_date:
            row_data = ppvSheet.row_values(idx + 1)

            # Ensure row has at least 9 fields
            if len(row_data) < 9:
                continue

            if row_data[6] != "":  # Skip empty grade
                submission = HomeworkSubmission(
                    date=row_data[0],
                    img_id=row_data[1],
                    discord_name=row_data[2],
                    completion_time=row_data[3],
                    response=row_data[4],
                    self_rate=row_data[5],
                    grade=row_data[6],
                    notes=row_data[7],
                    trainee_id=row_data[8],
                )
                matched_rows.append(submission)

    return matched_rows

