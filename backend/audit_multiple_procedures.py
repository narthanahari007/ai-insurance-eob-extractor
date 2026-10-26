import os
import re

from eob_detector import (
    get_ocr_data,
    find_claim_positions,
    create_blocks
)


PAGE_FOLDER = "processed/pages"


def find_procedure_codes(block):

    procedures = []

    for word in block["words"]:

        text = word["text"].strip()

        # Procedure codes in this EOB are generally 5-digit codes.
        if re.fullmatch(r"\d{5}", text):

            # Avoid obvious dates and patient numbers.
            if text.startswith(("17", "18", "19", "20")):
                continue

            procedures.append({
                "code": text,
                "x": word["x"],
                "y": word["y"]
            })

    # Remove duplicates at the same approximate location.
    unique = []

    for item in procedures:

        duplicate = False

        for existing in unique:

            if (
                existing["code"] == item["code"]
                and abs(existing["y"] - item["y"]) < 10
            ):
                duplicate = True
                break

        if not duplicate:
            unique.append(item)

    unique.sort(
        key=lambda item: item["y"]
    )

    return unique


def main():

    print("\n========================================")
    print("AUDITING MULTIPLE PROCEDURE EOBs")
    print("========================================")

    multiple_count = 0
    total_blocks = 0

    for page_number in range(1, 83):

        image_path = os.path.join(
            PAGE_FOLDER,
            f"page_{page_number:03d}.png"
        )

        if not os.path.exists(image_path):
            continue

        words = get_ocr_data(image_path)

        claim_positions = find_claim_positions(
            words
        )

        blocks = create_blocks(
            words,
            claim_positions
        )

        total_blocks += len(blocks)

        for block_number, block in enumerate(
            blocks,
            start=1
        ):

            procedures = find_procedure_codes(
                block
            )

            if len(procedures) > 1:

                multiple_count += 1

                print(
                    f"\nPage {page_number}, "
                    f"Block {block_number}"
                )

                print(
                    "Procedure codes:"
                )

                for procedure in procedures:

                    print(
                        f"  {procedure['code']} "
                        f"(y={procedure['y']})"
                    )

    print("\n========================================")
    print("AUDIT COMPLETE")
    print("========================================")

    print(
        "Total EOB blocks scanned:",
        total_blocks
    )

    print(
        "Blocks with multiple procedures:",
        multiple_count
    )


if __name__ == "__main__":
    main()