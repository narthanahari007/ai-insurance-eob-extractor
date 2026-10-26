import pytesseract
from PIL import Image


TEST_CASES = [
    (3, 2, 805),
    (4, 1, 220),
]


def main():

    print("\n========================================")
    print("FOCUSED PROCEDURE OCR")
    print("========================================")

    for page_number, block_number, start_y in TEST_CASES:

        image_path = (
            f"processed/pages/"
            f"page_{page_number:03d}.png"
        )

        image = Image.open(image_path)

        # Procedure column is around x=250-520.
        # Procedure row is around start_y + 265.
        crop = image.crop(
            (
                240,
                start_y + 230,
                520,
                start_y + 310
            )
        )

        output_path = (
            f"processed/"
            f"procedure_debug_p{page_number}_b{block_number}.png"
        )

        crop.save(output_path)

        print("\n----------------------------------------")
        print(
            f"PAGE {page_number} - "
            f"BLOCK {block_number}"
        )
        print("----------------------------------------")

        for psm in [3, 6, 7, 11, 12, 13]:

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