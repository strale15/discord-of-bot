import settings
import gspread
from google.oauth2.service_account import Credentials

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
key = Credentials.from_service_account_file("key.json", scopes=scopes)
client = gspread.authorize(key)

workbook = client.open_by_key(settings.SHEET_ID)

finesSheet = workbook.get_worksheet(0)

class FineRow:
    def __init__(self, username, reason, amount, date):
        self.username = username
        self.reason = reason
        self.amount = int(amount)
        self.date = date
    
    def discordFormat(self) -> str:
        amount = str(self.amount) + "$"
        return f"username={self.username:15} amount={amount:<5} date={self.date:11} reason={self.reason}"



def test():
    sheets = map(lambda x: x.title, workbook.worksheets())
    print(list(sheets))
    
def addFine(username, reason, amount: int, date) -> bool:
    empty_row = -1
    try:
        empty_row = finesSheet.find("", in_column=1).row
    except:
        empty_row = len(finesSheet.col_values(1)) + 1
        
    if empty_row != -1:
        finesSheet.update_cell(empty_row, 1, username)
        finesSheet.update_cell(empty_row, 2, reason)
        finesSheet.update_cell(empty_row, 3, amount)
        finesSheet.update_cell(empty_row, 4, date)
        return True
    
    return False
    
def getUserFines(username: str) -> str:
    rows = finesSheet.get_all_values()[1:]
    userFines = [FineRow(row[0], row[1], row[2], row[3]) for row in rows if row[0] == username]
    if len(userFines) == 0:
        return ""
    
    message = "```"
    fineSum = 0
    for fines in userFines:
        message += fines.discordFormat() + "\n"
        fineSum += fines.amount
        
    message += f"\n Fines sum: {fineSum}$```"
    return message