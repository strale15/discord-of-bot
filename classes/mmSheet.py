import gspread
from google.oauth2.service_account import Credentials
from gspread_formatting import (
    CellFormat,
    Color,
    TextFormat,
    Borders,
    Border,
    format_cell_range
)

import settings
import util

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
key = Credentials.from_service_account_file("sheets/sheet-key.json", scopes=scopes)
client = gspread.authorize(key)

workbook = client.open_by_key(settings.TRAIN_HW_SHEET)

mmSheet = workbook.get_worksheet(1)

def submit_hw_to_sheet(date: str, discord_display_name: str, trainee_id, mms: list[str]):
    sheet_data = mmSheet.col_values(1)
    empty_row = len(sheet_data) + 1
    for i, cell in enumerate(sheet_data, start=1):
        if cell.strip() == "":
            empty_row = i
            break
    
    row_data = [
        date,
        discord_display_name,
        mms[0],
        mms[1],
        mms[2],
        mms[3],
        mms[4],
    ]

    mmSheet.insert_row(row_data, index=empty_row)
    mmSheet.update_cell(empty_row, 10, str(trainee_id))
    add_grade_dropdown_with_colors(mmSheet, empty_row)
    
def add_grade_dropdown_with_colors(sheet, row_index):
    sheet_id = sheet._properties['sheetId']
    grade_options = [str(i) for i in range(1, 11)]
    
    # Example: Use a gradient from green (high) to red (low)
    grade_colors = {
        "10": {"red": 0.6, "green": 0.9, "blue": 0.6},
        "9": {"red": 0.7, "green": 0.95, "blue": 0.7},
        "8": {"red": 0.8, "green": 1.0, "blue": 0.8},
        "7": {"red": 1.0, "green": 1.0, "blue": 0.6},
        "6": {"red": 1.0, "green": 0.9, "blue": 0.6},
        "5": {"red": 1.0, "green": 0.8, "blue": 0.5},
        "4": {"red": 1.0, "green": 0.7, "blue": 0.4},
        "3": {"red": 1.0, "green": 0.5, "blue": 0.3},
        "2": {"red": 1.0, "green": 0.3, "blue": 0.2},
        "1": {"red": 0.9, "green": 0.2, "blue": 0.2},
    }

    requests = []

    # Add dropdown validation
    requests.append({
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": row_index - 1,
                "endRowIndex": row_index,
                "startColumnIndex": 7,
                "endColumnIndex": 8
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": grade} for grade in grade_options]
                },
                "showCustomUi": True,
                "strict": True
            }
        }
    })

    # Conditional formatting for each grade
    for grade, color in grade_colors.items():
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet_id,
                        "startRowIndex": row_index - 1,
                        "endRowIndex": row_index,
                        "startColumnIndex": 7,
                        "endColumnIndex": 8
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "TEXT_EQ",
                            "values": [{"userEnteredValue": grade}]
                        },
                        "format": {
                            "backgroundColor": color
                        }
                    }
                },
                "index": 0
            }
        })

    # Apply dropdown and conditional format
    sheet.spreadsheet.batch_update({"requests": requests})

    # Apply font size and alignment
    fmt = CellFormat(
        textFormat=TextFormat(fontSize=20),
        horizontalAlignment='CENTER',
        verticalAlignment='MIDDLE'
    )
    format_cell_range(sheet, f"H{row_index}", fmt)
    
    fmt = CellFormat(verticalAlignment='TOP')
    format_cell_range(sheet, f"C{row_index}:G{row_index}", fmt)
    
    # Add dashed border to the whole row (A-G)
    fmt = CellFormat(
        borders=Borders(
            top=Border(style='DASHED', color=Color(0.2, 0.2, 0.2)),
            bottom=Border(style='DASHED', color=Color(0.2, 0.2, 0.2)),
            left=Border(style='DASHED', color=Color(0.2, 0.2, 0.2)),
            right=Border(style='DASHED', color=Color(0.2, 0.2, 0.2)),
        )
    )
    format_cell_range(sheet, f"A{row_index}:I{row_index}", fmt)