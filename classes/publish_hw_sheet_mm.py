import gspread
from google.oauth2.service_account import Credentials

import settings

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
key = Credentials.from_service_account_file("sheets/sheet-key.json", scopes=scopes)
client = gspread.authorize(key)

workbook = client.open_by_key(settings.TRAIN_HW_SHEET)

mmSheet = workbook.get_worksheet(1)

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import List

from typing import List
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class MMHomeworkSubmission:
    date: str
    discord_name: str
    mm1: str
    mm2: str
    mm3: str
    mm4: str
    mm5: str
    grade: str
    notes: str
    trainee_id: str

def fetch_rows_by_date(target_date: str) -> List[MMHomeworkSubmission]:
    matched_rows = []

    col_a = mmSheet.col_values(1)

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
            row_data = mmSheet.row_values(idx + 1)

            # Ensure row has at least 9 fields
            if len(row_data) < 10:
                continue

            if row_data[7] != "":  # Skip empty grade
                submission = MMHomeworkSubmission(
                    date=row_data[0],
                    discord_name=row_data[1],
                    mm1=row_data[2],
                    mm2=row_data[3],
                    mm3=row_data[4],
                    mm4=row_data[5],
                    mm5=row_data[6],
                    grade=row_data[7],
                    notes=row_data[8],
                    trainee_id=row_data[9],
                )
                matched_rows.append(submission)

    return matched_rows

