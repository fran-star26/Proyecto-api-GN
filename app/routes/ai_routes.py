from fastapi import APIRouter, Form, HTTPException, Depends
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Cargar las variables de entorno (tu API Key del .env)
load_dotenv()

# ============================================================================
# CONFIGURACIÓN DE GEMINI
# ============================================================================

try:
    # Configurar el cliente de Gemini
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
    if not gemini_api_key:
        raise RuntimeError("GOOGLE_API_KEY no encontrada. Asegúrate de que tu archivo .env esté correcto.")
    
    genai.configure(api_key=gemini_api_key)

    # Configuración del modelo
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1024,
    }

    # Esta es la variable que tu main.py intenta importar para el health check
    gemini_client = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config
    )
    
except Exception as e:
    print(f"Error al configurar Gemini: {e}")
    gemini_client = None

# ============================================================================
# DEFINICIÓN DEL ROUTER
# ============================================================================

# Este router será importado por main.py
router = APIRouter()

# ============================================================================
# ENDPOINTS DE IA (AQUÍ ESTÁ LA LÓGICA)
# ============================================================================

@router.post(
    "/ai/chat",
    response_description="Respuesta del chatbot de Gemini",
    tags=["IA - Chat"],
)
async def chat(message: str = Form(...)):
    """
    Recibe un mensaje (con contexto) de la app, lo envía a Gemini y devuelve la respuesta.
    Esta es la ruta que tu app está llamando.
    """
    if gemini_client is None:
        raise HTTPException(status_code=500, detail="El cliente de Gemini no está inicializado.")

    try:
        # Imprime en tu terminal de uvicorn para que veas qué recibe
        print(f"Recibido prompt para Gemini: {message[:150]}...") 

        # Enviar el prompt a Gemini
        response = gemini_client.generate_content(message)
        chat_response = response.text
        
        # Imprime en tu terminal lo que va a responder
        print(f"Respuesta de Gemini: {chat_response[:150]}...")

        # Devolver la respuesta a la app de Android
        return {
            "response": chat_response,
            "status": "success"
            # Tu app espera un campo "response", así que esto funcionará.
        }
        
    except Exception as e:
        print(f"Error al procesar el chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- PLACEHOLDERS PARA OTRAS RUTAS DE IA ---
# Agregamos funciones vacías para las otras rutas que tu main.py
# espera, para que la app no se rompa si las llama.

@router.post("/ai/analyze-text", tags=["IA - Análisis"])
async def analyze_text(text: str = Form(...)):
    return {"message": "Endpoint /ai/analyze-text aún no implementado"}

@router.post("/ai/analyze-image", tags=["IA - Análisis"])
async def analyze_image():
    return {"message": "Endpoint /ai/analyze-image aún no implementado"}

@router.post("/ai/analyze-document", tags=["IA - Análisis"])
async def analyze_document():
    return {"message": "Endpoint /ai/analyze-document aún no implementado"}