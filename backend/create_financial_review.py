import os
from PIL import Image

from eob_detector import (
    get_ocr_data,
    find_claim_positions,
    create_blocks
)


PAGES_TO_REVIEW = {
    6: [1],
    10: [3],
    12: [2, 3],
    14: [3, 4],
    18: [1],
    34: [1, 3],
    72: [2],
    78: [1],
}


PAGE_FOLDER = "processed/pages"
OUTPUT_FOLDER = "exports/financial_review"


def main():

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    print("\n========================================")
    print("CREATING FINANCIAL REVIEW IMAGES")
    print("========================================")

    created = 0

    for page_number, blocks_needed in PAGES_TO_REVIEW.items():

        image_path = os.path.join(
            PAGE_FOLDER,
            f"page_{page_number:03d}.png"
        )

        if not os.path.exists(image_path):
            print(
                f"Missing page image: {image_path}"
            )
            continue

        print(
            f"\nProcessing Page {page_number}..."
        )

        words = get_ocr_data(image_path)

        claim_positions = find_claim_positions(
            words
        )

        blocks = create_blocks(
            words,
            claim_positions
        )

        image = Image.open(image_path)

        for block_number in blocks_needed:

            if block_number > len(blocks):
                print(
                    f"  Block {block_number} not found"
                )
                continue

            block = blocks[
                block_number - 1
            ]

            start_y = block["start_y"]

            # Focus on the financial table area.
            crop_left = 300
            crop_right = min(
                image.width,
                1900
            )

            crop_top = max(
                0,
                start_y + 190
            )

            crop_bottom = min(
                image.height,
                start_y + 370
            )

            crop = image.crop(
                (
                    crop_left,
                    crop_top,
                    crop_right,
                    crop_bottom
                )
            )

            output_path = os.path.join(
                OUTPUT_FOLDER,
                f"page_{page_number:03d}_block_{block_number}.png"
            )

            crop.save(output_path)

            print(
                f"  Created: "
                f"page_{page_number:03d}_block_{block_number}.png"
            )

            created += 1

    print("\n========================================")
    print("REVIEW IMAGE CREATION COMPLETE")
    print("========================================")

    print(
        "Images created:",
        created
    )

    print(
        "Folder:",
        OUTPUT_FOLDER
    )


if __name__ == "__main__":
    main()