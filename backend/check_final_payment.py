import json


INPUT_FILE = "exports/final_eob_data.json"
SOURCE_TOTAL = 21375.83


def money_to_float(value):

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = (
        value
        .replace("$", "")
        .replace(",", "")
        .strip()
    )

    try:
        return float(value)

    except ValueError:
        return None


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as file:

    records = json.load(file)


total_payment = 0.0
missing_payment = []

for record in records:

    payment = money_to_float(
        record.get("payment")
    )

    if payment is None:

        missing_payment.append(record)

    else:

        total_payment += payment


difference = total_payment - SOURCE_TOTAL


print("\n========================================")
print("FINAL PAYMENT RECONCILIATION")
print("========================================")

print(
    "Final service-line records:",
    len(records)
)

print(
    "Extracted Payment Total:",
    f"${total_payment:,.2f}"
)

print(
    "Missing Payment Values:",
    len(missing_payment)
)

print(
    "Previously Observed Source Total:",
    f"${SOURCE_TOTAL:,.2f}"
)

print(
    "Difference:",
    f"${difference:,.2f}"
)


if missing_payment:

    print("\nRecords still missing Payment:")

    for record in missing_payment:

        print(
            f"Page {record.get('page_number')} "
            f"Block {record.get('block_number')} "
            f"Line {record.get('service_line', 1)} "
            f"| {record.get('patient')} "
            f"| Procedure {record.get('procedure_number')}"
        )


print("\n========================================")
print("RECONCILIATION COMPLETE")
print("========================================")