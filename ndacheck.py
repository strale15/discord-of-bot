import fitz  # PyMuPDF
import cv2
from PIL import Image
import numpy as np
import os
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime
import signatureScan

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def edit_nda_date():
    # Define paths
    original_pdf = "nda/XIC_NDA_ORG.pdf"
    temp_pdf = "nda/XIC_NDA.pdf"

    current_date = datetime.now().strftime("%B %d, %Y")

    doc = fitz.open(original_pdf)  # the file with the text you want to change
    search_term = "{dateplaceholder1}"
    found = doc[0].search_for(search_term)  # list of rectangles where to replace
    for item in found:
        doc[0].add_redact_annot(item, '')  # create redaction for text
        doc[0].apply_redactions()  # apply the redaction now
        doc[0].insert_text(item.bl - (0, 3), current_date)

    doc.save(temp_pdf)
    doc.close()
    return temp_pdf


def authenticate():
    creds = None
    # Use the service account key file (drive-key.json) to authenticate
    try:
        creds = service_account.Credentials.from_service_account_file(
            "nda/drive-key.json",  # Path to your service account key
            scopes=SCOPES  # Required scopes for Drive API
        )
    except Exception as e:
        print(f"Error loading service account: {e}")
        return None
    return creds

def upload_to_drive(file_path, folder_id=None):
    creds = authenticate()
    if not creds:
        print("Authentication failed!")
        return
    service = build("drive", "v3", credentials=creds, cache_discovery=False)

    file_name = os.path.basename(file_path)
    media = MediaFileUpload(file_path)

    file_metadata = {"name": file_name}
    if folder_id:  # Only add parents if folder_id is provided
        file_metadata["parents"] = [folder_id]  # Must be a list

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    print(f"Uploaded to folder! File ID: {file.get('id')}")

def checkNda(path="nda/XIC_NDA.pdf"):
    path = path.lstrip("./")

    # Extract the name between 'NDA_' and '.pdf'
    #Check filename for name
    name = ""
    match = re.search(r"XIC_NDA[-_](.*)\.pdf$", os.path.basename(path))
    if match:
        name = match.group(1)
        
    if len(name) < 4:
        msg = """Your NDA file needs to follow the format: XIC_NDA-Name_Surname.pdf
For example: XIC_NDA-John_Doe.pdf
Please rename your file and submit it to me once again.
        """
        return False, msg, ""
        
    #Check for name
    try:
        doc = fitz.open(path)
    except:
        return False, "Internal error while processing pdf, please contact management.", ""    
    
    first_page = doc[0]
    
    text = first_page.get_text()
    lines = text.strip().split('\n')

    if lines[-1].lower() != name.lower().replace('_', ' '):
        msg = """The name on your PDF does not match up with the name on your NDA file, or you did not write your name on your PDF at all.
Please apply said changes and submit it to me once again.
        """
        return False, msg, ""
        
    #Check for signature
    if signatureScan.is_there_signature(pdf_path=path, img_path=f"signature_{name}.png"):
        return True, "All good!", name.replace('_', ' ')
    else:
        msg = """Please provide your signature next to "EMPLOYEE: By: " instead of typing your name. The typed name should only appear in the Employee Name section."""
        return False, msg, ""