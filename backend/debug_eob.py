import pytesseract
from PIL import Image


IMAGE_PATH = "processed/pages/page_001.png"


def get_ocr_data():

    image = Image.open(IMAGE_PATH)

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


def find_claim_positions(words):

    positions = []

    for word in words:

        if (
            word["text"].lower() == "claim"
            and word["x"] < 300
        ):
            positions.append(word["y"])

    return sorted(set(positions))


def create_blocks(words, positions):

    blocks = []

    for i, start_y in enumerate(positions):

        if i + 1 < len(positions):
            end_y = positions[i + 1]

        else:
            end_y = max(w["y"] for w in words) + 100

        block_words = [
            w for w in words
            if start_y <= w["y"] < end_y
        ]

        blocks.append({
            "number": i + 1,
            "start": start_y,
            "end": end_y,
            "words": block_words
        })

    return blocks


def print_section(title, words):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)

    sorted_words = sorted(
        words,
        key=lambda w: (w["y"], w["x"])
    )

    for w in sorted_words:

        print(
            f"{w['text']:<25}"
            f" X={w['x']:<5}"
            f" Y={w['y']:<5}"
            f" CONF={w['confidence']:.1f}"
        )


def main():

    print("Reading page 1...")

    words = get_ocr_data()

    positions = find_claim_positions(words)

    blocks = create_blocks(
        words,
        positions
    )

    print(
        "\nDetected blocks:",
        len(blocks)
    )

    for block in blocks:

        start = block["start"]

        print(
            f"\n\n##############################"
        )

        print(
            f"BLOCK {block['number']}"
        )

        print(
            f"Y RANGE: {block['start']} -> {block['end']}"
        )

        print(
            f"##############################"
        )

        # Patient/header area
        header_words = [
            w for w in block["words"]
            if start + 20 <= w["y"] <= start + 130
        ]

        print_section(
            "PATIENT / HEADER AREA",
            header_words
        )

        # Service/financial area
        financial_words = [
            w for w in block["words"]
            if start + 200 <= w["y"] <= start + 330
        ]

        print_section(
            "SERVICE / FINANCIAL AREA",
            financial_words
        )


if __name__ == "__main__":
    main()