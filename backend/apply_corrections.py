import json
import os


INPUT_FILE = "exports/extracted_eobs.json"
OUTPUT_FILE = "exports/extracted_eobs.json"


CORRECTIONS = {

    # Page 8 - Block 1
    (8, 1): {
        "patient_number": "17689778",
        "reason_codes": "45, 23, B7, N257",
    },

    # Page 10 - Block 1
    (10, 1): {
        "patient_number": "17680246",
        "reason_codes": "45, 23, B7, N257",
    },

    # Page 20 - Block 1
    (20, 1): {
        "patient_number": "17987027",
        "allowed_amount": "$219.50",
        "reason_codes": "45",
    },

    # Page 22 - Block 1
    (22, 1): {
        "patient_number": "17711037",
        "reason_codes": "45, 23",
    },

    # Page 48 - Block 3
    (48, 3): {
        "patient_number": "188206487",
        "reason_codes": "45, 253",
    },

    # Page 54 - Block 2
    (54, 2): {
        "patient_number": "18329671",
        "deduc_copay_coins": "$0.00",
        "reason_codes": "45",
    },

    # Page 58 - Block 3
    (58, 3): {
        "patient_number": "188279062",
        "reason_codes": "45, 253",
    },
}


def main():

    print("\n========================================")
    print("APPLYING VERIFIED EOB CORRECTIONS")
    print("========================================")

    if not os.path.exists(INPUT_FILE):
        print("ERROR: extracted_eobs.json not found.")
        return

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        records = json.load(file)

    corrected_count = 0

    for record in records:

        key = (
            record.get("page_number"),
            record.get("block_number")
        )

        if key not in CORRECTIONS:
            continue

        corrections = CORRECTIONS[key]

        print(
            f"\nCorrecting Page {key[0]}, "
            f"Block {key[1]}..."
        )

        for field, value in corrections.items():

            old_value = record.get(field)

            record[field] = value

            print(
                f"  {field}: "
                f"{old_value} -> {value}"
            )

        record["status"] = "OK"
        record["validation_issues"] = ""

        corrected_count += 1

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=4,
            ensure_ascii=False
        )

    ok_count = sum(
        1
        for record in records
        if record.get("status") == "OK"
    )

    review_count = sum(
        1
        for record in records
        if record.get("status") == "REVIEW"
    )

    print("\n========================================")
    print("CORRECTION COMPLETE")
    print("========================================")

    print(
        "Records corrected:",
        corrected_count
    )

    print(
        "OK records:",
        ok_count
    )

    print(
        "Remaining REVIEW records:",
        review_count
    )

    print(
        "\nUpdated:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()