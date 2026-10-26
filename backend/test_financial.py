import os
import eob_extractor

from eob_extractor import (
    get_ocr_data,
    find_claim_positions,
    create_blocks,
    extract_block
)


PAGES_TO_TEST = [1, 2]


def main():

    print("\n========================================")
    print("FINANCIAL EXTRACTION TEST")
    print("========================================\n")

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

        # Tell extractor which page is being processed
        eob_extractor.IMAGE_PATH = image_path

        words = get_ocr_data(image_path)

        claim_positions = find_claim_positions(words)

        blocks = create_blocks(
            words,
            claim_positions
        )

        print("EOB blocks:", len(blocks))

        for block in blocks:

            record = extract_block(
                block,
                image_path
            )

            print(
                f"\nBLOCK {block['block_number']}"
            )

            print(
                f"Patient: "
                f"{record.get('patient')}"
            )

            print(
                f"Patient #: "
                f"{record.get('patient_number')}"
            )

            print(
                f"Service Dates: "
                f"{record.get('service_dates')}"
            )

            print(
                f"Procedure: "
                f"{record.get('procedure_number')}"
            )

            print(
                f"Billed Amount: "
                f"{record.get('billed_amount')}"
            )

            print(
                f"Discount: "
                f"{record.get('discount')}"
            )

            print(
                f"Allowed Amount: "
                f"{record.get('allowed_amount')}"
            )

            print(
                f"Not Covered: "
                f"{record.get('not_covered')}"
            )

            print(
                f"Other Cov: "
                f"{record.get('other_cov')}"
            )

            print(
                f"Deduc/Copay/Coins: "
                f"{record.get('deduc_copay_coins')}"
            )

            print(
                f"Patient Resp.: "
                f"{record.get('patient_resp')}"
            )

            print(
                f"Payment: "
                f"{record.get('payment')}"
            )

            print(
                f"Reason Codes: "
                f"{record.get('reason_codes')}"
            )


    print("\n========================================")
    print("FINANCIAL TEST COMPLETE")
    print("========================================")


if __name__ == "__main__":
    main()