def extract_procedure(block_words, start_y):

    target_y = start_y + 265

    candidates = []

    for word in block_words:

        text = word["text"].strip()

        # Look for a 4-5 digit procedure code
        # anywhere inside the OCR text.
        matches = re.findall(r"\b\d{4,5}\b", text)

        if not matches:
            continue

        x = word["x"]
        distance = abs(word["y"] - target_y)

        # Procedure column
        if 250 <= x <= 520 and distance <= 50:

            for match in matches:
                candidates.append(
                    (distance, match)
                )

    if candidates:

        candidates.sort(
            key=lambda item: item[0]
        )

        return candidates[0][1]

    return None