import pytesseract
from PIL import Image

image_path = "processed/pages/page_001.png"

print("Starting OCR...")
print("Image:", image_path)

text = pytesseract.image_to_string(
    Image.open(image_path),
    lang="eng"
)

print("\n========== OCR RESULT ==========\n")
print(text)
print("\n========== END ==========\n")