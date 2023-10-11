from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import io
from googleapiclient.http import MediaIoBaseDownload
import shutil
from pdfrw import PdfReader, PdfWriter


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata']

def main():
    """get the file in terms of docx...
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    print(os.listdir())
    drive = build('drive', 'v3', credentials=creds)
    request = drive.files().export_media(fileId='1aKf0ffoL7XjR26npjBmNcKClULSlGDIrlQx_E8dNXxI',  mimeType='application/pdf')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    fh.seek(0)
    with open('PDFs/CV_mcdanal.pdf', 'wb') as f: # it's only been loaded into RAM!
        shutil.copyfileobj(fh, f, length=131072)

    trailer = PdfReader("PDFs/CV_mcdanal.pdf")
    trailer.Info.Title = """Riley McDanal's CV"""
    trailer.Info.Author = 'Riley McDanal'
    trailer.Info.Subject = 'PhD Candidate in Clinical Science at Stony Brook University'
    PdfWriter(outfn, trailer=trailer).write()
    
if __name__ == '__main__':
    main()
