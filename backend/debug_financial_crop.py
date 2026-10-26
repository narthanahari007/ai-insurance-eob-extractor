import pytesseract
from PIL import Image


TEST_CASES = [
    (2, 1, 225),
    (2, 2, 805),
    (2, 3, 1382),
]


def main():

    print("\n========================================")
    print("FOCUSED FINANCIAL OCR")
    print("========================================")

    for page_number, block_number, start_y in TEST_CASES:

        image_path = (
            f"processed/pages/"
            f"page_{page_number:03d}.png"
        )

        image = Image.open(image_path)

        # Crop the complete financial/service area.
        crop = image.crop(
            (
                480,
                start_y + 235,
                1800,
                start_y + 330
            )
        )

        output_path = (
            f"processed/"
            f"financial_debug_p{page_number}"
            f"_b{block_number}.png"
        )

        crop.save(output_path)

        print("\n----------------------------------------")
        print(
            f"PAGE {page_number} - "
            f"BLOCK {block_number}"
        )
        print("----------------------------------------")

        for psm in [3, 4, 6, 11, 12]:

            text = pytesseract.image_to_string(
                crop,
                lang="eng",
                config=f"--psm {psm}"
            )

            print(f"\nPSM {psm}:")
            print(repr(text))

    print("\n========================================")
    print("DONE")
    print("========================================")


if __name__ == "__main__":
    main()