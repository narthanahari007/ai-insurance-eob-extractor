import json
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


INPUT_FILE = "exports/final_eob_data.json"
OUTPUT_FILE = "exports/insurance_eob_extracted.xlsx"


MAIN_COLUMNS = [
    "Patient",
    "Patient #:",
    "Service Dates",
    "Procedure No:",
    "Billed Amount",
    "Discount",
    "Allowed Amount",
    "Not Covered",
    "Other Cov",
    "Deduc/Copay/Coins",
    "Patient Resp.",
    "Payment",
    "Reason Codes",
    "Note",
]


def money_to_number(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return value

    value = str(value).strip()

    if not value:
        return None

    negative = value.startswith("-")

    value = (
        value
        .replace("$", "")
        .replace(",", "")
        .strip()
    )

    try:
        number = float(value)

        if negative:
            number = -abs(number)

        return number

    except ValueError:
        return None


def main():

    print("\n========================================")
    print("CREATING INSURANCE EOB EXCEL")
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

    print("Records loaded:", len(records))

    workbook = Workbook()

    # ==================================================
    # SHEET 1 - EOB DATA
    # ==================================================

    ws = workbook.active
    ws.title = "EOB Data"

    for column_number, column_name in enumerate(
        MAIN_COLUMNS,
        start=1
    ):

        cell = ws.cell(
            row=1,
            column=column_number,
            value=column_name
        )

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.fill = PatternFill(
            "solid",
            fgColor="1F4E78"
        )

        cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    for record in records:

        note_parts = []

        if record.get("status") == "REVIEW":
            note_parts.append("Review required")

        validation_issues = record.get(
            "validation_issues"
        )

        if validation_issues:
            note_parts.append(
                str(validation_issues)
            )

        financial_fields = [
            "billed_amount",
            "discount",
            "allowed_amount",
            "not_covered",
            "other_cov",
            "deduc_copay_coins",
            "patient_resp",
            "payment",
        ]

        missing_financial = [
            field
            for field in financial_fields
            if record.get(field) is None
        ]

        if missing_financial:

            note_parts.append(
                "Missing financial fields: "
                + ", ".join(missing_financial)
            )

        note = " | ".join(note_parts)

        row = [
            record.get("patient"),
            record.get("patient_number"),
            record.get("service_dates"),
            record.get("procedure_number"),
            money_to_number(
                record.get("billed_amount")
            ),
            money_to_number(
                record.get("discount")
            ),
            money_to_number(
                record.get("allowed_amount")
            ),
            money_to_number(
                record.get("not_covered")
            ),
            money_to_number(
                record.get("other_cov")
            ),
            money_to_number(
                record.get("deduc_copay_coins")
            ),
            money_to_number(
                record.get("patient_resp")
            ),
            money_to_number(
                record.get("payment")
            ),
            record.get("reason_codes"),
            note,
        ]

        ws.append(row)

    # Currency formatting
    currency_columns = [
        5, 6, 7, 8, 9, 10, 11, 12
    ]

    for row in ws.iter_rows(
        min_row=2,
        max_row=ws.max_row
    ):

        for column_number in currency_columns:

            cell = row[column_number - 1]

            if cell.value is not None:
                cell.number_format = '$#,##0.00;-$#,##0.00'

    # Borders
    thin_border = Border(
        left=Side(style="thin", color="D9E1F2"),
        right=Side(style="thin", color="D9E1F2"),
        top=Side(style="thin", color="D9E1F2"),
        bottom=Side(style="thin", color="D9E1F2"),
    )

    for row in ws.iter_rows():

        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(
                vertical="center"
            )

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    # Column widths
    widths = {
        "A": 25,
        "B": 16,
        "C": 25,
        "D": 15,
        "E": 16,
        "F": 14,
        "G": 16,
        "H": 15,
        "I": 14,
        "J": 20,
        "K": 16,
        "L": 14,
        "M": 24,
        "N": 45,
    }

    for column, width in widths.items():
        ws.column_dimensions[column].width = width

    ws.row_dimensions[1].height = 30

    # ==================================================
    # SHEET 2 - REVIEW
    # ==================================================

    review_ws = workbook.create_sheet(
        "Review"
    )

    review_columns = [
        "Page",
        "Block",
        "Patient",
        "Patient #",
        "Missing Financial Fields",
        "Status",
    ]

    for column_number, column_name in enumerate(
        review_columns,
        start=1
    ):

        cell = review_ws.cell(
            row=1,
            column=column_number,
            value=column_name
        )

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.fill = PatternFill(
            "solid",
            fgColor="C55A11"
        )

        cell.alignment = Alignment(
            horizontal="center"
        )

    financial_fields = [
        "billed_amount",
        "discount",
        "allowed_amount",
        "not_covered",
        "other_cov",
        "deduc_copay_coins",
        "patient_resp",
        "payment",
    ]

    review_count = 0

    for record in records:

        missing = [
            field
            for field in financial_fields
            if record.get(field) is None
        ]

        if not missing:
            continue

        review_ws.append([
            record.get("page_number"),
            record.get("block_number"),
            record.get("patient"),
            record.get("patient_number"),
            ", ".join(missing),
            "MANUAL REVIEW",
        ])

        review_count += 1

    review_ws.freeze_panes = "A2"
    review_ws.auto_filter.ref = review_ws.dimensions

    review_widths = {
        "A": 10,
        "B": 10,
        "C": 25,
        "D": 16,
        "E": 60,
        "F": 20,
    }

    for column, width in review_widths.items():
        review_ws.column_dimensions[column].width = width

    # ==================================================
    # SHEET 3 - VALIDATION SUMMARY
    # ==================================================

    summary_ws = workbook.create_sheet(
        "Validation Summary"
    )

    summary = [
        ("Metric", "Value"),
        ("Total EOB Records", len(records)),
        (
            "OK Records",
            sum(
                1
                for r in records
                if r.get("status") == "OK"
            )
        ),
        (
            "REVIEW Records",
            sum(
                1
                for r in records
                if r.get("status") == "REVIEW"
            )
        ),
        (
            "Records With Missing Financial Fields",
            review_count
        ),
        ("PDF Pages", 82),
        (
            "Pages With Extracted Records",
            len(
                set(
                    r.get("page_number")
                    for r in records
                )
            )
        ),
        ("Pages Without Extracted Records", "80, 81, 82"),
        ("Previously Observed Service Lines", 210),
        ("Current Extracted EOB Blocks", len(records)),
    ]

    for row_number, row_data in enumerate(
        summary,
        start=1
    ):

        for column_number, value in enumerate(
            row_data,
            start=1
        ):

            cell = summary_ws.cell(
                row=row_number,
                column=column_number,
                value=value
            )

            cell.border = thin_border

            if row_number == 1:

                cell.font = Font(
                    bold=True,
                    color="FFFFFF"
                )

                cell.fill = PatternFill(
                    "solid",
                    fgColor="548235"
                )

    summary_ws.column_dimensions["A"].width = 40
    summary_ws.column_dimensions["B"].width = 30

    # ==================================================
    # SHEET 4 - SOURCE TRACEABILITY
    # ==================================================

    source_ws = workbook.create_sheet(
        "Source Traceability"
    )

    source_columns = [
        "Page",
        "Block",
        "Patient",
        "Patient #",
        "Procedure",
        "Source Status",
    ]

    for column_number, column_name in enumerate(
        source_columns,
        start=1
    ):

        cell = source_ws.cell(
            row=1,
            column=column_number,
            value=column_name
        )

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.fill = PatternFill(
            "solid",
            fgColor="4472C4"
        )

    for record in records:

        source_ws.append([
            record.get("page_number"),
            record.get("block_number"),
            record.get("patient"),
            record.get("patient_number"),
            record.get("procedure_number"),
            record.get("status"),
        ])

    for column in ["A", "B"]:
        source_ws.column_dimensions[column].width = 10

    source_ws.column_dimensions["C"].width = 25
    source_ws.column_dimensions["D"].width = 16
    source_ws.column_dimensions["E"].width = 15
    source_ws.column_dimensions["F"].width = 15

    source_ws.freeze_panes = "A2"
    source_ws.auto_filter.ref = source_ws.dimensions

    # ==================================================
    # SAVE
    # ==================================================

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    workbook.save(OUTPUT_FILE)

    print("\n========================================")
    print("EXCEL CREATION COMPLETE")
    print("========================================")

    print("Total records:", len(records))
    print("Review records:", review_count)
    print("Output:", OUTPUT_FILE)


if __name__ == "__main__":
    main()