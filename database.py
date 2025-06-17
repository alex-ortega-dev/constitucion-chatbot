"""
Gestión de la base de datos Supabase
"""

import streamlit as st
import os
import pandas as pd
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_TABLE

"""
Gestión de la base de datos Supabase
"""

import streamlit as st
import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
from config import SUPABASE_URL, SUPABASE_TABLE

# Forzar carga del .env
load_dotenv()

@st.cache_resource
def init_supabase():
    """
    Inicializar cliente de Supabase
    
    Returns:
        Client: Cliente de Supabase o None si hay error
    """
    # Forzar carga del .env otra vez
    load_dotenv()
    
    key = os.getenv("SUPABASE_KEY")
    
    if not key:
        st.error("❌ SUPABASE_KEY no encontrada en variables de entorno")
        return None
    
    try:
        supabase: Client = create_client(SUPABASE_URL, key)
        return supabase
    except Exception as e:
        st.error(f"❌ Error conectando a Supabase: {e}")
        return None

def save_conversation(supabase, pregunta, respuesta, modo, tiempo_respuesta, session_id):
    """
    Guardar conversación en la base de datos
    
    Args:
        supabase (Client): Cliente de Supabase
        pregunta (str): Pregunta del usuario
        respuesta (str): Respuesta del bot
        modo (str): Modo utilizado
        tiempo_respuesta (float): Tiempo de respuesta en segundos
        session_id (str): ID de la sesión
        
    Returns:
        bool: True si se guardó correctamente, False si hubo error
    """
    if not supabase:
        st.warning("⚠️ Supabase no está conectado - no se guardará la conversación")
        return False
    
    try:
        data = {
            "pregunta": pregunta,
            "respuesta": respuesta,
            "modo": modo,
            "tiempo_respuesta": tiempo_respuesta,
            "session_id": session_id
        }
        
        # Debug más persistente
        with st.container():
            st.write("🔍 **Datos a guardar:**")
            st.json(data)
        
        result = supabase.table(SUPABASE_TABLE).insert(data).execute()
        
        with st.container():
            st.success("✅ **Conversación guardada exitosamente**")
            st.write("📊 Resultado:", result.data)
        
        return True
    except Exception as e:
        with st.container():
            st.error(f"❌ **Error detallado:** {str(e)}")
            st.error(f"🔍 **Tipo de error:** {type(e).__name__}")
        return False

def get_analytics(supabase):
    """
    Obtener estadísticas de uso de la base de datos
    
    Args:
        supabase (Client): Cliente de Supabase
        
    Returns:
        dict: Diccionario con estadísticas o None si hay error
    """
    if not supabase:
        return None
    
    try:
        # Obtener todas las conversaciones
        result = supabase.table(SUPABASE_TABLE).select("*").execute()
        data = result.data
        
        if not data:
            return None
        
        df = pd.DataFrame(data)
        
        # Calcular estadísticas
        analytics = {
            "total_conversaciones": len(df),
            "modos_populares": df['modo'].value_counts().to_dict(),
            "tiempo_promedio": round(df['tiempo_respuesta'].mean(), 2),
            "preguntas_frecuentes": df['pregunta'].value_counts().head(5).to_dict(),
            "sesiones_unicas": df['session_id'].nunique()
        }
        
        return analytics
    except Exception as e:
        st.error(f"❌ Error obteniendo analytics: {e}")
        return None

def get_conversation_history(supabase, session_id, limit=10):
    """
    Obtener historial de conversaciones de una sesión específica
    
    Args:
        supabase (Client): Cliente de Supabase
        session_id (str): ID de la sesión
        limit (int): Número máximo de conversaciones a obtener
        
    Returns:
        list: Lista de conversaciones o None si hay error
    """
    if not supabase:
        return None
    
    try:
        result = supabase.table(SUPABASE_TABLE)\
            .select("*")\
            .eq("session_id", session_id)\
            .order("timestamp", desc=True)\
            .limit(limit)\
            .execute()
        
        return result.data
    except Exception as e:
        st.error(f"❌ Error obteniendo historial: {e}")
        return None