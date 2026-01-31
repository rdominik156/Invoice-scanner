import pdfplumber
import pytesseract
import re
import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
import os
import pandas as pd
import fitz
import io

# Global variables
tesseractWindowsPath = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = tesseractWindowsPath

#main_folder_path = r"D:\Programozás\VS gyakorlás\Számla extraktor\invoices"
main_folder_path = r"C:/Users/User/Documents/GitHub/Invoice-scanner"

# ----- PDF-en használt műveletek -----
# Kigyűjtöm a számlákon gyakran előforduló mezőket és azok lehetséges mintáit
def szöveg_vagy_kép_PDF(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def ocr_image(image_objs):
    text = ""
    for i in range(len(image_objs)):
        image_bytes = image_objs[i]["image"]
        io_bytes = io.BytesIO(image_bytes)
        img = Image.open(io_bytes)
        text += pytesseract.image_to_string(img)
    return text

# ----- REGEX -----
# Mezők kinyerése reguláris kifejezésekkel
def extract_invoice_fields(text):
    patterns = {
        "Számlaszám": [r"Számlaszám\s*(No|#)?[:\-]?\s*([A-Z0-9\-]+)",
                       r"Invoice\s*Number[:\-]?\s*([A-Z0-9\-]+)"],
        "Számla_dátuma": [r"Számla kelte[:\-]?\s*([\d/.-]+)",
                          r"Invoice\s*Date[:\-]?\s*([\d/.-]+)"],
        "Összeg": [r"(Total\s*(Amount)?|Grand\s*Total)[:\-]?\s*\$?([\d,]+\.\d{2})"],
    }

    data = {}

    for key, patterns_list in patterns.items():
        match = None
        for pattern in patterns_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                break
        if match:
            data[key] = match.group(match.lastindex)
        else:
            data[key] = None

    return data

# ----- fő művelet -----
# Fő függvény a számla feldolgozására (Text alapú vagy OCR)
def számla_feldolgozás(pdf_path):
    text = szöveg_vagy_kép_PDF(pdf_path)

    # If very little text is found, assume scanned PDF
    if len(text) < 15:
        print("Scanned PDF detected → using OCR")

        images = PDF_to_images(pdf_path)
        text = ocr_image(images)
        print(text)

        #text = extract_text("invoices/page_1.png")
        #print(text)

    else:
        print("Text-based PDF detected")
        text = szöveg_vagy_kép_PDF(pdf_path)


    invoice_data = extract_invoice_fields(text)
    return invoice_data, text

def PDF_to_images(pdf_path):
    list = []

    doc = fitz.open(pdf_path)                       # 1. kinyitom a pdf-et
    for page_index in range(len(doc)):              # 2. iterálom az összes oldalt
        page = doc[page_index]                      # 3. lementem az oldal tatlmát
        image_list = page.get_images(full=True)     # 4. lementem az oldalról az összes képet

        for img_index, img in enumerate(image_list):
            xref = img[0]                           # 5. a kép byte-jainak lementése
            base_image = doc.extract_image(xref)
            list.append(base_image)

    doc.close()
    return list

if __name__ == "__main__":
    root_folder = r"C:/Users/User/Documents/GitHub/Invoice-scanner"

    exclude = set(["New folder", "Windows", "Desktop", ".venv", "venv", ".git"])
    for current_path, folders, files in os.walk(root_folder):
        folders[:] = [d for d in folders if d not in exclude]
        # If this folder has NO subfolders
        if not folders:
            for file in files:
                if file.lower().endswith(".pdf"):
                    pdf_path = os.path.join(current_path, file)
                    invoice_data, raw_text = számla_feldolgozás(pdf_path) # invoice_data = már kinyert mezők, raw_text = teljes szöveg   

    print("\nExtracted Invoice Data:")
    for k, v in invoice_data.items(): # kiíratás, itt kell majd ecelbe rakni.
        print(f"{k}: {v}") 