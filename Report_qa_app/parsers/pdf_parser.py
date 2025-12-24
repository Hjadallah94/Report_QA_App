from typing import Tuple, List, Dict
import pdfplumber

# Optional OCR support. If `pytesseract` and `Pillow` are installed and
# a Tesseract binary is available, we'll attempt to OCR image regions
# to get text for caption detection. This is optional and failures are
# silently ignored so the parser still works without OCR.
try:
    from PIL import Image
    import pytesseract
    _OCR_AVAILABLE = True
except Exception:
    _OCR_AVAILABLE = False


def parse_pdf(file) -> Tuple[str, List[str], Dict]:
    """Return (full_text, paragraphs_list, meta).

    Meta currently includes `images`: a list of dicts with keys `page`,
    `bbox` and `nearby_text` when available. This helps downstream
    checks determine whether an image likely has a caption.
    """
    paras: List[str] = []
    texts = []
    images: List[Dict] = []
    with pdfplumber.open(file) as pdf:
        for pnum, page in enumerate(pdf.pages, start=1):
            t = page.extract_text() or ""
            if t.strip():
                texts.append(t.strip())

            # Collect image objects and nearby text words
            try:
                img_objs = page.images or []
            except Exception:
                img_objs = []
            if img_objs:
                # extract words with positioning to find nearby text
                words = page.extract_words() if hasattr(page, "extract_words") else []
                for img in img_objs:
                    x0 = img.get("x0")
                    x1 = img.get("x1")
                    top = img.get("top") or img.get("y0")
                    bottom = img.get("bottom") or img.get("y1")
                    # find words whose vertical span overlaps expanded bbox
                    nearby = []
                    below = []
                    for w in words:
                        try:
                            wy0 = float(w.get("top", 0))
                            wy1 = float(w.get("bottom", wy0))
                        except Exception:
                            wy0 = wy1 = 0
                        # expand vertical window by 30 units for nearby
                        if (wy1 >= (top - 30)) and (wy0 <= (bottom + 30)):
                            nearby.append(w.get("text", ""))
                        # words that are just below the image (within 80 units)
                        if (wy0 > bottom) and (wy0 <= (bottom + 80)):
                            below.append(w.get("text", ""))
                    img_entry = {
                        "page": pnum,
                        "bbox": (x0, top, x1, bottom),
                        "nearby_text": " ".join(nearby),
                        "below_text": " ".join(below),
                        "ocr_text": "",
                    }

                    # Attempt OCR of the image area when available
                    if _OCR_AVAILABLE:
                        try:
                            # Create a PIL image of the page and crop the bbox
                            page_image = page.to_image(resolution=150)
                            pil_img = page_image.original
                            # pdfplumber coordinates: x0, top, x1, bottom
                            # Ensure coordinates are integers and within image bounds
                            w, h = pil_img.size
                            left = max(0, int(x0 or 0))
                            upper = max(0, int(top or 0))
                            right = min(w, int(x1 or w))
                            lower = min(h, int(bottom or h))
                            if right > left and lower > upper:
                                crop = pil_img.crop((left, upper, right, lower))
                                try:
                                    ocr_text = pytesseract.image_to_string(crop)
                                    img_entry["ocr_text"] = (ocr_text or "").strip()
                                except Exception:
                                    # OCR failed for this image; continue without it
                                    pass
                        except Exception:
                            # Any page-image creation/cropping error should not break parsing
                            pass

                    images.append(img_entry)

    full = "\n\n".join(texts)
    # heuristic: split by double newline for paragraphs
    paras = [p.strip() for p in full.split("\n\n") if p.strip()]
    meta = {"images": images}
    return full, paras, meta