<<<<<<< HEAD
"""OCR using Tesseract. Pillow-only preprocessing (no OpenCV needed)."""
import os

from PIL import Image, ImageFilter, ImageOps

try:  # the app still opens (paste-text mode) if pytesseract is missing
    import pytesseract
except ImportError:
    pytesseract = None

# Windows: point to the Tesseract install if it is not on PATH
_WIN_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if pytesseract and os.name == "nt" and os.path.exists(_WIN_PATH):
    pytesseract.pytesseract.tesseract_cmd = _WIN_PATH

CONFIG = "--oem 3 --psm 6"


def preprocess(img: Image.Image) -> Image.Image:
    img = ImageOps.exif_transpose(img).convert("L")
    longest = max(img.size)
    if longest < 1600:  # upscale small photos so small print is readable
        scale = 1600 / longest
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    img = ImageOps.autocontrast(img)
    return img.filter(ImageFilter.SHARPEN)


def read_text(img: Image.Image):
    """Return (raw_text, average_confidence 0-100)."""
    if pytesseract is None:
        raise RuntimeError("pytesseract is not installed. Add 'pytesseract' to requirements.txt (and 'tesseract-ocr' to packages.txt), then redeploy.")
    proc = preprocess(img)
    text = pytesseract.image_to_string(proc, config=CONFIG)
    data = pytesseract.image_to_data(proc, config=CONFIG, output_type=pytesseract.Output.DICT)
    confs = [float(c) for w, c in zip(data["text"], data["conf"]) if w.strip() and float(c) >= 0]
    return text, (sum(confs) / len(confs) if confs else 0.0)
=======
"""OCR using Tesseract. Pillow-only preprocessing (no OpenCV needed)."""
import os

import pytesseract
from PIL import Image, ImageFilter, ImageOps

# Windows: point to the Tesseract install if it is not on PATH
_WIN_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.name == "nt" and os.path.exists(_WIN_PATH):
    pytesseract.pytesseract.tesseract_cmd = _WIN_PATH

CONFIG = "--oem 3 --psm 6"


def preprocess(img: Image.Image) -> Image.Image:
    img = ImageOps.exif_transpose(img).convert("L")
    longest = max(img.size)
    if longest < 1600:  # upscale small photos so small print is readable
        scale = 1600 / longest
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    img = ImageOps.autocontrast(img)
    return img.filter(ImageFilter.SHARPEN)


def read_text(img: Image.Image):
    """Return (raw_text, average_confidence 0-100)."""
    proc = preprocess(img)
    text = pytesseract.image_to_string(proc, config=CONFIG)
    data = pytesseract.image_to_data(proc, config=CONFIG, output_type=pytesseract.Output.DICT)
    confs = [float(c) for w, c in zip(data["text"], data["conf"]) if w.strip() and float(c) >= 0]
    return text, (sum(confs) / len(confs) if confs else 0.0)
>>>>>>> e5d2695 (LabelLens AI)
