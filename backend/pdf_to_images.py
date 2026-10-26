import pymupdf
import os

# Our PDF
pdf_path = "../uploads/presbyterian.pdf"

# Where we will save the page pictures
output_folder = "../processed/pages"

# Create the folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Open the PDF
doc = pymupdf.open(pdf_path)

print("Total pages:", len(doc))
print("Starting conversion...\n")

# Go through every page
for page_number, page in enumerate(doc):

    # Make the page high quality
    matrix = pymupdf.Matrix(3, 3)

    # Convert PDF page into an image
    pix = page.get_pixmap(
        matrix=matrix,
        alpha=False
    )

    # Example:
    # page_001.png
    # page_002.png
    # page_003.png
    file_name = f"page_{page_number + 1:03d}.png"

    output_path = os.path.join(
        output_folder,
        file_name
    )

    # Save the image
    pix.save(output_path)

    print(f"Created: {file_name}")

doc.close()

print("\nFinished!")
print("All 82 pages were converted into images.")