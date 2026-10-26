import json
import os
import re

from PIL import Image
import pytesseract

from eob_extractor import (
    extract_patient,
    extract_patient_number,
    extract_service_dates,
    extract_reason_codes,
)

from eob_detector import (
    get_ocr_data,
    find_claim_positions,
    create_blocks,
)


PAGE_FOLDER = "processed/pages"
INPUT_FILE = "exports/extracted_eobs.json"
OUTPUT_FILE = "exports/service_line_review.json"


# Financial column positions from the EOB layout.
FINANCIAL_FIELDS = [
    "billed_amount",
    "discount",
    "grt",
    "allowed_amount",
    "not_covered",
    "other_cov",
    "deduc_copay_coins",
    "patient_resp",
    "payment",
]


# Only these blocks need multi-line investigation.
CANDIDATES = {
    (18, 2),
    (25, 3),
    (27, 2),
    (32, 3),
    (39, 2),
    (39, 3),
    (40, 1),
    (44, 1),
    (52, 2),
    (66, 1),
    (67, 2),
    (72, 1),
    (72, 2),
    (77, 2),
    (78, 1),
}


def money_value(text):

    text = text.strip()

    if "$" not in text:
        return None

    text = (
        text
        .replace(",", ".")
        .replace(" ", "")
        .rstrip(".,:")
    )

    if not re.fullmatch(
        r"-?\$?\d+\.\d{2}",
        text
    ):
        return None

    return text


def get_procedures(words):

    procedures = []

    for word in words:

        text = word["text"].strip()

        if not re.fullmatch(
            r"\d{5}",
            text
        ):
            continue

        procedures.append({
            "code": text,
            "x": word["x"],
            "y": word["y"],
        })

    # Remove duplicate OCR detections.
    unique = []

    for item in procedures:

        duplicate = False

        for existing in unique:

            if (
                existing["code"] == item["code"]
                and abs(
                    existing["y"] - item["y"]
                ) < 10
            ):
                duplicate = True
                break

        if not duplicate:
            unique.append(item)

    unique.sort(
        key=lambda item: item["y"]
    )

    return unique


def get_coordinate_financials(
    words,
    procedure_y
):

    values = []

    for word in words:

        value = money_value(
            word["text"]
        )

        if value is None:
            continue

        if abs(
            word["y"] - procedure_y
        ) <= 30:

            values.append({
                "value": value,
                "x": word["x"],
                "y": word["y"],
            })

    values.sort(
        key=lambda item: item["x"]
    )

    return values


def focused_financial_ocr(
    image,
    procedure_y
):

    # Crop only the financial row.
    crop = image.crop(
        (
            450,
            max(0, procedure_y - 35),
            min(image.width, 1700),
            min(
                image.height,
                procedure_y + 35
            ),
        )
    )

    best = []

    for psm in [6, 7, 11, 12]:

        data = pytesseract.image_to_data(
            crop,
            lang="eng",
            config=f"--psm {psm}",
            output_type=pytesseract.Output.DICT,
        )

        current = []

        for i, text in enumerate(
            data["text"]
        ):

            value = money_value(text)

            if value is None:
                continue

            x = (
                data["left"][i]
                + 450
            )

            current.append({
                "value": value,
                "x": x,
                "y": procedure_y,
            })

        current.sort(
            key=lambda item: item["x"]
        )

        if len(current) > len(best):
            best = current

    return best


def assign_financial_columns(values):

    result = {
        field: None
        for field in FINANCIAL_FIELDS
    }

    # Expected approximate x positions.
    # The first value is Billed.
    #
    # If OCR misses a middle value, we use
    # x-position instead of shifting values
    # into the wrong column.

    x_ranges = {
        "billed_amount": (470, 620),
        "discount": (620, 760),
        "grt": (760, 850),
        "allowed_amount": (850, 990),
        "not_covered": (990, 1085),
        "other_cov": (1085, 1215),
        "deduc_copay_coins": (1215, 1350),
        "patient_resp": (1350, 1495),
        "payment": (1495, 1660),
    }

    for value in values:

        x = value["x"]

        for field, (
            lower,
            upper
        ) in x_ranges.items():

            if lower <= x < upper:

                if result[field] is None:

                    result[field] = value["value"]

                break

    return result


def extract_line(
    image,
    words,
    procedure
):

    coordinate_values = (
        get_coordinate_financials(
            words,
            procedure["y"]
        )
    )

    focused_values = (
        focused_financial_ocr(
            image,
            procedure["y"]
        )
    )

    # Combine both OCR sources.
    combined = (
        coordinate_values
        + focused_values
    )

    # Keep the first value found in each
    # approximate x-position.
    unique = []

    for value in combined:

        duplicate = False

        for existing in unique:

            if (
                abs(
                    existing["x"]
                    - value["x"]
                ) < 20
                and existing["value"]
                == value["value"]
            ):
                duplicate = True
                break

        if not duplicate:
            unique.append(value)

    unique.sort(
        key=lambda item: item["x"]
    )

    return assign_financial_columns(
        unique
    )


def main():

    print("\n========================================")
    print("MULTI-SERVICE-LINE EXTRACTION")
    print("========================================")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        original_records = json.load(file)

    review_records = []

    for page_number, block_number in sorted(
        CANDIDATES
    ):

        image_path = os.path.join(
            PAGE_FOLDER,
            f"page_{page_number:03d}.png"
        )

        if not os.path.exists(
            image_path
        ):
            continue

        image = Image.open(
            image_path
        )

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

        if block_number > len(blocks):
            continue

        block = blocks[
            block_number - 1
        ]

        procedures = get_procedures(
            block["words"]
        )

        if len(procedures) <= 1:
            continue

        # Find corresponding existing record.
        base_record = None

        for record in original_records:

            if (
                record.get("page_number")
                == page_number
                and
                record.get("block_number")
                == block_number
            ):

                base_record = record
                break

        if base_record is None:
            continue

        for line_number, procedure in enumerate(
            procedures,
            start=1
        ):

            financial = extract_line(
                image,
                block["words"],
                procedure
            )

            record = {
                "page_number": page_number,
                "block_number": block_number,
                "service_line": line_number,

                "patient":
                    base_record.get("patient"),

                "patient_number":
                    base_record.get(
                        "patient_number"
                    ),

                "service_dates":
                    base_record.get(
                        "service_dates"
                    ),

                "procedure_number":
                    procedure["code"],
            }

            record.update(
                financial
            )

            record["reason_codes"] = (
                base_record.get(
                    "reason_codes"
                )
            )

            review_records.append(
                record
            )

            print(
                f"\nPage {page_number} "
                f"Block {block_number} "
                f"Line {line_number}"
            )

            print(
                "Procedure:",
                procedure["code"]
            )

            for field in FINANCIAL_FIELDS:

                print(
                    f"  {field}: "
                    f"{financial[field]}"
                )

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
            review_records,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n========================================")
    print("MULTI-LINE EXTRACTION COMPLETE")
    print("========================================")

    print(
        "Service-line records generated:",
        len(review_records)
    )

    print(
        "Saved:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()