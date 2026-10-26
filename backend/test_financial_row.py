import os
import eob_extractor

from eob_extractor import (
    get_ocr_data,
    find_claim_positions,
    create_blocks,
    extract_financial_row
)


PAGES_TO_TEST = [3, 4, 5]


def main():

    print("\n========================================")
    print("FINANCIAL ROW PARSER TEST")
    print("========================================")

    for page_number in PAGES_TO_TEST:

        image_path = (
            f"processed/pages/"
            f"page_{page_number:03d}.png"
        )

        print("\n----------------------------------------")
        print(f"PAGE {page_number}")
        print("----------------------------------------")

        if not os.path.exists(image_path):
            print("Image not found:", image_path)
            continue

        eob_extractor.IMAGE_PATH = image_path

        words = get_ocr_data(image_path)

        claim_positions = find_claim_positions(words)

        blocks = create_blocks(
            words,
            claim_positions
        )

        for block in blocks:

            values = extract_financial_row(
                block["words"],
                block["start_y"]
            )

            print(
                f"\nBLOCK {block['block_number']}"
            )

            for value in values:

                print(
                    f"x={str(value['x']):<5} "
                    f"y={str(value['y']):<5} "
                    f"value={value['text']}"
                )

    print("\n========================================")
    print("TEST COMPLETE")
    print("========================================")


if __name__ == "__main__":
    main()
