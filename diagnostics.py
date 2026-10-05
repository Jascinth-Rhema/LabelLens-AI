"""System check: shows exactly why OCR might not work (missing package, missing Tesseract, bad requirements.txt)."""
import importlib.util
import shutil
import sys
from pathlib import Path


def _read_text(path: Path):
    raw = path.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="ignore"), "UTF-16 (WRONG: re-save as UTF-8, e.g. edit it on the GitHub website)"
    if raw[:3] == b"\xef\xbb\xbf":
        return raw.decode("utf-8-sig", errors="ignore"), "UTF-8 with BOM (usually ok)"
    return raw.decode("utf-8", errors="ignore"), "UTF-8 (ok)"


def run():
    base = Path(__file__).parent
    rows = [("Python version", sys.version.split()[0])]
    for mod in ("pytesseract", "rapidocr_onnxruntime", "rapidfuzz", "PIL", "pandas"):
        rows.append((f"Package: {mod}", "installed" if importlib.util.find_spec(mod) else "MISSING"))
    rows.append(("Tesseract program", shutil.which("tesseract") or "NOT FOUND"))
    for name in ("requirements.txt", "packages.txt", "data/ingredients.csv"):
        rows.append((f"File: {name}", "found" if (base / name).exists() else "NOT FOUND"))
    req = base / "requirements.txt"
    if req.exists():
        text, enc = _read_text(req)
        rows.append(("requirements.txt encoding", enc))
        rows.append(("requirements.txt lists pytesseract", "yes" if "pytesseract" in text.lower() else "NO"))
    pk = base / "packages.txt"
    if pk.exists():
        text, _ = _read_text(pk)
        rows.append(("packages.txt lists tesseract-ocr", "yes" if "tesseract-ocr" in text.lower() else "NO"))
    return rows


def advice(rows):
    d = dict(rows)
    if d.get("File: requirements.txt") == "NOT FOUND":
        return "requirements.txt is not next to app.py in the repo. Create it at the top level of the repository."
    if "UTF-16" in d.get("requirements.txt encoding", ""):
        return "requirements.txt is saved as UTF-16, so Streamlit cannot read it. Re-create it on the GitHub website."
    if d.get("requirements.txt lists pytesseract") == "NO":
        return "requirements.txt does not contain pytesseract. Add the line 'pytesseract' and reboot the app."
    if d.get("Package: pytesseract") == "MISSING":
        return "pytesseract is listed but not installed. Reboot the app (Manage app > Reboot) and check the logs for install errors."
    if d.get("Tesseract program") == "NOT FOUND":
        return "pytesseract is installed but the Tesseract program is missing. Create packages.txt (tesseract-ocr, tesseract-ocr-eng) at the top level and reboot."
    return "OCR setup looks fine."