import os
import eob_extractor

from eob_extractor import (
    get_ocr_data,
    find_claim_positions,
    create_blocks,
    extract_block,
    extract_financial_row
)


PAGES_TO_TEST = list(range(1, 11))


def main():

    print("\n========================================")
    print("COMPLETE EOB EXTRACTION TEST")
    print("========================================")

    total_blocks = 0

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

        print("Detected blocks:", len(blocks))

        for block in blocks:

            total_blocks += 1

            record = extract_block(
                block,
                image_path
            )

            financial_values = extract_financial_row(
                block["words"],
                block["start_y"]
            )

            print(
                f"\nBLOCK {block['block_number']}"
            )

            print(
                "Patient:",
                record.get("patient")
            )

            print(
                "Patient #:",
                record.get("patient_number")
            )

            print(
                "Service Dates:",
                record.get("service_dates")
            )

            print(
                "Procedure:",
                record.get("procedure_number")
            )

            print(
                "Reason Codes:",
                record.get("reason_codes")
            )

            print("\nFinancial:")

            names = [
                "Billed",
                "Discount",
                "GRT",
                "Allowed",
                "Not Covered",
                "Other Cov",
                "Deduc/Copay/Coins",
                "Patient Resp.",
                "Payment"
            ]

            for i, value in enumerate(financial_values):

                if i >= len(names):
                    break

                print(
                    f"{names[i]}: {value['text']}"
                )

    print("\n========================================")
    print("SUMMARY")
    print("========================================")

    print("Pages tested:", len(PAGES_TO_TEST))
    print("Total blocks:", total_blocks)

    print("\nTEST COMPLETE")


if __name__ == "__main__":
    main()