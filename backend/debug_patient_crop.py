import pytesseract
from PIL import Image

PAGE = 4

image_path = (
    f"processed/pages/page_{PAGE:03d}.png"
)

image = Image.open(image_path)

print("\n========================================")
print("FOCUSED PATIENT OCR")
print("========================================")

# Page 4 Block 2 starts around y = 1381.
# Patient name is around y = 1412.
crop = image.crop(
    (
        200,     # left
        1385,    # top
        750,     # right
        1450     # bottom
    )
)

crop.save("processed/patient_debug.png")

print("\nTesting different OCR modes...\n")

for psm in [3, 6, 11, 12]:

    text = pytesseract.image_to_string(
        crop,
        lang="eng",
        config=f"--psm {psm}"
    )

    print("----------------------------------------")
    print(f"PSM {psm}")
    print("----------------------------------------")
    print(repr(text))


print("\n========================================")
print("DONE")
print("========================================")