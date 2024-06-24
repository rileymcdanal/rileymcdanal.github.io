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
import numpy as np
import sys


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata']



                    
def replace_text(service, document_id, old_text, new_text):
    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=document_id).execute()
    content = document.get('body').get('content')

    requests = []
    for element in content:
        if 'paragraph' in element:
            for paragraph_element in element.get('paragraph').get('elements'):
                text_run = paragraph_element.get('textRun')
                if text_run and old_text in text_run.get('content'):
                    requests.append({
                        'replaceAllText': {
                            'containsText': {
                                'text': old_text,
                                'matchCase': 'true'
                            },
                            'replaceText': new_text
                        }
                    })

    result = service.documents().batchUpdate(
        documentId=document_id, body={'requests': requests}).execute()
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




    # try it new style


    file_id = '1aKf0ffoL7XjR26npjBmNcKClULSlGDIrlQx_E8dNXxI'
    n_citations = np.loadtxt('data/n_citations.txt')
    h_index = np.loadtxt('data/h_index.txt')
    n_first_author_citations = np.loadtxt('data/n_first_author_citations.txt')
    first_author_h_index = np.loadtxt('data/first_author_h_index.txt')

    # get today's date, format in month.day.year
    today = datetime.datetime.today()
    today = today.strftime("%m.%d.%Y")

    # replace data in docs

    new_texts = [f'As of {today}', f'Citations: {int(n_citations)}', f'H-index: {int(h_index)}', f'First author citations: {int(n_first_author_citations)}', f'First author H-index: {int(first_author_h_index)}']
    old_texts = ['As of 6.24.24', 'Citations: NCITATIONS', 'H-index: HINDEX', 'First author citations: N_FIRST_AUTHOR_CITATIONS', 'First author H-index: FIRST_AUTHOR_HINDEX']
    pdb.set_trace()
    drive = build('docs', 'v1', credentials=creds)

    try:
        for old_text, new_text in zip(old_texts, new_texts):
            replace_text(drive, file_id, old_text, new_text)
    except googleapiclient.errors.HttpError as err:
        print(err)
        print("maybe the filler text is not in the doc?")
        sys.exit()


    drive = build('drive', 'v3', credentials=creds)
    request = drive.files().export_media(fileId=file_id,  mimeType='application/pdf')
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
    PdfWriter("PDFs/CV_mcdanal.pdf", trailer=trailer).write()

    # lastly, put the google doc back the way it was
    for old_text, new_text in zip(old_texts, new_texts):
        replace_text(drive, file_id, new_text, old_text)

    # replace_number_in_pdf('PDFs/CV_mcdanal.pdf', 'PDFs/CV_mcdanal.pdf',
    #                       61, -99)



    
if __name__ == '__main__':
    main()
