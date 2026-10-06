"""OCR engine. Tries Tesseract first; if the Tesseract program is missing on the
server, falls back to RapidOCR (pure pip install, no system package needed)."""

import os

from PIL import Image, ImageFilter, ImageOps

try:
    import pytesseract
except ImportError:
    pytesseract = None

# Windows: point to the Tesseract install if it is not on PATH.
_WIN_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if pytesseract and os.name == "nt" and os.path.exists(_WIN_PATH):
    pytesseract.pytesseract.tesseract_cmd = _WIN_PATH

CONFIG = "--oem 3 --psm 6"
_rapid = None


def preprocess(img: Image.Image) -> Image.Image:
    img = ImageOps.exif_transpose(img).convert("L")
    longest = max(img.size)
    if longest < 1600:
        scale = 1600 / longest
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    img = ImageOps.autocontrast(img)
    return img.filter(ImageFilter.SHARPEN)


def _read_tesseract(proc):
    text = pytesseract.image_to_string(proc, config=CONFIG)
    data = pytesseract.image_to_data(proc, config=CONFIG, output_type=pytesseract.Output.DICT)
    confs = [float(c) for w, c in zip(data["text"], data["conf"]) if w.strip() and float(c) >= 0]
    return text, (sum(confs) / len(confs) if confs else 0.0)


def _read_rapid(img: Image.Image):
    global _rapid
    import numpy as np
    from rapidocr_onnxruntime import RapidOCR

    if _rapid is None:
        _rapid = RapidOCR()
    arr = np.array(ImageOps.exif_transpose(img).convert("RGB"))
    result, _ = _rapid(arr)
    if not result:
        return "", 0.0
    # group boxes into lines by vertical position, then read left to right
    items = sorted(((b[0][1], b[0][0], t, float(s)) for b, t, s in result))
    lines, cur, last_y = [], [], None
    for y, x, t, s in items:
        if last_y is not None and abs(y - last_y) > 18:
            lines.append(cur)
            cur = []
        cur.append((x, t, s))
        last_y = y
    if cur:
        lines.append(cur)
    text = "\n".join(" ".join(t for _, t, _ in sorted(line)) for line in lines)
    conf = sum(s for line in lines for _, _, s in line) / sum(len(line) for line in lines) * 100
    return text, conf


def read_text(img: Image.Image):
    """Return (raw_text, average_confidence 0-100)."""
    tesseract_error = None

    if pytesseract is not None:
        try:
            return _read_tesseract(preprocess(img))
        except Exception as e:  # Tesseract program missing or failed
            tesseract_error = e

    try:
        return _read_rapid(img)
    except ImportError:
        raise RuntimeError(
            "No OCR engine is available. Install the Tesseract program, or add "
            "'rapidocr-onnxruntime' to requirements.txt. "
            f"(Tesseract error: {tesseract_error})"
        )