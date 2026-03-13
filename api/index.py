from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import textwrap
import math
import re
import io

app = FastAPI(title="AI Detector Pro API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción se reemplaza con el dominio de Render
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# UTILIDADES DE EXTRACCIÓN DE TEXTO
# ─────────────────────────────────────────────

def extract_text_from_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore")


def extract_text_from_pdf(content: bytes) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(
                page.extract_text() or "" for page in pdf.pages
            )
    except Exception:
        raise HTTPException(status_code=422, detail="No se pudo leer el PDF. Instala pdfplumber.")


def extract_text_from_docx(content: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        raise HTTPException(status_code=422, detail="No se pudo leer el DOCX. Instala python-docx.")


def extract_text_from_image(content: bytes) -> str:
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(io.BytesIO(content))
        return pytesseract.image_to_string(img)
    except Exception:
        raise HTTPException(status_code=422, detail="No se pudo leer la imagen. Instala pytesseract y Pillow.")


EXTRACTORS = {
    "txt": extract_text_from_txt,
    "md": extract_text_from_txt,
    "py": extract_text_from_txt,
    "js": extract_text_from_txt,
    "ts": extract_text_from_txt,
    "jsx": extract_text_from_txt,
    "tsx": extract_text_from_txt,
    "html": extract_text_from_txt,
    "css": extract_text_from_txt,
    "json": extract_text_from_txt,
    "csv": extract_text_from_txt,
    "pdf": extract_text_from_pdf,
    "docx": extract_text_from_docx,
    "jpg": extract_text_from_image,
    "jpeg": extract_text_from_image,
    "png": extract_text_from_image,
    "webp": extract_text_from_image,
}


# ─────────────────────────────────────────────
# MOTOR DE ANÁLISIS DE IA
# ─────────────────────────────────────────────

def calculate_perplexity(text: str) -> float:
    """
    Aproximación heurística de perplejidad basada en proporción
    de palabras comunes de 'relleno' en textos de IA.
    """
    ai_filler_words = [
        "additionally", "furthermore", "moreover", "therefore", "consequently",
        "nevertheless", "notwithstanding", "henceforth", "heretofore",
        "it is worth noting", "it should be noted", "in conclusion",
        "in summary", "to summarize", "importantly", "significantly",
        "essentially", "fundamentally", "comprehensively", "delve", "elucidate",
        "in the realm of", "as we navigate", "by leveraging",
    ]
    words = text.lower().split()
    if len(words) == 0:
        return 50.0
    filler_count = sum(1 for w in ai_filler_words if w in text.lower())
    # Perplejidad baja → texto más predecible → más IA
    base = 80.0 - (filler_count * 8)
    return max(10.0, min(100.0, base))


def calculate_burstiness(text: str) -> float:
    """
    Calcula la variabilidad en longitud de oraciones.
    Baja variabilidad = IA (oraciones uniformes).
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if len(sentences) < 2:
        return 50.0
    lengths = [len(s.split()) for s in sentences if len(s.split()) > 0]
    if not lengths:
        return 50.0
    mean_len = sum(lengths) / len(lengths)
    variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
    std_dev = math.sqrt(variance)
    # Normalizar: std_dev alta → burstiness alta → más humano
    return min(100.0, std_dev * 4)


def detect_ai_patterns(text: str) -> dict:
    """Detecta patrones específicos de escritura IA."""
    ai_patterns = [
        r"\bdelve\b", r"\bcomprehensive\b", r"\bin conclusion\b",
        r"\bit is important to note\b", r"\bfurthermore\b",
        r"\badditionally,\b", r"\bmoreover\b", r"\bnevertheless\b",
        r"\bin summary\b", r"\bto summarize\b",
    ]
    found = [p for p in ai_patterns if re.search(p, text.lower())]
    return {
        "patterns_found": len(found),
        "patterns": [p.strip(r'\b') for p in found[:5]],
    }


def analyze_text(text: str) -> dict:
    perplexity = calculate_perplexity(text)
    burstiness = calculate_burstiness(text)
    patterns = detect_ai_patterns(text)

    # Calcular probabilidad de IA (0-100)
    # Perplejidad baja + burstiness baja + muchos patrones → alta prob IA
    perplexity_score = (100 - perplexity) / 100  # Mayor si baja perplejidad
    burstiness_score = (100 - burstiness) / 100  # Mayor si baja variabilidad
    pattern_score = min(patterns["patterns_found"] / 5, 1.0)

    ai_prob = (perplexity_score * 0.4 + burstiness_score * 0.35 + pattern_score * 0.25) * 100
    ai_prob = round(min(99.9, max(0.1, ai_prob)), 1)
    human_prob = round(100 - ai_prob, 1)

    humanizer_detected = patterns["patterns_found"] >= 3

    return {
        "ai_probability": ai_prob,
        "human_probability": human_prob,
        "perplexity": round(perplexity, 1),
        "burstiness": round(burstiness, 1),
        "patterns_found": patterns["patterns"],
        "humanizer_detected": humanizer_detected,
        "word_count": len(text.split()),
        "sentence_count": len(re.split(r'(?<=[.!?])\s+', text.strip())),
    }


# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "AI Detector Pro API"}


@app.get("/supported-formats")
def supported_formats():
    return {
        "formats": list(EXTRACTORS.keys()),
        "categories": {
            "text": ["txt", "md"],
            "code": ["py", "js", "ts", "jsx", "tsx", "html", "css", "json", "csv"],
            "documents": ["pdf", "docx"],
            "images": ["jpg", "jpeg", "png", "webp"],
        }
    }


@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    filename = file.filename or "unknown"
    extension = filename.split(".")[-1].lower() if "." in filename else ""

    if extension not in EXTRACTORS:
        raise HTTPException(
            status_code=415,
            detail=f"Formato '.{extension}' no soportado. Formatos válidos: {', '.join(EXTRACTORS.keys())}"
        )

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=413, detail="Archivo demasiado grande. Máximo 10 MB.")

    text = EXTRACTORS[extension](content)

    if not text.strip():
        raise HTTPException(status_code=422, detail="No se pudo extraer texto del archivo.")

    if len(text.split()) < 20:
        raise HTTPException(status_code=422, detail="El archivo tiene muy poco texto para analizar (mínimo 20 palabras).")

    result = analyze_text(text)
    result["file_name"] = filename
    result["file_format"] = extension.upper()
    result["file_size_kb"] = round(len(content) / 1024, 2)

    return result
