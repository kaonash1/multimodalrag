import re 
import nltk
from nltk.corpus import words 

nltk.download('words')

def is_logo(ocr_text: str, expected: str) -> bool:

    valid_words = set(words.words())
    cleaned_text = re.sub(r"[@#&*\(\)]+", "", ocr_text)

    tokens = cleaned_text.slit()
    filtered_tokens = [word for word in tokens if word.lower() in valid_words or word.istitle()]

    final = " ".join(filtered_tokens)
    is_match = final.lower() == expected.lower()

    return is_match

def remove_logo(chunk):
    """
    Removes the logo based on the OCR extracted test
    Metadata elements are being updated, TODO chunk.text update (?)
    """
    elements = chunk.metadata.orig_elements

    chunk_images = [
        (i, el) for i, el in enumerate(elements)
        if el.category == 'Image'
    ]

    indices_to_remove = [img[0] for img in chunk_images if is_logo(img[1].text)]
    removed_ = []
    for idx in sorted(indices_to_remove, reverse = True):
        removed_.append(elements.pop(idx))
    
    return elements, removed_

