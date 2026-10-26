import os

from eob_extractor import (
    get_ocr_data,
    find_claim_positions,
    create_blocks
)


PAGE = 2


def main():

    image_path = (
        f"processed/pages/"
        f"page_{PAGE:03d}.png"
    )

    print("\n========================================")
    print("FINANCIAL OCR DEBUG")
    print("========================================")

    if not os.path.exists(image_path):
        print("Image not found:", image_path)
        return

    words = get_ocr_data(image_path)

    claim_positions = find_claim_positions(words)

    blocks = create_blocks(
        words,
        claim_positions
    )

    for block in blocks:

        start_y = block["start_y"]

        print("\n----------------------------------------")
        print(
            f"PAGE {PAGE} - "
            f"BLOCK {block['block_number']}"
        )
        print(
            f"Y range: "
            f"{block['start_y']} -> {block['end_y']}"
        )
        print("----------------------------------------")

        # Financial/service rows normally occur
        # around start_y + 265.
        target_y = start_y + 265

        print("\nFinancial-area OCR:\n")

        for word in block["words"]:

            distance = abs(
                word["y"] - target_y
            )

            if distance <= 80:

                print(
                    f"text={word['text']:<20} "
                    f"x={word['x']:<5} "
                    f"y={word['y']:<5} "
                    f"distance={distance:<5} "
                    f"confidence={word['confidence']:.1f}"
                )


if __name__ == "__main__":
    main()