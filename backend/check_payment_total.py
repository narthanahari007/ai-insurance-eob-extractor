import json

INPUT_FILE = "exports/extracted_eobs.json"

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
missing_payment = 0
invalid_payment = 0


for record in records:

    payment = money_to_float(
        record.get("payment")
    )

    if payment is None:

        missing_payment += 1
        continue

    total_payment += payment


difference = total_payment - SOURCE_TOTAL


print("\n========================================")
print("PAYMENT TOTAL RECONCILIATION")
print("========================================")

print(
    "Total records:",
    len(records)
)

print(
    "Extracted Payment Total:",
    f"${total_payment:,.2f}"
)

print(
    "Missing Payment Values:",
    missing_payment
)

print(
    "Previously Observed Source Total:",
    f"${SOURCE_TOTAL:,.2f}"
)

print(
    "Difference:",
    f"${difference:,.2f}"
)

print("\n========================================")
print("RECONCILIATION COMPLETE")
print("========================================")