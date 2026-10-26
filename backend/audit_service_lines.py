import os
import re

from eob_detector import (
    get_ocr_data,
    find_claim_positions,
    create_blocks
)


PAGE_FOLDER = "processed/pages"


def get_procedures(block):

    procedures = []

    for word in block["words"]:

        text = word["text"].strip()

        if not re.fullmatch(r"\d{5}", text):
            continue

        # Ignore likely patient/date-like numbers
        if text.startswith(("17", "18", "19", "20")):
            continue

        procedures.append({
            "code": text,
            "x": word["x"],
            "y": word["y"]
        })

    # Remove OCR duplicates at almost identical positions
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


def get_money_near_row(words, procedure_y):

    values = []

    for word in words:

        text = word["text"].strip()

        if "$" not in text:
            continue

        cleaned = text.replace(",", ".")
        cleaned = cleaned.rstrip(".,:")

        if not re.fullmatch(
            r"-?\$?\d+\.\d{2}",
            cleaned
        ):
            continue

        distance = abs(
            word["y"] - procedure_y
        )

        if distance <= 30:

            values.append({
                "value": cleaned,
                "x": word["x"],
                "y": word["y"],
                "distance": distance
            })

    values.sort(
        key=lambda item: item["x"]
    )

    return values


def main():

    print("\n========================================")
    print("SERVICE-LINE FINANCIAL AUDIT")
    print("========================================")

    candidate_count = 0

    for page_number in range(1, 83):

        image_path = os.path.join(
            PAGE_FOLDER,
            f"page_{page_number:03d}.png"
        )

        if not os.path.exists(image_path):
            continue

        words = get_ocr_data(
            image_path
        )

        claim_positions = find_claim_positions(
            words
        )

        blocks = create_blocks(
            words,
            claim_positions
        )

        for block_number, block in enumerate(
            blocks,
            start=1
        ):

            procedures = get_procedures(
                block
            )

            if len(procedures) <= 1:
                continue

            candidate_count += 1

            print("\n----------------------------------------")
            print(
                f"Page {page_number}, "
                f"Block {block_number}"
            )
            print("----------------------------------------")

            for index, procedure in enumerate(
                procedures,
                start=1
            ):

                print(
                    f"\nService line {index}"
                )

                print(
                    "Procedure:",
                    procedure["code"]
                )

                print(
                    "Procedure Y:",
                    procedure["y"]
                )

                money_values = get_money_near_row(
                    block["words"],
                    procedure["y"]
                )

                if money_values:

                    print("Financial values:")

                    for value in money_values:

                        print(
                            f"  {value['value']} "
                            f"(x={value['x']}, "
                            f"y={value['y']})"
                        )

                else:

                    print(
                        "  NO FINANCIAL VALUES "
                        "NEAR THIS PROCEDURE"
                    )

    print("\n========================================")
    print("AUDIT COMPLETE")
    print("========================================")

    print(
        "Candidate multi-procedure blocks:",
        candidate_count
    )


if __name__ == "__main__":
    main()