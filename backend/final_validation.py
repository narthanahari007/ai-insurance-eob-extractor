import json
import os


INPUT_FILE = "exports/extracted_eobs.json"


def main():

    print("\n========================================")
    print("FINAL EOB DATA VALIDATION")
    print("========================================")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        records = json.load(file)

    print("\nTotal records:", len(records))

    # ---------------------------------------------------------
    # Status check
    # ---------------------------------------------------------

    ok_records = [
        r for r in records
        if r.get("status") == "OK"
    ]

    review_records = [
        r for r in records
        if r.get("status") == "REVIEW"
    ]

    print("OK records:", len(ok_records))
    print("REVIEW records:", len(review_records))

    # ---------------------------------------------------------
    # Required field check
    # ---------------------------------------------------------

    required_fields = [
        "patient",
        "patient_number",
        "service_dates",
        "procedure_number"
    ]

    print("\nMissing required fields:")

    missing_count = 0

    for record in records:

        missing = []

        for field in required_fields:

            if not record.get(field):

                missing.append(field)

        if missing:

            missing_count += 1

            print(
                f"Page {record.get('page_number')} "
                f"Block {record.get('block_number')} "
                f"{record.get('patient')}: "
                f"{missing}"
            )

    if missing_count == 0:

        print("None")

    # ---------------------------------------------------------
    # Financial missing-value check
    # ---------------------------------------------------------

    financial_fields = [
        "billed_amount",
        "discount",
        "allowed_amount",
        "not_covered",
        "other_cov",
        "deduc_copay_coins",
        "patient_resp",
        "payment"
    ]

    print("\nRecords with missing financial fields:")

    financial_missing_count = 0

    for record in records:

        missing = []

        for field in financial_fields:

            if record.get(field) is None:

                missing.append(field)

        if missing:

            financial_missing_count += 1

            print(
                f"Page {record.get('page_number')} "
                f"Block {record.get('block_number')} "
                f"{record.get('patient')}: "
                f"{missing}"
            )

    if financial_missing_count == 0:

        print("None")

    # ---------------------------------------------------------
    # Duplicate patient numbers
    # ---------------------------------------------------------

    patient_numbers = {}

    for record in records:

        patient_number = record.get(
            "patient_number"
        )

        if not patient_number:
            continue

        patient_numbers.setdefault(
            patient_number,
            []
        ).append(
            (
                record.get("page_number"),
                record.get("block_number"),
                record.get("patient")
            )
        )

    duplicate_patients = {
        number: locations
        for number, locations
        in patient_numbers.items()
        if len(locations) > 1
    }

    print(
        "\nPatient numbers appearing in multiple records:",
        len(duplicate_patients)
    )

    # ---------------------------------------------------------
    # Page coverage
    # ---------------------------------------------------------

    pages_with_records = sorted(
        set(
            r.get("page_number")
            for r in records
        )
    )

    missing_pages = [
        page
        for page in range(1, 83)
        if page not in pages_with_records
    ]

    print(
        "\nPages containing extracted records:",
        len(pages_with_records)
    )

    print(
        "Pages with no extracted records:",
        missing_pages
    )

    # ---------------------------------------------------------
    # Expected source total
    # ---------------------------------------------------------

    print("\nExpected source information:")
    print("PDF pages: 82")
    print("Previously observed service lines: 210")
    print("Current extracted EOB blocks:", len(records))

    print("\n========================================")
    print("VALIDATION COMPLETE")
    print("========================================")


if __name__ == "__main__":
    main()