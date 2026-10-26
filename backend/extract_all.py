import os
import csv
import json
import eob_extractor

from eob_extractor import (
    get_ocr_data,
    find_claim_positions,
    create_blocks,
    extract_block
)


INPUT_FOLDER = "processed/pages"
OUTPUT_FOLDER = "exports"

OUTPUT_JSON = os.path.join(
    OUTPUT_FOLDER,
    "extracted_eobs.json"
)

OUTPUT_CSV = os.path.join(
    OUTPUT_FOLDER,
    "extracted_eobs.csv"
)


def validate_record(record):

    issues = []

    # ---------------------------------------------------------
    # Required fields
    # ---------------------------------------------------------

    required_fields = [
        "patient",
        "patient_number",
        "service_dates",
        "procedure_number"
    ]

    for field in required_fields:

        value = record.get(field)

        if not value:

            issues.append(
                f"Missing {field}"
            )

    # ---------------------------------------------------------
    # Patient number validation
    # ---------------------------------------------------------

    patient_number = record.get(
        "patient_number"
    )

    if patient_number:

        if not str(
            patient_number
        ).isdigit():

            issues.append(
                "Invalid patient number"
            )

    # ---------------------------------------------------------
    # Procedure validation
    # ---------------------------------------------------------

    procedure = record.get(
        "procedure_number"
    )

    if procedure:

        procedure = str(
            procedure
        )

        if not procedure.isdigit():

            issues.append(
                "Invalid procedure number"
            )

    # ---------------------------------------------------------
    # Reason code review
    # ---------------------------------------------------------

    reason_codes = record.get(
        "reason_codes"
    )

    if reason_codes:

        if len(
            reason_codes
        ) > 60:

            issues.append(
                "Reason codes need review"
            )

    # ---------------------------------------------------------
    # Final status
    # ---------------------------------------------------------

    if issues:

        record["status"] = "REVIEW"

        record["validation_issues"] = (
            "; ".join(issues)
        )

    else:

        record["status"] = "OK"

        record["validation_issues"] = ""

    return record


def main():

    print("\n========================================")
    print("FULL 82-PAGE EOB EXTRACTION")
    print("========================================")

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    all_records = []

    total_pages = 0
    total_blocks = 0

    # ---------------------------------------------------------
    # Process all page images
    # ---------------------------------------------------------

    for page_number in range(1, 83):

        image_path = os.path.join(
            INPUT_FOLDER,
            f"page_{page_number:03d}.png"
        )

        if not os.path.exists(
            image_path
        ):

            print(
                f"\nPage {page_number}: IMAGE NOT FOUND"
            )

            continue

        total_pages += 1

        print(
            f"\nProcessing Page "
            f"{page_number}/82..."
        )

        try:

            # Set image for focused OCR
            eob_extractor.IMAGE_PATH = (
                image_path
            )

            words = get_ocr_data(
                image_path
            )

            claim_positions = (
                find_claim_positions(
                    words
                )
            )

            blocks = create_blocks(
                words,
                claim_positions
            )

            print(
                "  Detected blocks:",
                len(blocks)
            )

            for block in blocks:

                total_blocks += 1

                record = extract_block(
                    block,
                    image_path
                )

                # Add source information
                record["page_number"] = (
                    page_number
                )

                record["block_number"] = (
                    block["block_number"]
                )

                # Validate
                record = validate_record(
                    record
                )

                all_records.append(
                    record
                )

        except Exception as error:

            print(
                f"  ERROR on Page "
                f"{page_number}: {error}"
            )

    # ---------------------------------------------------------
    # Save JSON
    # ---------------------------------------------------------

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_records,
            file,
            indent=4,
            ensure_ascii=False
        )

    # ---------------------------------------------------------
    # Save CSV
    # ---------------------------------------------------------

    fieldnames = [
        "page_number",
        "block_number",
        "patient",
        "patient_number",
        "service_dates",
        "procedure_number",
        "billed_amount",
        "discount",
        "allowed_amount",
        "not_covered",
        "other_cov",
        "deduc_copay_coins",
        "patient_resp",
        "payment",
        "reason_codes",
        "status",
        "validation_issues"
    ]

    with open(
        OUTPUT_CSV,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for record in all_records:

            writer.writerow(
                {
                    field: record.get(
                        field,
                        ""
                    )
                    for field in fieldnames
                }
            )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    review_count = sum(
        1
        for record in all_records
        if record.get("status") == "REVIEW"
    )

    ok_count = sum(
        1
        for record in all_records
        if record.get("status") == "OK"
    )

    print("\n========================================")
    print("EXTRACTION COMPLETE")
    print("========================================")

    print(
        "Pages processed:",
        total_pages
    )

    print(
        "Total EOB blocks:",
        total_blocks
    )

    print(
        "OK records:",
        ok_count
    )

    print(
        "Records requiring review:",
        review_count
    )

    print(
        "\nJSON saved:",
        OUTPUT_JSON
    )

    print(
        "CSV saved:",
        OUTPUT_CSV
    )


if __name__ == "__main__":
    main()