import pytesseract
from PIL import Image


IMAGE_PATH = "processed/pages/page_001.png"


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


def find_claim_positions(words):

    claim_positions = []

    for word in words:

        text = word["text"].lower()

        # Claim label normally appears on the left side
        if text == "claim" and word["x"] < 300:

            claim_positions.append(word["y"])

    return sorted(set(claim_positions))


def create_blocks(words, claim_positions):

    blocks = []

    for index, start_y in enumerate(claim_positions):

        if index + 1 < len(claim_positions):
            end_y = claim_positions[index + 1]
        else:
            end_y = max(word["y"] for word in words) + 100

        block_words = []

        for word in words:

            if start_y <= word["y"] < end_y:
                block_words.append(word)

        blocks.append({
            "block_number": index + 1,
            "start_y": start_y,
            "end_y": end_y,
            "words": block_words
        })

    return blocks


def print_blocks(blocks):

    print("\n======================================")
    print("EOB BLOCK DETECTION")
    print("======================================\n")

    print("Total EOB blocks:", len(blocks))

    for block in blocks:

        print("\n--------------------------------------")
        print(
            f"BLOCK {block['block_number']} "
            f"(Y: {block['start_y']} -> {block['end_y']})"
        )
        print("--------------------------------------")

        for word in block["words"]:
            print(
                f"{word['text']:<25} "
                f"x={word['x']:<5} "
                f"y={word['y']:<5} "
                f"conf={word['confidence']:.1f}"
            )


def main():

    print("Reading page 1...")

    words = get_ocr_data(IMAGE_PATH)

    print("Total OCR words:", len(words))

    claim_positions = find_claim_positions(words)

    print("\nClaim positions found:", claim_positions)

    blocks = create_blocks(
        words,
        claim_positions
    )

    print_blocks(blocks)


if __name__ == "__main__":
    main()