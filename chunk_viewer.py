import pymupdf
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from PIL import Image

import base64
from IPython.display import Image as Imagep, display as displayp

from llama_index.core import Document


def plot_pdf_with_boxes(pdf_image, segments):
    pix = pdf_image.get_pixmap()
    pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    fig, ax = plt.subplots(1, figsize = (10, 10))
    ax.imshow(pil_image)
    categories = set()
    category_to_color = {
        "Title": "orchid",
        "Image": "forestgreen",
        "Table": "tomato"
    }

    for segment in segments:
        points = segment["coordinates"]["points"]
        layout_width = segment["coordinates"]["layout_width"]
        layout_height = segment["coordinates"]["layout_height"]
        scaled_points = [
            (x * pix.width / layout_width, y * pix.height / layout_height)
            for x, y in points
        ]
        box_color = category_to_color.get(segment['category'], 'deepskyblue')
        categories.add(segment['category'])
        rect = patches.Polygon(
            scaled_points, linewidth = 1, edgecolor = box_color, facecolor = "none"
        )
        ax.add_patch(rect)
    
    #Make Legend 
    legend_handles = [patches.Patch(color = 'deepskyblue', label = "Text")]
    for category in ["Title", "Image", "Table"]:
        if category in categories:
            legend_handles.append(
                patches.Patch(color=category_to_color[category], label = category)
            )
    ax.axis('off')
    ax.legend(handles=legend_handles, loc = "upper right")
    plt.tight_layout()
    plt.show()

def render_page(file_path: str, doc_list: list, page_number: int, print_text = True) -> None:
    pdf_page = pymupdf.open(file_path).load_page(page_number - 1)
    page_docs = [
        doc for doc in doc_list if doc.metadata.get('page_number') == page_number
    ]
    segments = [doc.metadata for doc in page_docs]

    plot_pdf_with_boxes(pdf_page, segments)
    if print_text:
        for doc in page_docs:
            print(f"{doc.page_content}\n")

def extract_page_numbers_from_chunk(chunk):
    elements = chunk.metadata.orig_elements

    page_numbers = set()
    for element in elements:
        page_numbers.add(element.metadata.page_number)

    return page_numbers

def display_chunk_pages(file_path:str, chunk):
    page_numbers = extract_page_numbers_from_chunk(chunk)

    docs = []
    for element in chunk.metadata.orig_elements:
        metadata = element.metadata.to_dict()
        if "Table" in str(type(element)):
            metadata["category"] = "Table"
        elif "Image" in str(type(element)):
            metadata["category"] = "Image"
        else:
            metadata["category"] = "Text"
        metadata["page_number"] = int(element.metadata.page_number)

        docs.append(Document(text=element.text, metadata=metadata))
    
    for page_number in page_numbers:
        render_page(file_path, docs, page_number, False)

#display_chunk_pages(chunks[5])


def chunk_composition(chunks):
    for i, chunk in enumerate(chunks):
        if "CompositeElement" in str(type(chunk)):
            print("\n\nChunk", i)
            for doc in chunk.metadata.orig_elements:
                print(doc.to_dict()["type"], doc.metadata.page_number)


def get_images_base64(chunks):
    images_b64 = []
    for chunk in chunks: 
        if "CompositeElement" in str(type(chunk)):
            chunk_els = chunk.metadata.orig_elements
            for el in chunk_els:
                if el.category == 'Image':
                    images_b64.append(el.metadata.image_base64)
                if (el.category == 'Table') and hasattr(el.metadata, 'image_base64'):
                    images_b64.append(el.metadata.image_base64)
    return images_b64

def display_base64_image(base64_code):
    image_data = base64.b64decode(base64_code)
    displayp(Imagep(data = image_data))