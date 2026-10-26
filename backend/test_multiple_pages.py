import os
import eob_extractor

from eob_extractor import (
    get_ocr_data,
    find_claim_positions,
    create_blocks,
    extract_patient,
    extract_patient_number,
    extract_service_dates,
    extract_procedure
)


PAGES_TO_TEST = [1, 2, 3, 4, 5]


def main():

    print("\n========================================")
    print("MULTI-PAGE EXTRACTION TEST")
    print("========================================\n")

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

        # Tell extractor which page is being processed
        eob_extractor.IMAGE_PATH = image_path

        words = get_ocr_data(image_path)

        print("OCR words:", len(words))

        claim_positions = find_claim_positions(words)

        print("Claim positions:", claim_positions)

        blocks = create_blocks(
            words,
            claim_positions
        )

        print("EOB blocks:", len(blocks))

        total_blocks += len(blocks)

        for block in blocks:

            patient = extract_patient(
                block["words"],
                block["start_y"]
            )

            patient_number = extract_patient_number(
                block["words"],
                block["start_y"]
            )

            service_dates = extract_service_dates(
                block["words"],
                block["start_y"]
            )

            procedure = extract_procedure(
                block["words"],
                block["start_y"]
            )

            print(f"\n  BLOCK {block['block_number']}")
            print(f"  Patient: {patient}")
            print(f"  Patient #: {patient_number}")
            print(f"  Service Dates: {service_dates}")
            print(f"  Procedure: {procedure}")

    print("\n========================================")
    print("TEST COMPLETE")
    print("========================================")

    print("\nTotal EOB blocks found:", total_blocks)


if __name__ == "__main__":
    main()