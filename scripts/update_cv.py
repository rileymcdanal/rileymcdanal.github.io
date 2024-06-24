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
import PyPDF2


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata']


def replace_number_in_pdf(input_pdf_path, output_pdf_path, old_number, new_number):
    # Open the input PDF
    with open(input_pdf_path, 'rb') as input_pdf_file:
        reader = PyPDF2.PdfReader(input_pdf_file)
        writer = PyPDF2.PdfWriter()

        # Iterate through the pages and replace the number
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num] 
            content = page.extract_text()
            updated_content = content.replace(str(old_number), str(new_number))
            print('$$$$$$$$$$$')
            print(updated_content)
            print('$$$$$$$$$$$')
            # Write the updated content to a new page
            new_page = writer.add_blank_page(width=page.mediabox.width, height=page.mediabox.height)
            new_page.merge_page(page)
            new_page_content = PyPDF2.PageObject.create_blank_page(width=page.mediabox.width,
                                                                     height=page.mediabox.height)
            # new_page_content.mergeTranslatedPage(new_page, 0, 0)
            new_page.add_transformation(PyPDF2.Transformation().translate(0, 0)); new_page_content.merge_page(new_page, 0)

            # Note: PyPDF2 does not support editing text directly in a page, so this is a workaround
            # More complex PDFs may require a different approach

            writer.add_page(new_page_content)

        # Write the output PDF
        with open(output_pdf_path, 'wb') as output_pdf_file:
            writer.write(output_pdf_file)

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
    PdfWriter("PDFs/CV_mcdanal.pdf", trailer=trailer).write()

    replace_number_in_pdf('PDFs/CV_mcdanal.pdf', 'PDFs/CV_mcdanal.pdf',
                          61, -99)



    
if __name__ == '__main__':
    main()
