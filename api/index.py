from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import math
import re
import io
import statistics

app = FastAPI(title="AI Detector Pro API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
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
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            if not text.strip():
                raise HTTPException(status_code=422, detail="El PDF no contiene texto extraíble.")
            return text
    except ImportError:
        raise HTTPException(status_code=501, detail="Soporte de PDF no disponible en este entorno.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"No se pudo leer el PDF: {str(e)[:100]}")


def extract_text_from_docx(content: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    except ImportError:
        raise HTTPException(status_code=501, detail="Soporte de DOCX no disponible en este entorno.")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"No se pudo leer el DOCX: {str(e)[:100]}")


def extract_text_from_image(content: bytes) -> str:
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(io.BytesIO(content))
        return pytesseract.image_to_string(img)
    except ImportError:
        raise HTTPException(status_code=501, detail="OCR no disponible en este entorno. Sube un archivo de texto.")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"No se pudo leer la imagen: {str(e)[:100]}")


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
# MOTOR DE ANÁLISIS v2 (inspirado en GPTZero + Turnitin)
# ─────────────────────────────────────────────

# Lista expandida de "AI-isms" basada en investigación de GPTZero y corpus de LLMs
AI_MARKERS = [
    # Transiciones clásicas de IA
    "additionally", "furthermore", "moreover", "therefore", "consequently",
    "nevertheless", "notwithstanding", "henceforth", "heretofore",
    # Frases de relleno
    "it is worth noting", "it should be noted", "it is important to note",
    "it's important to note", "in conclusion", "in summary", "to summarize",
    "importantly", "significantly", "essentially", "fundamentally",
    "comprehensively", "notably", "remarkably", "undoubtedly",
    # Verbos "IA"
    "delve", "elucidate", "leverage", "underscore", "resonate", "unveil",
    "embark", "unleash", "navigate", "showcase", "foster", "cultivate",
    "harness", "streamline", "revolutionize", "empower", "facilitate",
    # Adjetivos "IA"
    "meticulous", "intricate", "comprehensive", "transformative", "vibrant",
    "pivotal", "crucial", "vital", "robust", "dynamic", "innovative",
    "cutting-edge", "state-of-the-art", "multifaceted", "nuanced",
    # Frases cliché de IA
    "in the realm of", "as we navigate", "by leveraging", "in the ever-evolving",
    "tapestry of", "at the pinnacle", "landscape of", "paradigm shift",
    "in today's fast-paced", "it goes without saying", "needless to say",
    "the bottom line is", "at the end of the day", "last but not least",
]


def calculate_perplexity_v2(text: str) -> float:
    """
    Perplejidad mejorada basada en diversidad léxica y densidad de marcadores de IA.
    Inspirada en el modelo de GPTZero.
    """
    words = text.lower().split()
    if not words:
        return 50.0

    # Diversidad léxica (Type-Token Ratio): más diversidad = más humano = más perplejidad
    unique_ratio = len(set(words)) / len(words)

    # Análisis de bigrams: IA repite combinaciones de palabras
    if len(words) > 1:
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        unique_bigrams_ratio = len(set(bigrams)) / len(bigrams)
    else:
        unique_bigrams_ratio = 1.0

    # Densidad de marcadores de IA
    text_lower = text.lower()
    marker_count = sum(1 for m in AI_MARKERS if m in text_lower)
    marker_density = marker_count / len(AI_MARKERS)

    # Perplejidad: más diversidad + menos marcadores = más perplejidad (más humano)
    perplexity = (unique_ratio * 45) + (unique_bigrams_ratio * 35) - (marker_density * 40) + 20
    return max(5.0, min(100.0, perplexity))


def calculate_burstiness_v2(text: str) -> float:
    """
    Burstiness real basada en coeficiente de variación de longitud de oraciones.
    Turnitin usa este método: humanos tienen picos, IA mantiene uniformidad.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.split()) > 1]

    if len(sentences) < 3:
        return 50.0

    lengths = [len(s.split()) for s in sentences]

    try:
        mean = statistics.mean(lengths)
        if mean == 0:
            return 50.0
        std = statistics.stdev(lengths)
        # Coeficiente de variación: alta variación = más humano = más burstiness
        cv = (std / mean) * 100
        return min(100.0, cv * 1.2)
    except Exception:
        return 50.0


def analyze_per_sentence(text: str) -> list:
    """
    Análisis oración por oración inspirado en el método de Turnitin.
    Cada oración recibe un score de 0 (humano) a 1 (IA).
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.split()) > 3][:20]  # Cap en 20

    scored = []
    text_lower = text.lower()
    for sentence in sentences:
        s_lower = sentence.lower()
        # Contar marcadores de IA en esta oración
        markers_in_sentence = sum(1 for m in AI_MARKERS if m in s_lower)
        # Uniformidad de longitud de palabras
        words = s_lower.split()
        avg_word_len = sum(len(w) for w in words) / max(len(words), 1)
        # Score IA: más marcadores + palabras largas uniformes = más IA
        ai_score = min(1.0, (markers_in_sentence * 0.3) + (max(0, avg_word_len - 4) * 0.07))
        scored.append({"sentence": sentence[:100], "ai_score": round(ai_score, 2)})

    return scored


def analyze_text(text: str) -> dict:
    perplexity = calculate_perplexity_v2(text)
    burstiness = calculate_burstiness_v2(text)

    words = text.lower().split()
    lexical_diversity = len(set(words)) / max(len(words), 1)

    # Marcadores encontrados
    text_lower = text.lower()
    found_markers = [m for m in AI_MARKERS if m in text_lower]

    # Scores normalizados (0=humano, 1=IA)
    perplexity_score = (100 - perplexity) / 100
    burstiness_score = (100 - burstiness) / 100
    pattern_score = min(len(found_markers) / 10, 1.0)
    diversity_score = 1 - lexical_diversity

    # Ponderación basada en investigación de GPTZero / Turnitin
    ai_prob = (
        perplexity_score * 0.35 +
        burstiness_score * 0.30 +
        pattern_score    * 0.20 +
        diversity_score  * 0.15
    ) * 100

    ai_prob = round(min(99.9, max(0.1, ai_prob)), 1)
    human_prob = round(100 - ai_prob, 1)

    # Nivel de confianza (como Turnitin)
    if ai_prob >= 80 or ai_prob <= 20:
        confidence = "Alta"
    elif ai_prob >= 65 or ai_prob <= 35:
        confidence = "Media"
    else:
        confidence = "Baja"

    sentence_scores = analyze_per_sentence(text)

    return {
        "ai_probability": ai_prob,
        "human_probability": human_prob,
        "confidence": confidence,
        "perplexity": round(perplexity, 1),
        "burstiness": round(burstiness, 1),
        "lexical_diversity": round(lexical_diversity * 100, 1),
        "patterns_found": found_markers[:8],  # Top 8 marcadores
        "humanizer_detected": len(found_markers) >= 4,
        "word_count": len(words),
        "sentence_count": len(re.split(r'(?<=[.!?])\s+', text.strip())),
        "sentence_analysis": sentence_scores,
    }


# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────

router = APIRouter()


@router.get("/")
def root():
    return {"status": "ok", "service": "AI Detector Pro API v2", "version": "2.0.0"}


@router.get("/health")
def health():
    return {"status": "ok", "service": "AI Detector Pro API v2"}


@router.get("/supported-formats")
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


@router.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    filename = file.filename or "unknown"
    extension = filename.split(".")[-1].lower() if "." in filename else ""

    if extension not in EXTRACTORS:
        raise HTTPException(
            status_code=415,
            detail=f"Formato '.{extension}' no soportado. Formatos válidos: {', '.join(EXTRACTORS.keys())}"
        )

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10 MB
        raise HTTPException(status_code=413, detail="Archivo demasiado grande. Máximo 10 MB.")

    text = EXTRACTORS[extension](content)

    if not text or not text.strip():
        raise HTTPException(status_code=422, detail="No se pudo extraer texto del archivo.")

    if len(text.split()) < 20:
        raise HTTPException(status_code=422, detail="Texto insuficiente (mínimo 20 palabras).")

    result = analyze_text(text)
    result["file_name"] = filename
    result["file_format"] = extension.upper()
    result["file_size_kb"] = round(len(content) / 1024, 2)

    return result


# Registrar rutas — Vercel hace el routing via vercel.json rewrites
app.include_router(router)
