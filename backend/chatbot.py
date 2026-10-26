import json
import re


DATA_FILE = "exports/final_eob_data.json"


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# MONEY CONVERSION
# ============================================================

def money(value):

    if value is None:
        return 0.0

    value = str(value).strip()

    value = value.replace("$", "")
    value = value.replace(",", "")

    try:
        return float(value)

    except ValueError:
        return 0.0


# ============================================================
# OVERALL SUMMARY
# ============================================================

def show_summary(records):

    total_billed = sum(
        money(record.get("billed_amount"))
        for record in records
    )

    total_allowed = sum(
        money(record.get("allowed_amount"))
        for record in records
    )

    total_payment = sum(
        money(record.get("payment"))
        for record in records
    )

    print("\n========================================")
    print("          EOB DATA SUMMARY")
    print("========================================")

    print(
        "Total records:",
        len(records)
    )

    print(
        f"Total billed:  ${total_billed:,.2f}"
    )

    print(
        f"Total allowed: ${total_allowed:,.2f}"
    )

    print(
        f"Total payment: ${total_payment:,.2f}"
    )

    print("========================================\n")


# ============================================================
# SEARCH PATIENT
# ============================================================

def search_patient(records, name):

    results = []

    for record in records:

        patient = str(
            record.get(
                "patient",
                ""
            )
        ).lower()

        if name.lower() in patient:

            results.append(record)

    return results


# ============================================================
# SHOW PATIENT DETAILS
# ============================================================

def show_patient_results(results):

    print(
        f"\nBot: Found {len(results)} record(s).\n"
    )

    for record in results:

        print("----------------------------------------")

        print(
            "Patient:",
            record.get("patient")
        )

        print(
            "Patient #:",
            record.get("patient_number")
        )

        print(
            "Service Date:",
            record.get("service_dates")
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
            "Allowed:",
            record.get("allowed_amount")
        )

        print(
            "Payment:",
            record.get("payment")
        )

        print(
            "Patient Responsibility:",
            record.get("patient_resp")
        )

        print(
            "Reason Codes:",
            record.get("reason_codes")
        )

    print()


# ============================================================
# PATIENT PAYMENT
# ============================================================

def patient_total_payment(results):

    total = 0.0

    for record in results:

        total += money(
            record.get("payment")
        )

    return total


# ============================================================
# PATIENT PROCEDURES
# ============================================================

def patient_procedures(results):

    procedures = set()

    for record in results:

        procedure = record.get(
            "procedure_number"
        )

        if procedure:

            procedures.add(
                str(procedure)
            )

    return sorted(procedures)


# ============================================================
# PATIENT REASON CODES
# ============================================================

def patient_reason_codes(results):

    procedure_codes = {}

    for record in results:

        procedure = str(
            record.get(
                "procedure_number",
                "Unknown"
            )
        )

        reason_codes = record.get(
            "reason_codes"
        )

        if procedure not in procedure_codes:

            procedure_codes[procedure] = []

        if reason_codes:

            reason_codes = str(
                reason_codes
            ).strip()

            if reason_codes not in procedure_codes[procedure]:

                procedure_codes[procedure].append(
                    reason_codes
                )

    return procedure_codes


# ============================================================
# PROCEDURE COUNT
# ============================================================

def procedure_count(records, procedure):

    count = 0

    for record in records:

        record_procedure = str(
            record.get(
                "procedure_number",
                ""
            )
        )

        if record_procedure == procedure:

            count += 1

    return count


# ============================================================
# EXTRACT PATIENT NAME
# ============================================================

def extract_patient_name(question):

    q = question.lower().strip()

    # --------------------------------------------------------
    # "for Robert M Adams"
    # --------------------------------------------------------

    match = re.search(
        r"(?:for|of|patient)\s+"
        r"([a-z]+(?:\s+[a-z]+){1,4})",
        q
    )

    if match:

        return match.group(1).strip()

    # --------------------------------------------------------
    # "does Robert M Adams have"
    # --------------------------------------------------------

    match = re.search(
        r"(?:does|do)\s+"
        r"([a-z]+(?:\s+[a-z]+){1,4})\s+"
        r"(?:have|has)",
        q
    )

    if match:

        return match.group(1).strip()

    # --------------------------------------------------------
    # "How much is Robert M Adams responsible for?"
    # --------------------------------------------------------

    match = re.search(
        r"how much is\s+"
        r"([a-z]+(?:\s+[a-z]+){1,4})\s+"
        r"responsible for",
        q
    )

    if match:

        return match.group(1).strip()

    # --------------------------------------------------------
    # "What procedures did Robert M Adams have?"
    # --------------------------------------------------------

    match = re.search(
        r"what\s+procedures?\s+did\s+"
        r"([a-z]+(?:\s+[a-z]+){1,4})\s+"
        r"have",
        q
    )

    if match:

        return match.group(1).strip()

    return None


# ============================================================
# ANSWER QUESTION
# ============================================================

def answer_question(records, question):

    q = question.lower().strip()

    # ========================================================
    # PATIENT QUESTIONS
    # ========================================================

    possible_name = extract_patient_name(q)

    if possible_name:

        results = search_patient(
            records,
            possible_name
        )

        if not results:

            print(
                f"\nBot: No patient found for "
                f"'{possible_name}'."
            )

            return

        patient_name = results[0].get(
            "patient",
            possible_name
        )

        # ----------------------------------------------------
        # REASON CODES
        # ----------------------------------------------------

        if (
            "reason code" in q
            or "reason codes" in q
        ):

            reason_data = patient_reason_codes(
                results
            )

            print(
                f"\nBot: Reason codes for "
                f"{patient_name}:"
            )

            for procedure, codes in reason_data.items():

                print(
                    f"\nProcedure {procedure}:"
                )

                if not codes:

                    print(
                        "  No reason codes"
                    )

                else:

                    for code in codes:

                        print(
                            f"  {code}"
                        )

            print()

            return

        # ----------------------------------------------------
        # PROCEDURES
        # ----------------------------------------------------

        if "procedure" in q:

            procedures = patient_procedures(
                results
            )

            print(
                f"\nBot: Procedures for "
                f"{patient_name}: "
                f"{', '.join(procedures)}"
            )

            return

        # ----------------------------------------------------
        # TOTAL BILLED
        # ----------------------------------------------------

        if "billed" in q:

            total = sum(
                money(
                    record.get(
                        "billed_amount"
                    )
                )
                for record in results
            )

            print(
                f"\nBot: Total billed amount "
                f"for {patient_name}: "
                f"${total:,.2f}"
            )

            return

        # ----------------------------------------------------
        # TOTAL ALLOWED
        # ----------------------------------------------------

        if "allowed" in q:

            total = sum(
                money(
                    record.get(
                        "allowed_amount"
                    )
                )
                for record in results
            )

            print(
                f"\nBot: Total allowed amount "
                f"for {patient_name}: "
                f"${total:,.2f}"
            )

            return

        # ----------------------------------------------------
        # PATIENT RESPONSIBILITY
        # ----------------------------------------------------

        if (
            "responsible" in q
            or "responsibility" in q
        ):

            total = sum(
                money(
                    record.get(
                        "patient_resp"
                    )
                )
                for record in results
            )

            print(
                f"\nBot: Total patient "
                f"responsibility for "
                f"{patient_name}: "
                f"${total:,.2f}"
            )

            return

        # ----------------------------------------------------
        # TOTAL PAYMENT
        # ----------------------------------------------------

        if (
            "payment" in q
            or "paid" in q
        ):

            total = patient_total_payment(
                results
            )

            print(
                f"\nBot: Total payment "
                f"for {patient_name}: "
                f"${total:,.2f}"
            )

            return

        # ----------------------------------------------------
        # CLAIM COUNT
        # ----------------------------------------------------

        if (
            "how many" in q
            or "claims" in q
            or "records" in q
        ):

            print(
                f"\nBot: {patient_name} has "
                f"{len(results)} record(s)."
            )

            return

        # ----------------------------------------------------
        # DEFAULT PATIENT DETAILS
        # ----------------------------------------------------

        show_patient_results(
            results
        )

        return

    # ========================================================
    # PROCEDURE COUNT
    # ========================================================

    procedure_match = re.search(
        r"\b\d{5}\b",
        q
    )

    if (
        procedure_match
        and (
            "how many" in q
            or "count" in q
        )
    ):

        procedure = procedure_match.group()

        count = procedure_count(
            records,
            procedure
        )

        print(
            f"\nBot: Procedure {procedure} "
            f"appears in {count} record(s)."
        )

        return

    # ========================================================
    # OVERALL TOTAL PAYMENT
    # ========================================================

    if "total payment" in q:

        total = sum(
            money(
                record.get("payment")
            )
            for record in records
        )

        print(
            f"\nBot: Total payment: "
            f"${total:,.2f}"
        )

        return

    # ========================================================
    # OVERALL TOTAL ALLOWED
    # ========================================================

    if "total allowed" in q:

        total = sum(
            money(
                record.get(
                    "allowed_amount"
                )
            )
            for record in records
        )

        print(
            f"\nBot: Total allowed amount: "
            f"${total:,.2f}"
        )

        return

    # ========================================================
    # OVERALL TOTAL BILLED
    # ========================================================

    if "total billed" in q:

        total = sum(
            money(
                record.get(
                    "billed_amount"
                )
            )
            for record in records
        )

        print(
            f"\nBot: Total billed amount: "
            f"${total:,.2f}"
        )

        return

    # ========================================================
    # UNKNOWN QUESTION
    # ========================================================

    print(
        "\nBot: I couldn't understand "
        "that question."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("========================================")
    print("       AI INSURANCE EOB CHATBOT")
    print("========================================")

    records = load_data()

    print(
        f"Loaded {len(records)} "
        f"EOB service-line records."
    )

    show_summary(records)

    while True:

        question = input(
            "You: "
        ).strip()

        if question.lower() in [
            "exit",
            "quit"
        ]:

            print(
                "Chatbot closed."
            )

            break

        if question.lower() == "summary":

            show_summary(
                records
            )

            continue

        answer_question(
            records,
            question
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()