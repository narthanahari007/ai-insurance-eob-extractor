import json
import os


INPUT_FILE = "exports/extracted_eobs.json"
SERVICE_LINE_FILE = "exports/service_line_review.json"
OUTPUT_FILE = "exports/final_eob_data.json"


# These 14 blocks contain genuine multiple financial service lines.
MULTI_LINE_BLOCKS = {
    (18, 2),
    (25, 3),
    (27, 2),
    (32, 3),
    (39, 2),
    (39, 3),
    (40, 1),
    (44, 1),
    (52, 2),
    (67, 2),
    (72, 1),
    (72, 2),
    (77, 2),
    (78, 1),
}


# Verified corrections from the source images
BLOCK_CORRECTIONS = {

    (6, 1): {
        "discount": "-$64.65",
        "other_cov": "$64.65",
        "deduc_copay_coins": "$0.00",
        "patient_resp": "$0.00",
        "payment": "$0.00",
    },

    (10, 3): {
        "deduc_copay_coins": "$0.00",
        "patient_resp": "$0.00",
        "payment": "$0.00",
    },

    (12, 2): {
        "deduc_copay_coins": "$0.00",
        "patient_resp": "$0.00",
        "payment": "$23.64",
    },

    (12, 3): {
        "discount": "-$92.28",
        "deduc_copay_coins": "$0.00",
        "patient_resp": "$0.00",
        "payment": "$0.00",
    },

    (14, 3): {
        "other_cov": "$50.23",
        "deduc_copay_coins": "$0.00",
        "patient_resp": "$0.00",
        "payment": "$0.00",
    },

    (14, 4): {
        "patient_resp": "$12.82",
        "payment": "$12.82",
    },

    (18, 1): {
        "patient_resp": "$12.82",
        "payment": "$12.82",
    },

    (34, 1): {
        "not_covered": "$0.00",
        "other_cov": "$0.00",
        "deduc_copay_coins": "$0.00",
        "patient_resp": "$0.00",
        "payment": "$219.50",
    },

    (34, 3): {
        "other_cov": "$0.00",
        "deduc_copay_coins": "$0.00",
        "patient_resp": "$0.00",
        "payment": "$115.28",
    },

}


# Corrections for service-line records verified from images.
SERVICE_LINE_CORRECTIONS = {

    # Page 18 Block 2 Line 1
    (18, 2, 1): {
        "patient_resp": "$0.00",
        "payment": "$0.00",
    },

    # Page 32 Block 3 Line 1
    (32, 3, 1): {
        "discount": "$209.57",
    },

    # Page 72 Block 2 Line 2
    (72, 2, 2): {
        "billed_amount": "$168.00",
    },

    # Page 78 Block 1 Line 1
    (78, 1, 1): {
        "discount": "$92.50",
    },

    # Page 78 Block 1 Line 2
    (78, 1, 2): {
        "discount": "$0.00",
    },
}


def main():

    print("\n========================================")
    print("BUILDING FINAL EOB DATASET")
    print("========================================")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        original_records = json.load(file)

    with open(
        SERVICE_LINE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        service_lines = json.load(file)

    print(
        "Original records:",
        len(original_records)
    )

    final_records = []

    replaced_blocks = 0
    correction_count = 0

    # Group service lines by page/block.
    service_groups = {}

    for record in service_lines:

        key = (
            record.get("page_number"),
            record.get("block_number")
        )

        service_groups.setdefault(
            key,
            []
        ).append(record)

    # Process original records.
    for record in original_records:

        key = (
            record.get("page_number"),
            record.get("block_number")
        )

        # Replace genuine multi-line blocks.
        if key in MULTI_LINE_BLOCKS:

            lines = service_groups.get(
                key,
                []
            )

            if not lines:

                print(
                    "WARNING: no service lines for",
                    key
                )

                final_records.append(
                    record
                )

                continue

            replaced_blocks += 1

            for line in lines:

                line_key = (
                    line.get("page_number"),
                    line.get("block_number"),
                    line.get("service_line")
                )

                corrections = (
                    SERVICE_LINE_CORRECTIONS.get(
                        line_key,
                        {}
                    )
                )

                for field, value in corrections.items():

                    line[field] = value
                    correction_count += 1

                line["status"] = "OK"
                line["validation_issues"] = ""

                final_records.append(
                    line
                )

            continue

        # Keep normal single-line records.
        final_records.append(
            record.copy()
        )

    # Apply verified corrections to normal
    # non-multi-line records.
    for record in final_records:

        key = (
            record.get("page_number"),
            record.get("block_number")
        )

        if key in BLOCK_CORRECTIONS:

            for field, value in BLOCK_CORRECTIONS[key].items():

                record[field] = value
                correction_count += 1

            record["status"] = "OK"
            record["validation_issues"] = ""

    # Add stable final row number.
    for index, record in enumerate(
        final_records,
        start=1
    ):

        record["final_row_number"] = index

    os.makedirs(
        "exports",
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            final_records,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n========================================")
    print("FINAL DATASET CREATED")
    print("========================================")

    print(
        "Original EOB blocks:",
        len(original_records)
    )

    print(
        "Multi-line blocks replaced:",
        replaced_blocks
    )

    print(
        "Final service-line records:",
        len(final_records)
    )

    print(
        "Verified corrections applied:",
        correction_count
    )

    print(
        "Output:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()