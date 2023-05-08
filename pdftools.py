from io import BytesIO
import zipfile
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from PyPDF2 import PdfFileReader, PdfFileWriter
import time
from os import system, name
from PyPDF2 import *
# import pikepdf
# import tqdm
# import pyttsx3
import io
import PyPDF2
import os
import base64


def pdfmerger(file1, file2, output_path):
    def merge_pdfs(paths, output):
        pdf_writer = PdfFileWriter()
        for path in paths:
            pdf_reader = PdfFileReader(path)
            for page in range(pdf_reader.getNumPages()):
                # Add each page to the writer object
                pdf_writer.addPage(pdf_reader.getPage(page))
        # Write out the merged PDF
        with open(output, 'wb') as out:
            pdf_writer.write(out)

    paths = [file1, file2]
    # Convert the uploaded files to a readable format for PyPDF2
    file_data = [io.BytesIO(file.read()) for file in paths]
    paths = [io.BufferedReader(file) for file in file_data]
    # Merge the PDFs
    merge_pdfs(paths, output_path)


def PDFsplit(pdf, splits, outputpdf):
    # creating input pdf file object
    pdfFileObj = open(pdf, 'rb')

    # creating pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    # starting index of first slice
    start = 0

    # starting index of last slice
    end = splits[0]

    for i in range(len(splits)+1):
        # creating pdf writer object for (i+1)th split
        pdfWriter = PyPDF2.PdfFileWriter()

        # output pdf file name
        output_filename = outputpdf.split('.pdf')[0] + str(i) + '.pdf'

        # adding pages to pdf writer object
        for page in range(start, end):
            pdfWriter.addPage(pdfReader.getPage(page))

        # writing split pdf pages to pdf file
        with open(outputpdf, "wb") as f:
            pdfWriter.write(f)

        # interchanging page split start position for next split
        start = end
        try:
            # setting split end position for next split
            end = splits[i+1]
        except IndexError:
            # setting split end position for last split
            end = pdfReader.numPages

    # closing the input pdf file object
    pdfFileObj.close()


def convert_pdf_to_txt(uploaded_file):
    '''Convert pdf content to text
    :uploaded_file the uploaded file
    '''
    rsrcmgr = PDFResourceManager()
    codec = 'utf-8'
    laparams = LAParams()

    with io.StringIO() as retstr:
        with TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams) as device:
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            password = ""
            maxpages = 0
            caching = True
            pagenos = set()

            for page in PDFPage.get_pages(uploaded_file,
                                          pagenos,
                                          maxpages=maxpages,
                                          password=password,
                                          caching=caching,
                                          check_extractable=True):
                interpreter.process_page(page)

            return retstr.getvalue()


def extract_images_zip(pdf_file):
    # Get the number of pages in PDF file
    page_nums = len(pdf_file)

    # Create empty list to store images information
    images_list = []

    # Extract all images information from each page
    for page_num in range(page_nums):
        page_content = pdf_file[page_num]
        images_list.extend(page_content.get_images())

    # Raise error if PDF has no images
    if len(images_list) == 0:
        raise ValueError(f'No images found in {file_path}')

    # Create in-memory zip file
    zip_file = BytesIO()
    with zipfile.ZipFile(zip_file, mode='w') as zf:
        # Save all the extracted images to the zip file
        for i, img in enumerate(images_list, start=1):
            # Extract the image object number
            xref = img[0]
            # Extract image
            base_image = pdf_file.extract_image(xref)
            # Store image bytes
            image_bytes = base_image['image']
            # Store image extension
            image_ext = base_image['ext']
            # Generate image file name
            image_name = str(i) + '.' + image_ext
            # Add image to zip file
            zf.writestr(image_name, image_bytes)

    # Return zip file
    return zip_file.getvalue()
