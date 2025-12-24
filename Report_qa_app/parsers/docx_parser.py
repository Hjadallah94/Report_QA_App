from typing import Tuple, List, Dict
from docx import Document


def parse_docx(file) -> Tuple[str, List[str], Dict]:
    """Return (full_text, paragraphs_list, meta).

    DOCX parsing currently returns paragraphs; image extraction is
    non-trivial for all DOCX variants, so `meta` will be returned
    (empty by default) to keep the API consistent with PDF parser.
    """
    doc = Document(file)
    paras = []
    for p in doc.paragraphs:
        txt = (p.text or "").strip()
        if txt:
            paras.append(txt)
    full_text = "\n\n".join(paras)
    meta: Dict = {"images": []}
    return full_text, paras, meta