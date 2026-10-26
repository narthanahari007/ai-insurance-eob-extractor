import pytesseract
from PIL import Image

image_path = "processed/pages/page_001.png"

print("Starting OCR coordinate test...")

image = Image.open(image_path)

data = pytesseract.image_to_data(
    image,
    lang="eng",
    config="--psm 3",
    output_type=pytesseract.Output.DICT
)

print("\n========== OCR WORDS ==========\n")

for i in range(len(data["text"])):

    text = data["text"][i].strip()
    confidence = float(data["conf"][i])

    if text and confidence > 30:

        x = data["left"][i]
        y = data["top"][i]
        width = data["width"][i]
        height = data["height"][i]

        print(
            f"{text:<25} "
            f"confidence={confidence:>6.1f} "
            f"x={x:<5} "
            f"y={y:<5} "
            f"w={width:<5} "
            f"h={height:<5}"
        )

print("\n========== END ==========\n")