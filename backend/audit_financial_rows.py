import os
import re

from eob_detector import (
    get_ocr_data,
    find_claim_positions,
    create_blocks
)


PAGE_FOLDER = "processed/pages"


def is_money(text):

    text = text.strip()

    if "$" not in text:
        return False

    text = (
        text
        .replace(",", ".")
        .replace(" ", "")
        .rstrip(".,:")
    )

    return bool(
        re.fullmatch(
            r"-?\$?\d+\.\d{2}",
            text
        )
    )


def get_money_rows(words):

    rows = {}

    for word in words:

        text = word["text"].strip()

        if not is_money(text):
            continue

        y = word["y"]

        # Group values belonging to approximately
        # the same horizontal financial row.
        matched_y = None

        for existing_y in rows:

            if abs(existing_y - y) <= 12:
                matched_y = existing_y
                break

        if matched_y is None:
            matched_y = y
            rows[matched_y] = []

        rows[matched_y].append({
            "text": text,
            "x": word["x"],
            "y": y
        })

    # Sort values horizontally.
    for y in rows:
        rows[y].sort(
            key=lambda item: item["x"]
        )

    return rows


def main():

    print("\n========================================")
    print("FULL FINANCIAL ROW AUDIT")
    print("========================================")

    candidate_count = 0
    total_blocks = 0

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

        claim_positions = (
            find_claim_positions(words)
        )

        blocks = create_blocks(
            words,
            claim_positions
        )

        for block_number, block in enumerate(
            blocks,
            start=1
        ):

            total_blocks += 1

            money_rows = get_money_rows(
                block["words"]
            )

            # A normal financial line generally has
            # several monetary values.
            valid_rows = [
                (y, values)
                for y, values
                in money_rows.items()
                if len(values) >= 5
            ]

            if len(valid_rows) <= 1:
                continue

            candidate_count += 1

            print("\n----------------------------------------")
            print(
                f"Page {page_number}, "
                f"Block {block_number}"
            )
            print(
                "Financial rows detected:",
                len(valid_rows)
            )
            print("----------------------------------------")

            for row_number, (
                y,
                values
            ) in enumerate(
                valid_rows,
                start=1
            ):

                print(
                    f"\nRow {row_number} "
                    f"(y={y})"
                )

                print(
                    " | ".join(
                        value["text"]
                        for value in values
                    )
                )

    print("\n========================================")
    print("AUDIT COMPLETE")
    print("========================================")

    print(
        "Total EOB blocks:",
        total_blocks
    )

    print(
        "Blocks with multiple financial rows:",
        candidate_count
    )


if __name__ == "__main__":
    main()