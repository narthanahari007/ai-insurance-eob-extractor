from eob_extractor import (
    get_ocr_data,
    find_claim_positions,
    create_blocks
)

TEST_CASES = [
    (4, 1),
    (4, 2),
]


def main():

    print("\n========================================")
    print("PATIENT NAME DEBUG")
    print("========================================")

    for page_number, block_number in TEST_CASES:

        image_path = (
            f"processed/pages/"
            f"page_{page_number:03d}.png"
        )

        print("\n\n----------------------------------------")
        print(f"PAGE {page_number} - BLOCK {block_number}")
        print("----------------------------------------")

        words = get_ocr_data(image_path)

        claim_positions = find_claim_positions(words)

        blocks = create_blocks(
            words,
            claim_positions
        )

        block = blocks[block_number - 1]

        start_y = block["start_y"]

        print(
            f"Block Y range: "
            f"{start_y} -> {block['end_y']}"
        )

        print("\nOCR words near patient area:\n")

        # Patient information is normally
        # near the beginning of the block.
        for word in block["words"]:

            distance = abs(
                word["y"] - (start_y + 35)
            )

            if distance <= 70 and word["x"] < 700:

                print(
                    f"text={word['text']:<25} "
                    f"x={word['x']:<5} "
                    f"y={word['y']:<5} "
                    f"distance={distance:<5} "
                    f"confidence={word['confidence']:.1f}"
                )


if __name__ == "__main__":
    main()