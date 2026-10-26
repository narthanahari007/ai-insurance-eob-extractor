import os
import eob_extractor

from eob_extractor import (
    get_ocr_data,
    find_claim_positions,
    create_blocks
)

from PIL import Image, ImageEnhance, ImageFilter
import pytesseract


PAGE_NUMBER = 4
BLOCK_NUMBER = 1


def main():

    image_path = (
        f"processed/pages/"
        f"page_{PAGE_NUMBER:03d}.png"
    )

    if not os.path.exists(image_path):
        print("Image not found:", image_path)
        return

    eob_extractor.IMAGE_PATH = image_path

    words = get_ocr_data(image_path)

    claim_positions = find_claim_positions(words)

    blocks = create_blocks(
        words,
        claim_positions
    )

    block = blocks[BLOCK_NUMBER - 1]

    start_y = block["start_y"]

    print("\n========================================")
    print("ENHANCED REASON CODE OCR")
    print("========================================")

    print("Page:", PAGE_NUMBER)
    print("Block:", BLOCK_NUMBER)
    print("start_y:", start_y)

    image = Image.open(image_path)

    crop = image.crop(
        (
            1580,
            start_y + 245,
            1850,
            start_y + 335
        )
    )

    # Make the text larger.
    crop = crop.resize(
        (
            crop.width * 4,
            crop.height * 4
        )
    )

    # Convert to grayscale.
    crop = crop.convert("L")

    # Increase contrast.
    crop = ImageEnhance.Contrast(
        crop
    ).enhance(2.5)

    # Sharpen text.
    crop = crop.filter(
        ImageFilter.SHARPEN
    )

    crop.save(
        "processed/reason_codes_enhanced.png"
    )

    print("\nOCR results:\n")

    for psm in [6, 7, 11, 12, 13]:

        text = pytesseract.image_to_string(
            crop,
            lang="eng",
            config=(
                f"--psm {psm} "
                "-c tessedit_char_whitelist="
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                "abcdefghijklmnopqrstuvwxyz"
                "0123456789,."
            )
        )

        print(f"PSM {psm}:")
        print(repr(text))
        print()


if __name__ == "__main__":
    main()