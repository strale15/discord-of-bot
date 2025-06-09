import gspread
import calendar
import datetime
from datetime import datetime
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

workbook = client.open_by_key(settings.PPV_TRAIN_SHEET)

ppvSheet = workbook.get_worksheet(0)

def submit_hw_to_sheet(start_time, img_id, discord_display_name, completion_time_str, response):
    # Find the first empty row where the first column is empty
    sheet_data = ppvSheet.col_values(1)
    empty_row = len(sheet_data) + 1
    for i, cell in enumerate(sheet_data, start=1):
        if cell.strip() == "":
            empty_row = i
            break

    # Prepare row data
    drive_img_id = util.getCtxImgDriveId(img_id=img_id)
    sheet_img_embed = f"""=HYPERLINK("https://drive.google.com/uc?export=view&id={drive_img_id}", "🔍 {img_id}")"""
    
    row_data = [
        start_time,              # Column A
        sheet_img_embed,                  # Column B
        discord_display_name,    # Column C
        completion_time_str,     # Column D
        response                 # Column E
    ]

    ppvSheet.insert_row([""] * len(row_data), index=empty_row)

    ppvSheet.update_cell(empty_row, 1, start_time)
    ppvSheet.update_cell(empty_row, 2, sheet_img_embed)
    ppvSheet.update_cell(empty_row, 3, discord_display_name)
    ppvSheet.update_cell(empty_row, 4, completion_time_str)
    ppvSheet.update_cell(empty_row, 5, response)
    add_grade_dropdown_with_colors(ppvSheet, empty_row)
    
def add_grade_dropdown_with_colors(sheet, row_index):
    """
    Adds a dropdown to column F of the specified row with values S–F,
    applies conditional formatting based on the grade,
    and sets font size to 20 with centered alignment.
    """
    sheet_id = sheet._properties['sheetId']
    grade_options = ["S", "A", "B", "C", "D", "E", "F"]
    grade_colors = {
        "S": {"red": 0.6, "green": 0.4, "blue": 0.8},
        "A": {"red": 0.8, "green": 0.94, "blue": 0.8},
        "B": {"red": 0.8, "green": 0.87, "blue": 1.0},
        "C": {"red": 1.0, "green": 1.0, "blue": 0.6},
        "D": {"red": 1.0, "green": 0.8, "blue": 0.6},
        "E": {"red": 1.0, "green": 0.6, "blue": 0.6},
        "F": {"red": 0.8, "green": 0.2, "blue": 0.2},
    }

    requests = []

    # Add dropdown validation
    requests.append({
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": row_index - 1,
                "endRowIndex": row_index,
                "startColumnIndex": 5,
                "endColumnIndex": 6
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

    # Conditional formatting
    for grade, color in grade_colors.items():
        requests.append({
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": sheet_id,
                        "startRowIndex": row_index - 1,
                        "endRowIndex": row_index,
                        "startColumnIndex": 5,
                        "endColumnIndex": 6
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

    # Apply font size and alignment separately
    fmt = CellFormat(
        textFormat=TextFormat(fontSize=20),
        horizontalAlignment='CENTER',
        verticalAlignment='MIDDLE'
    )
    format_cell_range(sheet, f"F{row_index}", fmt)
    
    fmt = CellFormat(
        borders=Borders(
        top=Border(style='DASHED', color=Color(0.2, 0.2, 0.2)),
        bottom=Border(style='DASHED', color=Color(0.2, 0.2, 0.2)),
        left=Border(style='DASHED', color=Color(0.2, 0.2, 0.2)),
        right=Border(style='DASHED', color=Color(0.2, 0.2, 0.2)),
        )
    )
    format_cell_range(sheet, f"A{row_index}:G{row_index}", fmt)