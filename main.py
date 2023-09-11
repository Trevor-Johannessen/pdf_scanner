import os
import re
import sys
import fitz
import io
from PIL import Image
from pytesseract import pytesseract

"""
    PDF-TEXT-GRABBER
        Grabs images from image-only pdfs and extracts the textual contents

    USE CASES:
    1. Select document to grab from
    2. Select page to extract text
    3. Select page range to extract text
    4. Send data to be interpreted by Chatp-GPT
    5. -h or --help flags are provided, which should explain how to use the program
"""

def error(str):
    print(f"ERROR: {str}")
    sys.exit(-1)

# get pdf documents
print("Loading pdfs from ./Documents")
files = [x for x in os.listdir("./Documents") if re.search(".pdf$", x)]

# edge-case: no documents
if len(files) <= 0:
    error("No documents in documents folder. Use --help for more details. ")

# ask user which document to use
ids="0"
if len(files)-1 > 0:
    ids = f"0-{len(files)}"
print(f"Select document [{ids}]:")
for i in range(len(files)): 
    print(f"{i}: {files[i]}")
try:
    pdf_id = int(input())
except:
    error("ID could not be identified. Please input numerical ID.")
if pdf_id < 0 or pdf_id > len(files)-1:
    error(f"ID out of range. (Given ({pdf_id}), expected [{ids}])")

# initalize pytesseract
print("Loading pytesseract")
pytesseract.tesseract_cmd = f'/opt/homebrew/bin/tesseract'

# load PDF
print(f"Loading {files[pdf_id]}")
pdf_file = fitz.open(f"./Documents/{files[pdf_id]}")

# initalize interval
interval_start = 1
interval_end = len(pdf_file)

# get desired pages
while True:
    print("Please enter the page or range you would like to extract. Leave blank for all pages.")
    print("Type help for examples")
    str = input()
    if str == "help":
        print("""
Enter the page number or range of pages using interval notation.
Interval Notation:
    () - exclusive/exclusive
    [] - inclusive/inclusive
    [) - inclusive/exclusive
Examples:
    7: Get only the 7th page.
    [10-15): Get pages 10, 11, 12, 13, 14.
    (10-15): Get pages 11, 12, 13, 14.
        """)
        continue
    elif re.match('[\(\[]\d+[,-]\d+[\)\]]', str):
        p1 = str[0:1]
        p2 = str[-1]
        delimeter = re.search("[-,]", str)
        if delimeter:    
            delimeter = delimeter.start()
            interval_start = int(str[1:delimeter])
            interval_end = int(str[delimeter+1:-1])
            if p1 == "(":
                interval_start = interval_start + 1
            if p2 == "]":
                interval_end = interval_end + 1
            if interval_end > len(pdf_file):
                interval_end = len(pdf_file)
            if interval_start < 1:
                interval_start = 1
            if interval_end < interval_start:
                error("Interval end cannot be lower than interval start.")
            break
    elif re.match('\d+', str):
        interval_start = int(str)
        interval_end = interval_start+1
        break
    elif str == "":
        break
    print(f"Unrecognized input {str}")

# process file
for page_index in range(interval_start, interval_end):
    page = pdf_file[page_index]
    images = page.get_images()
    for image in images:
        xref = image[0]
        pixmap = fitz.Pixmap(pdf_file, xref)
        pix_binary = io.BytesIO(pixmap.tobytes("pbm"))
        pix_image = Image.open(pix_binary)
        text = pytesseract.image_to_string(pix_image)
        print(text)

