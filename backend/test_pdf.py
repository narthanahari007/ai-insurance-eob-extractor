import fitz

pdf_path = "../uploads/presbyterian.pdf"

doc = fitz.open(pdf_path)

print("Total pages:", len(doc))

doc.close()