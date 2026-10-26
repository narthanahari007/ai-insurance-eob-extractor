import pytesseract
from PIL import Image
import re


IMAGE_PATH = "processed/pages/page_001.png"


# --------------------------------------------------
# 1. OCR
# --------------------------------------------------

def get_ocr_data(image_path):

    image = Image.open(image_path)

    data = pytesseract.image_to_data(
        image,
        lang="eng",
        config="--psm 3",
        output_type=pytesseract.Output.DICT
    )

    words = []

    for i in range(len(data["text"])):

        text = data["text"][i].strip()

        if not text:
            continue

        confidence = float(data["conf"][i])

        if confidence < 30:
            continue

        words.append({
            "text": text,
            "confidence": confidence,
            "x": data["left"][i],
            "y": data["top"][i],
            "width": data["width"][i],
            "height": data["height"][i]
        })

    return words


# --------------------------------------------------
# 2. Find CLAIM positions
# --------------------------------------------------

def find_claim_positions(words):

    positions = []

    for word in words:

        if (
            word["text"].lower() == "claim"
            and word["x"] < 300
        ):
            positions.append(word["y"])

    return sorted(set(positions))


# --------------------------------------------------
# 3. Create EOB blocks
# --------------------------------------------------

def create_blocks(words, claim_positions):

    blocks = []

    for index, start_y in enumerate(claim_positions):

        if index + 1 < len(claim_positions):
            end_y = claim_positions[index + 1]

        else:
            end_y = max(
                word["y"]
                for word in words
            ) + 100

        block_words = [
            word
            for word in words
            if start_y <= word["y"] < end_y
        ]

        blocks.append({
            "block_number": index + 1,
            "start_y": start_y,
            "end_y": end_y,
            "words": block_words
        })

    return blocks


# --------------------------------------------------
# 4. Patient
# --------------------------------------------------

def extract_patient(block_words, start_y):

    # -----------------------------------------
    # Method 1: Use normal full-page OCR
    # -----------------------------------------

    patient_label = None

    for word in block_words:

        if (
            word["text"].lower().startswith("patient")
            and word["x"] < 150
            and start_y + 20 <= word["y"] <= start_y + 60
        ):
            patient_label = word
            break

    if patient_label:

        patient_y = patient_label["y"]

        candidates = []

        for word in block_words:

            same_line = abs(
                word["y"] - patient_y
            ) <= 15

            right_side = (
                word["x"] >
                patient_label["x"] + 150
            )

            reasonable_x = word["x"] < 600

            if (
                same_line
                and right_side
                and reasonable_x
            ):
                candidates.append(word)

        candidates.sort(
            key=lambda w: w["x"]
        )

        if candidates:

            result = " ".join(
                word["text"]
                for word in candidates
            )

            # Clean OCR punctuation/noise.
            result = re.sub(
                r"[^A-Za-z\s.'-]",
                " ",
                result
            )

            # Convert punctuation between name parts
            # into spaces.
            result = re.sub(
                r"[-:]+",
                " ",
                result
            )

            # Fix OCR such as "MAdams" -> "M Adams"
            result = re.sub(
                r"\b([A-Z])([A-Z][a-z]+)\b",
                r"\1 \2",
                result
            )

            result = re.sub(
                r"\s+",
                " ",
                result
            ).strip()

            if len(result.split()) >= 2:
                return result


    # -----------------------------------------
    # Method 2: Focused OCR fallback
    # -----------------------------------------

    try:

        from PIL import Image
        import pytesseract

        image = Image.open(IMAGE_PATH)

        crop = image.crop(
            (
                200,
                start_y,
                750,
                start_y + 90
            )
        )

        text = pytesseract.image_to_string(
            crop,
            lang="eng",
            config="--psm 6"
        )

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        for line in lines:

            if not re.search(
                r"[A-Za-z]",
                line
            ):
                continue

            # Keep only letters and spaces.
            cleaned = re.sub(
                r"[^A-Za-z\s]",
                " ",
                line
            )

            # Fix OCR such as "MAdams".
            cleaned = re.sub(
                r"\b([A-Z])([A-Z][a-z]+)\b",
                r"\1 \2",
                cleaned
            )

            cleaned = re.sub(
                r"\s+",
                " ",
                cleaned
            ).strip()

            if len(cleaned.split()) >= 2:
                return cleaned

    except Exception:
        pass

    return None

# --------------------------------------------------
# 5. Patient Number
# --------------------------------------------------

def extract_patient_number(block_words, start_y):

    # Find the "Patient #" label
    patient_label = None

    for word in block_words:

        text = word["text"].lower().replace("#", "").strip()

        if text == "patient" and word["x"] > 800:
            patient_label = word
            break

    # ---------------------------------------------------------
    # Method 1: Normal OCR
    # ---------------------------------------------------------

    if patient_label:

        label_y = patient_label["y"]

        candidates = []

        for word in block_words:

            same_line = abs(
                word["y"] - label_y
            ) <= 10

            right_side = (
                word["x"] > patient_label["x"]
            )

            if same_line and right_side:

                text = word["text"].strip()

                if re.fullmatch(
                    r"\d{6,12}",
                    text
                ):
                    candidates.append(word)

        if candidates:

            candidates.sort(
                key=lambda w: w["x"]
            )

            return candidates[0]["text"]

        # Backup search around the label
        for word in block_words:

            text = word["text"].strip()

            if re.fullmatch(
                r"\d{6,12}",
                text
            ):

                distance = abs(
                    word["y"] - label_y
                )

                if distance <= 30:

                    return text

    # ---------------------------------------------------------
    # Method 2: Focused OCR fallback
    # ---------------------------------------------------------

    if IMAGE_PATH:

        try:

            image = Image.open(IMAGE_PATH)

            if patient_label:

                crop_y = patient_label["y"]

            else:

                crop_y = start_y + 100

            crop = image.crop(
                (
                    750,
                    crop_y - 60,
                    1550,
                    crop_y + 100
                )
            )

            focused_text = pytesseract.image_to_string(
                crop,
                lang="eng",
                config="--psm 6"
            )

            numbers = re.findall(
                r"\b\d{6,12}\b",
                focused_text
            )

            if numbers:

                return numbers[0]

        except Exception as error:

            print(
                "Focused patient number OCR failed:",
                error
            )

    return None

# --------------------------------------------------
# 6. Service Dates
# --------------------------------------------------

def extract_service_dates(
    block_words,
    start_y
):

    target_y = start_y + 265

    candidates = []

    for word in block_words:

        same_line = abs(
            word["y"] - target_y
        ) <= 20

        correct_area = (
            40 <= word["x"] <= 280
        )

        if same_line and correct_area:

            candidates.append(word)

    candidates.sort(
        key=lambda w: w["x"]
    )

    if not candidates:
        return None

    text = " ".join(
        word["text"]
        for word in candidates
    )

    dates = re.findall(
        r"\d{2}/\d{2}/\d{2}",
        text
    )

    if len(dates) >= 2:

        return f"{dates[0]}- {dates[1]}"

    if len(dates) == 1:

        return dates[0]

    return None

# --------------------------------------------------
# 7. Procedure Number
# --------------------------------------------------

def extract_procedure(block_words, start_y):

    target_y = start_y + 265

    candidates = []

    # -----------------------------------------
    # Method 1: Normal OCR
    # -----------------------------------------

    for word in block_words:

        text = word["text"].strip()

        matches = re.findall(
            r"\d{4,5}",
            text
        )

        if not matches:
            continue

        x = word["x"]

        distance = abs(
            word["y"] - target_y
        )

        if (
            250 <= x <= 600
            and distance <= 50
        ):

            for match in matches:
                candidates.append(
                    (
                        distance,
                        match
                    )
                )

    if candidates:

        candidates.sort(
            key=lambda item: item[0]
        )

        return candidates[0][1]

    # -----------------------------------------
    # Method 2: Focused OCR fallback
    # -----------------------------------------

    try:

        from PIL import Image
        import pytesseract

        image = Image.open(IMAGE_PATH)

        crop = image.crop(
            (
                240,
                start_y + 230,
                520,
                start_y + 310
            )
        )

        for psm in [6, 11, 12]:

            text = pytesseract.image_to_string(
                crop,
                lang="eng",
                config=f"--psm {psm}"
            )

            matches = re.findall(
                r"\b\d{4,5}\b",
                text
            )

            for match in matches:

                # Procedure codes in our document
                # are in the procedure column.
                if match.startswith(("99", "98", "97")):
                    return match

    except Exception:
        pass

    return None

# --------------------------------------------------
# 8. Money helper
# --------------------------------------------------

def is_money(text):

    text = text.strip()

    text = text.replace(
        ",",
        ""
    )

    text = text.replace(
        " ",
        ""
    )

    return bool(
        re.fullmatch(
            r"-?\$?\d+\.\d{2}",
            text
        )
    )


# --------------------------------------------------
# 9. Extract money
# --------------------------------------------------

def extract_money(
    block_words,
    start_y,
    x_min,
    x_max
):

    target_y = start_y + 265

    candidates = []

    for word in block_words:

        same_line = abs(
            word["y"] - target_y
        ) <= 15

        correct_column = (
            x_min <= word["x"] <= x_max
        )

        if (
            same_line
            and correct_column
            and is_money(word["text"])
        ):

            candidates.append(word)

    if not candidates:
        return None

    candidates.sort(
        key=lambda w:
        abs(w["y"] - target_y)
    )

    return candidates[0]["text"]


# --------------------------------------------------
# 10. Reason Codes
# --------------------------------------------------

def extract_reason_codes(
    block_words,
    start_y
):

    target_y = start_y + 265

    codes = []

    # ---------------------------------------------------------
    # STEP 1: Coordinate-based OCR
    # ---------------------------------------------------------

    for word in block_words:

        same_line = abs(
            word["y"] - target_y
        ) <= 25

        correct_area = (
            1640 <= word["x"] <= 1800
        )

        if not (
            same_line
            and correct_area
        ):
            continue

        text = word["text"].strip()

        parts = re.split(
            r"[,;]+",
            text
        )

        for part in parts:

            part = part.strip(
                " .:-,;()[]|"
            )

            if re.fullmatch(
                r"[A-Za-z]?\d{1,4}",
                part
            ):

                if part not in codes:
                    codes.append(part)

    # ---------------------------------------------------------
    # STEP 2: Focused OCR only for alphabetic codes
    # ---------------------------------------------------------

    if IMAGE_PATH:

        try:

            image = Image.open(
                IMAGE_PATH
            )

            crop = image.crop(
                (
                    1580,
                    start_y + 270,
                    1850,
                    start_y + 330
                )
            )

            focused_text = pytesseract.image_to_string(
                crop,
                lang="eng",
                config="--psm 6"
            )

            # Only look for codes that contain
            # a letter, such as:
            # B7
            # N257
            # N287

            extra_codes = re.findall(
                r"\b[A-Za-z]\d{1,4}\b",
                focused_text
            )

            for code in extra_codes:

                code = code.upper()

                if code not in codes:

                    codes.append(code)

        except Exception as error:

            print(
                "Focused reason code OCR failed:",
                error
            )

    if not codes:
        return None

    return ", ".join(codes)
#------------------------------------------------
# extract financial row
# ------------------------------------------------ 

def extract_financial_row(block_words, start_y):

    # ---------------------------------------------------------
    # STEP 1: Try coordinate-based OCR
    # ---------------------------------------------------------

    target_y = start_y + 265

    money_values = []

    for word in block_words:

        text = word["text"].strip()

        # Financial values must contain $
        # This prevents values such as 45.23 from
        # being incorrectly treated as money.
        if "$" not in text:
            continue

        cleaned = text.replace(",", ".")
        cleaned = cleaned.rstrip(".,:")

        if not re.fullmatch(
            r"-?\$?\d+\.\d{2}",
            cleaned
        ):
            continue

        distance = abs(word["y"] - target_y)

        if distance <= 25:

            money_values.append({
                "text": cleaned,
                "x": word["x"],
                "y": word["y"],
                "distance": distance
            })

    money_values.sort(
        key=lambda item: item["x"]
    )

    # If coordinate OCR found all 9 columns,
    # this is the preferred result.
    if len(money_values) >= 9:

        return money_values[:9]

    # ---------------------------------------------------------
    # STEP 2: Focused OCR fallback
    # ---------------------------------------------------------

    if not IMAGE_PATH:
        return money_values

    try:

        image = Image.open(IMAGE_PATH)

        # Financial section of the EOB block.
        # Use a wider area because financial rows can
        # move slightly between pages.
        crop = image.crop(
            (
                400,
                start_y + 210,
                1850,
                start_y + 350
            )
        )

        best_values = []

        # Try several OCR layouts.
        for psm in [3, 6, 7, 11, 12]:

            focused_text = pytesseract.image_to_string(
                crop,
                lang="eng",
                config=f"--psm {psm}"
            )

            # Look through every OCR line.
            for line in focused_text.splitlines():

                line = line.strip()

                if not line:
                    continue

                # Extract only values that contain $.
                candidates = re.findall(
                    r"-?\$\s*\d+(?:[.,]\d{2})",
                    line
                )

                cleaned_values = []

                for value in candidates:

                    value = value.replace(" ", "")
                    value = value.replace(",", ".")
                    value = value.rstrip(".,:")

                    if re.fullmatch(
                        r"-?\$\d+\.\d{2}",
                        value
                    ):
                        cleaned_values.append(value)

                # Keep the line containing the largest
                # number of financial values.
                if len(cleaned_values) > len(best_values):

                    best_values = cleaned_values

        # -----------------------------------------------------
        # STEP 3: Return focused OCR result
        # -----------------------------------------------------

        if len(best_values) >= 9:

            return [
                {
                    "text": value,
                    "x": None,
                    "y": None,
                    "distance": None
                }
                for value in best_values[:9]
            ]

    except Exception as error:

        print(
            "Focused financial OCR failed:",
            error
        )

    # If fallback also failed, return whatever
    # coordinate OCR managed to find.
    return money_values
# --------------------------------------------------
# 11. Extract complete block
# --------------------------------------------------

def extract_block(block, image_path=None):

    words = block["words"]
    start_y = block["start_y"]

    global IMAGE_PATH

    if image_path:
        IMAGE_PATH = image_path

    # ---------------------------------------------------------
    # Extract complete financial row
    # ---------------------------------------------------------

    financial_values = extract_financial_row(
        words,
        start_y
    )

    # ---------------------------------------------------------
    # Convert financial list into named fields
    # ---------------------------------------------------------

    financial = {

        "billed_amount":
            financial_values[0]["text"]
            if len(financial_values) > 0
            else None,

        "discount":
            financial_values[1]["text"]
            if len(financial_values) > 1
            else None,

        "grt":
            financial_values[2]["text"]
            if len(financial_values) > 2
            else None,

        "allowed_amount":
            financial_values[3]["text"]
            if len(financial_values) > 3
            else None,

        "not_covered":
            financial_values[4]["text"]
            if len(financial_values) > 4
            else None,

        "other_cov":
            financial_values[5]["text"]
            if len(financial_values) > 5
            else None,

        "deduc_copay_coins":
            financial_values[6]["text"]
            if len(financial_values) > 6
            else None,

        "patient_resp":
            financial_values[7]["text"]
            if len(financial_values) > 7
            else None,

        "payment":
            financial_values[8]["text"]
            if len(financial_values) > 8
            else None
    }

    # ---------------------------------------------------------
    # Build complete EOB record
    # ---------------------------------------------------------

    record = {

        "patient":
            extract_patient(
                words,
                start_y
            ),

        "patient_number":
            extract_patient_number(
                words,
                start_y
            ),

        "service_dates":
            extract_service_dates(
                words,
                start_y
            ),

        "procedure_number":
            extract_procedure(
                words,
                start_y
            ),

        "billed_amount":
            financial["billed_amount"],

        "discount":
            financial["discount"],

        "grt":
            financial["grt"],

        "allowed_amount":
            financial["allowed_amount"],

        "not_covered":
            financial["not_covered"],

        "other_cov":
            financial["other_cov"],

        "deduc_copay_coins":
            financial["deduc_copay_coins"],

        "patient_resp":
            financial["patient_resp"],

        "payment":
            financial["payment"],

        "reason_codes":
            extract_reason_codes(
                words,
                start_y
            )
    }

    return record
# --------------------------------------------------
# 12. MAIN PROGRAM
# --------------------------------------------------

def main():

    print("Reading page 1...")

    words = get_ocr_data(
        IMAGE_PATH
    )

    print(
        "OCR words:",
        len(words)
    )

    claim_positions = (
        find_claim_positions(words)
    )

    print(
        "Claim positions:",
        claim_positions
    )

    blocks = create_blocks(
        words,
        claim_positions
    )

    print(
        "Detected blocks:",
        len(blocks)
    )

    print(
        "\n=============================="
    )

    print(
        "EXTRACTED RECORDS"
    )

    print(
        "=============================="
    )

    for block in blocks:

        print(
            f"\nBLOCK {block['block_number']}"
        )

        record = extract_block(
            block
        )

        for field, value in record.items():

            print(
                f"{field}: {value}"
            )


# --------------------------------------------------
# 13. START PROGRAM
# --------------------------------------------------

if __name__ == "__main__":
    main()