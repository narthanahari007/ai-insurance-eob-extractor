import os

from PIL import Image

from eob_detector import (
    get_ocr_data,
    find_claim_positions,
    create_blocks
)


PAGE_FOLDER = "processed/pages"
OUTPUT_FOLDER = "exports/service_line_review_images"

TARGETS = {
    (18, 2): [1],
    (32, 3): [1],
    (66, 1): [1],
    (72, 2): [2],
    (78, 1): [1, 2],
}


def main():

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    print("\n========================================")
    print("CREATING SERVICE-LINE REVIEW IMAGES")
    print("========================================")

    created = 0

    for (page_number, block_number), lines in TARGETS.items():

        image_path = os.path.join(
            PAGE_FOLDER,
            f"page_{page_number:03d}.png"
        )

        if not os.path.exists(image_path):
            print(
                "Missing:",
                image_path
            )
            continue

        image = Image.open(
            image_path
        )

        words = get_ocr_data(
            image_path
        )

        claim_positions = (
            find_claim_positions(words)
        )

        blocks = create_blocks(
            words,
            claim_positions
        )

        if block_number > len(blocks):
            continue

        block = blocks[
            block_number - 1
        ]

        for line_number in lines:

            # Find procedure codes in the block.
            procedures = []

            for word in block["words"]:

                text = word["text"].strip()

                if (
                    len(text) == 5
                    and text.isdigit()
                ):
                    procedures.append(
                        word
                    )

            procedures.sort(
                key=lambda word: word["y"]
            )

            if line_number > len(procedures):
                continue

            procedure = procedures[
                line_number - 1
            ]

            y = procedure["y"]

            # Wider crop around the entire service line.
            crop = image.crop(
                (
                    350,
                    max(0, y - 70),
                    min(image.width, 1800),
                    min(image.height, y + 80)
                )
            )

            output_path = os.path.join(
                OUTPUT_FOLDER,
                f"page_{page_number:03d}"
                f"_block_{block_number}"
                f"_line_{line_number}.png"
            )

            crop.save(
                output_path
            )

            print(
                "Created:",
                output_path
            )

            created += 1

    print("\n========================================")
    print("REVIEW IMAGE CREATION COMPLETE")
    print("========================================")

    print(
        "Images created:",
        created
    )


if __name__ == "__main__":
    main()