import json
import re


INPUT_FILE = "exports/final_eob_data.json"


def money(value):

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    text = (
        text
        .replace("$", "")
        .replace(",", "")
        .replace(" ", "")
    )

    try:
        return float(text)
    except ValueError:
        return None


def check_record(record):

    billed = money(record.get("billed_amount"))
    discount = money(record.get("discount"))
    allowed = money(record.get("allowed_amount"))
    not_covered = money(record.get("not_covered"))
    other_cov = money(record.get("other_cov"))
    patient_resp = money(record.get("patient_resp"))
    payment = money(record.get("payment"))

    if billed is None or discount is None or payment is None:
        return None

    # Basic claim/payment relationship.
    expected_payment = billed - discount

    difference = round(
        payment - expected_payment,
        2
    )

    return {
        "billed": billed,
        "discount": discount,
        "allowed": allowed,
        "not_covered": not_covered,
        "other_cov": other_cov,
        "patient_resp": patient_resp,
        "payment": payment,
        "expected_payment": expected_payment,
        "difference": difference
    }


def main():

    print("\n========================================")
    print("FINANCIAL MATH AUDIT")
    print("========================================")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        records = json.load(file)

    flagged = []

    for record in records:

        result = check_record(record)

        if result is None:
            continue

        difference = result["difference"]

        # Ignore normal zero/tiny rounding differences.
        if abs(difference) >= 0.01:

            flagged.append(
                (
                    record,
                    result
                )
            )

    print(
        "Final records:",
        len(records)
    )

    print(
        "Financial math exceptions:",
        len(flagged)
    )

    print("\n========================================")

    for record, result in flagged:

        print("\n----------------------------------------")

        print(
            f"Page {record.get('page_number')} "
            f"Block {record.get('block_number')} "
            f"Line {record.get('service_line', 1)}"
        )

        print(
            "Patient:",
            record.get("patient")
        )

        print(
            "Procedure:",
            record.get("procedure_number")
        )

        print(
            "Billed:",
            record.get("billed_amount")
        )

        print(
            "Discount:",
            record.get("discount")
        )

        print(
            "Allowed:",
            record.get("allowed_amount")
        )

        print(
            "Not Covered:",
            record.get("not_covered")
        )

        print(
            "Other Cov:",
            record.get("other_cov")
        )

        print(
            "Patient Resp:",
            record.get("patient_resp")
        )

        print(
            "Payment:",
            record.get("payment")
        )

        print(
            "Billed - Discount:",
            f"${result['expected_payment']:,.2f}"
        )

        print(
            "Difference:",
            f"${result['difference']:,.2f}"
        )

    print("\n========================================")
    print("AUDIT COMPLETE")
    print("========================================")


if __name__ == "__main__":
    main()