import json
from collections import Counter


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


def main():

    print("\n========================================")
    print("PAYMENT SOURCE RECONCILIATION")
    print("========================================")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        records = json.load(file)

    total_payment = 0.0
    positive_payment = 0.0
    negative_payment = 0.0
    zero_payment = 0.0

    total_billed = 0.0
    total_allowed = 0.0
    total_other_cov = 0.0
    total_patient_resp = 0.0

    positive_count = 0
    negative_count = 0
    zero_count = 0

    procedure_counts = Counter()

    print(
        "Records:",
        len(records)
    )

    for record in records:

        payment = money(
            record.get("payment")
        )

        billed = money(
            record.get("billed_amount")
        )

        allowed = money(
            record.get("allowed_amount")
        )

        other_cov = money(
            record.get("other_cov")
        )

        patient_resp = money(
            record.get("patient_resp")
        )

        procedure = record.get(
            "procedure_number"
        )

        if procedure:
            procedure_counts[procedure] += 1

        if payment is not None:

            total_payment += payment

            if payment > 0:

                positive_payment += payment
                positive_count += 1

            elif payment < 0:

                negative_payment += payment
                negative_count += 1

            else:

                zero_payment += payment
                zero_count += 1

        if billed is not None:
            total_billed += billed

        if allowed is not None:
            total_allowed += allowed

        if other_cov is not None:
            total_other_cov += other_cov

        if patient_resp is not None:
            total_patient_resp += patient_resp

    print("\n----------------------------------------")
    print("PAYMENT BREAKDOWN")
    print("----------------------------------------")

    print(
        "Positive payments:",
        f"${positive_payment:,.2f}",
        f"({positive_count} records)"
    )

    print(
        "Negative payments:",
        f"${negative_payment:,.2f}",
        f"({negative_count} records)"
    )

    print(
        "Zero payments:",
        f"${zero_payment:,.2f}",
        f"({zero_count} records)"
    )

    print(
        "Net payment:",
        f"${total_payment:,.2f}"
    )

    print("\n----------------------------------------")
    print("OTHER FINANCIAL TOTALS")
    print("----------------------------------------")

    print(
        "Total billed:",
        f"${total_billed:,.2f}"
    )

    print(
        "Total allowed:",
        f"${total_allowed:,.2f}"
    )

    print(
        "Total Other Cov:",
        f"${total_other_cov:,.2f}"
    )

    print(
        "Total Patient Resp.:",
        f"${total_patient_resp:,.2f}"
    )

    print("\n----------------------------------------")
    print("PROCEDURE COUNTS")
    print("----------------------------------------")

    for procedure, count in sorted(
        procedure_counts.items()
    ):

        print(
            procedure,
            ":",
            count
        )

    print("\n----------------------------------------")
    print("SOURCE COMPARISON")
    print("----------------------------------------")

    source_total = 21375.83

    print(
        "Extracted net payment:",
        f"${total_payment:,.2f}"
    )

    print(
        "Previously observed source total:",
        f"${source_total:,.2f}"
    )

    print(
        "Remaining difference:",
        f"${total_payment - source_total:,.2f}"
    )

    print("\n========================================")
    print("RECONCILIATION COMPLETE")
    print("========================================")


if __name__ == "__main__":
    main()