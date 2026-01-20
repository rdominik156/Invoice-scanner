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
windowsPath = r"D:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.tesseract_cmd = windowsPath

folder_path = r"D:\Programozás\VS gyakorlás\Számla extraktor\invoices"

# Kigyűjtöm a számlákon gyakran előforduló mezőket és azok lehetséges mintáit
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def ocr_pdf(pdf_path):
    images = convert_from_path(pdf_path=pdf_path, dpi=300)
    text = ""

    for img in images:
        img_np = np.array(img)
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]
        text += pytesseract.image_to_string(gray)

    return text

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

# Fő függvény a számla feldolgozására (Text alapú vagy OCR)
def parse_invoice(pdf_path):
    text = extract_text_from_pdf(pdf_path)

    # If very little text is found, assume scanned PDF
    if len(text) < 15:
        print("Scanned PDF detected → using OCR")
        #text = ocr_pdf(pdf_path)
        #images = PDF_to_images2(pdf_path)
        #extract_text(images[0])
        text = extract_text("invoices/page_1.png")
        print(text)

    else:
        print("Text-based PDF detected")

    invoice_data = extract_invoice_fields(text)
    return invoice_data, text

def PDF_to_images(pdf_path):
    list = []
    img_count = 0
    doc = fitz.open(pdf_path)


    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            list.append(base_image)

            image_filename = f"page{page_index+1}_img{img_index+1}.{image_ext}"
            #image_path = os.path.join(output_dir, image_filename)

            #with open(image_path, "wb") as f:
            #    f.write(image_bytes)

            img_count += 1

    print(f"Extracted {img_count} images")
    return list

def PDF_to_images2(pdf_path):
    doc = fitz.open(pdf_path)

    for page in doc:
        images = page.get_images(full=True)
        if len(images) != 1:
            raise RuntimeError(f"Expected 1 image on page, found {len(images)}")
    
        xref = images[0][0]
        img = doc.extract_image(xref)
        image_bytes = img["image"]
        image_ext = img["ext"]

        pil_img = Image.open(io.BytesIO(img["image"]))
        text =+ pytesseract.image_to_string(pil_img)
        #images.append(text)

        #output_path = os.path.join("invoices", f"page_{1}.{image_ext}")

    #with open(output_path, "wb") as f:
    #    f.write(image_bytes)

    return text

def extract_text(image_path):
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text

def process_invoice_folder(folder_path, output_csv="invoices.csv"):
    results = []

    for file in os.listdir(folder_path):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file)
            print(pdf_path)
            print(f"Processing: {file}")
            invoice_data = parse_invoice(pdf_path)
            results.append(invoice_data)
    for resoult in results:
        print(resoult)
        print("\n")

    #df = pd.DataFrame(results)
    #df.to_csv(output_csv, index=False)
    #return df


if __name__ == "__main__":
    invoice_data, raw_text = parse_invoice("invoices\invoice.pdf") # invoice_data = már kinyert mezők, raw_text = teljes szöveg
    process_invoice_folder(folder_path)

    print("\nExtracted Invoice Data:")
    for k, v in invoice_data.items(): # kiíratás, itt kell majd ecelbe rakni.
        print(f"{k}: {v}") 



class ImageReader:
    def __init__(self, image_path):
        self.image_path = image_path
        windowsPath = r"D:\Program Files\Tesseract-OCR\tesseract.exe"
        pytesseract.tesseract_cmd = windowsPath

    def extract_text(self):
        img = Image.open(self.image_path)
        text = pytesseract.image_to_string(img)
        return text
    
""" if __name__ == "__main__":
    reader = ImageReader(image_path)
    extracted_text = reader.extract_text()
    print(extracted_text) """