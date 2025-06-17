"""
Configuración y constantes del chatbot
"""

# URLs y configuración de servicios
SUPABASE_URL = "https://sevobuvdlkzqcbwfhzxq.supabase.com"
SUPABASE_TABLE = "conversaciones"

# Configuración del modelo
MODEL_NAME = "gpt-4.1"
MODEL_TEMPERATURE = 0
RETRIEVER_K = 3

# Configuración del streaming
STREAMING_DELAY = 0.05  # Segundos entre palabras

# Estilos CSS
CSS_STYLES = """
<style>
    .main-header {
        text-align: center;
        color: #d4af37;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: #000;
    }
    .user-message {
        background-color: #0066cc;
        color: white;
        border-left: 4px solid #004499;
    }
    .bot-message {
        background-color: #2d2d2d;
        color: white;
        border-left: 4px solid #d4af37;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    .mode-selector {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .analytics-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #d4af37;
        margin: 0.5rem 0;
    }
</style>
"""

# Configuración de modos
MODE_COLORS = {
    "ciudadano": "#4CAF50",
    "estudiante": "#2196F3", 
    "profesional": "#9C27B0"
}

MODE_NAMES = {
    "ciudadano": "👨‍👩‍👧‍👦 Ciudadano - Explicaciones simples y cercanas",
    "estudiante": "🎓 Estudiante - Respuestas pedagógicas y estructuradas", 
    "profesional": "⚖️ Profesional - Análisis jurídico técnico"
}

WELCOME_MESSAGES = {
    "ciudadano": "¡Hola! Soy tu asistente para entender la Constitución Española. Puedes preguntarme sobre tus derechos, cómo funciona el Estado, o cualquier duda que tengas sobre la Constitución. ¡Hablaré de forma sencilla y con ejemplos!",
    "estudiante": "¡Bienvenido! Soy tu profesor virtual de Derecho Constitucional. Estoy aquí para ayudarte a estudiar, preparar exámenes y entender a fondo la Constitución Española. Te daré explicaciones estructuradas y conectaré conceptos entre sí.",
    "profesional": "Saludos. Soy su consultor en Derecho Constitucional. Puedo asistirle con análisis jurídicos, interpretaciones doctrinales y cuestiones técnicas sobre la Constitución Española de 1978. Procederé con la precisión técnica que requiere su práctica profesional."
}