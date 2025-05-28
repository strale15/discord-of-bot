import gspread
import calendar
import datetime
from datetime import datetime
from google.oauth2.service_account import Credentials

import settings

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
key = Credentials.from_service_account_file("sheets/sheet-key.json", scopes=scopes)
client = gspread.authorize(key)

workbook = client.open_by_key(settings.SHEET_ID)
train_workbook = client.open_by_key(settings.TRAIN_FORM_SHEET_ID)

finesSheet = workbook.get_worksheet(0)
referralsSheet = workbook.get_worksheet(1)
trainFormSheet = train_workbook.get_worksheet(0)

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

def col_num_to_letter(col_num):
    """Convert column number (1-based) to letter (A, B, C, ...)"""
    letter = ""
    while col_num > 0:
        col_num, remainder = divmod(col_num - 1, 26)
        letter = chr(65 + remainder) + letter
    return letter

def cleanRowExceptColumnA(row_num):
    range_to_clear = f"B{row_num}:Z{row_num}"
    referralsSheet.batch_clear([range_to_clear])

def getFirstEmptyUsernameRow():
    column_values = referralsSheet.col_values(2)
    return len(column_values) + 1 if column_values else 2

def cleanReferralsSheet():
    last_row = referralsSheet.row_count
    last_col = referralsSheet.col_count

    start_col_letter = col_num_to_letter(2)
    end_col_letter = col_num_to_letter(last_col)
    clear_range = f"{start_col_letter}3:{end_col_letter}{last_row}"

    # Clear the range
    referralsSheet.batch_clear([clear_range])
    
def updateMonthAndClean():
    try:
        monthNumber = int(referralsSheet.cell(1, 2).value)
        if monthNumber > 12 or monthNumber < 1:
            return (-1, False)
    except:
        return (-1, False)
    
    currentMonth = datetime.now().month
    if currentMonth > monthNumber:
        cleanReferralsSheet()
        referralsSheet.update_cell(1, 2, currentMonth)
        return (currentMonth, True)
    
    return (currentMonth, False)

def getUserReferrals(username: str) -> str:
    noRefMsg = "_This user doesn't have any referrals._"
    invalidMonthMsg = "_Invalid month number, please check your sheets_"
    
    currentMonth, changeMade = updateMonthAndClean()
    if currentMonth == -1:
        return invalidMonthMsg
    elif changeMade:
        return noRefMsg[:-1] + f" Month has been updated to {calendar.month_name[currentMonth]} and referral data has been cleaned._"
    
    usernameCell = referralsSheet.find(username, in_column=2)
    if usernameCell == None:
        return noRefMsg
    
    referrals = referralsSheet.row_values(usernameCell.row)[2:]
    if len(referrals) == 0:
        return noRefMsg
    
    message = f"```Referrals for {username}:\n"
    for referral in referrals:
        message += f"{referral}, "
        
    message = message[:-2] + f"\nNumber of referrals for {calendar.month_name[currentMonth]} is {len(referrals)}" + "```"
    return message

def addReferral(employeeNick: str, referralNick: str) -> bool:
    res, _ = updateMonthAndClean()
    if res == -1:
        return False
    
    userRow = -1
    usernameCell = referralsSheet.find(employeeNick, in_column=2)
    if usernameCell == None:
        try:
            userRow = referralsSheet.find("", in_column=2).row
        except:
            userRow = len(referralsSheet.col_values(2)) + 1
        cleanRowExceptColumnA(userRow)
        referralsSheet.update_cell(userRow, 2, employeeNick)
    else:
        userRow = usernameCell.row
        
    if userRow == -1:
        return False
        
    firstEmptyRefCellCol = None
    last_column = referralsSheet.col_count
    numReferrals = len(referralsSheet.row_values(userRow)[2:])
    if numReferrals + 3 <= last_column:
        firstEmptyRefCellCol = numReferrals + 3
    
    if firstEmptyRefCellCol == None:
        return False
    
    referralsSheet.update_cell(userRow, firstEmptyRefCellCol, referralNick)
    return True

def is_form_filled(discord_nick: str):
    nick_values = trainFormSheet.col_values(3)
    for nick in nick_values:
        if nick.lower().lstrip('@') == discord_nick.lower().lstrip('@'):
            return True
    return False