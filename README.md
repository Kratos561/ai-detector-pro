# AI Detector Pro 🤖

Detecta contenido generado por Inteligencia Artificial en cualquier tipo de archivo.

## Stack Tecnológico

- **Frontend:** React + Vite + TailwindCSS v4 + Framer Motion
- **Backend:** Python FastAPI
- **Deploy:** Render (Static Site + Web Service) vía GitHub CI/CD

## Estructura del Proyecto

```
ai-detector-pro/
├── frontend/              # React + Vite app
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   └── package.json
├── backend/               # Python FastAPI
│   ├── main.py
│   └── requirements.txt
└── README.md
```

## Formatos Soportados

| Categoría  | Formatos |
|------------|---------|
| Texto      | .txt, .md |
| Código     | .py, .js, .ts, .jsx, .tsx, .html, .css, .json, .csv |
| Documentos | .pdf, .docx |
| Imágenes   | .jpg, .jpeg, .png, .webp (via OCR) |

## Cómo correr localmente

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```

## Variables de Entorno

| Variable | Descripción |
|----------|-------------|
| `VITE_API_URL` | URL del backend (frontend) |

## Deploy en Render

El proyecto se despliega automáticamente en cada push a `main`.

- **Backend Web Service:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Frontend Static Site:** Build `npm run build`, publish `dist/`
