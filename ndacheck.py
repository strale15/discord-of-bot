import fitz  # PyMuPDF
import cv2
from PIL import Image
import numpy as np
import os
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def edit_nda_date():
    # Define paths
    original_pdf = "nda/XIC_NDA_ORG.pdf"
    temp_pdf = "nda/XIC_NDA.pdf"

    current_date = datetime.now().strftime("%B %d, %Y")

    doc = fitz.open(original_pdf)  # the file with the text you want to change
    search_term = "{DATE_PLACEHOLDER}"
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
    if os.path.exists("nda/token.json"):
        creds = Credentials.from_authorized_user_file("nda/token.json", SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("nda/credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("nda/token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def upload_to_drive(file_path, folder_id=None):
    creds = authenticate()
    service = build("drive", "v3", credentials=creds)

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
    match = re.search(r"XIC_NDA[-_](.*)\.pdf$", os.path.basename(path))
    if match:
        name = match.group(1)
    else:
        return False, "No name provided with the PDF, please name your file XIC_NDA-Name_Surname.pdf"
        
    #Check for name
    try:
        doc = fitz.open(path)
    except:
        return False, "Internal error, please contact management."    
    
    first_page = doc[0]
    
    text = first_page.get_text()
    lines = text.strip().split('\n')

    if lines[-1].lower() != name.lower().replace('_', ' '):
        return False, "Name you wrote in the PDF does not match with the name in the filename or you didn't write the name at all."
        
    #Check for signature
    page = doc[-1]  # last page

    pix = page.get_pixmap(dpi=200)  # higher DPI for better detail
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    img_path = f"nda/{name}_last_page.png"
    img.save(img_path)

    image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    h, w = image.shape

    # Focus on bottom quarter of the page
    signature_zone = image[:int(0.25 * h), :]

    # Threshold to binary image
    _, binary = cv2.threshold(signature_zone, 200, 255, cv2.THRESH_BINARY_INV)

    # Count non-zero (inked) pixels
    ink_pixels = cv2.countNonZero(binary)
    
    try:
        os.remove(img_path)
    except Exception as e:
        print(f"Error deleting {img_path}")

    if ink_pixels > 2200:
        return True, "All good!"
    else:
        return False, "You didn't create a signature."