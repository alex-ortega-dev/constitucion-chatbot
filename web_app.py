"""
Aplicación principal del Chatbot de la Constitución Española
"""

import streamlit as st
import time
import uuid

# Importar módulos locales
from database import init_supabase, save_conversation, get_analytics
from chatbot import load_chatbot_components, create_conversational_chain, get_response, clear_conversation_memory
from config import CSS_STYLES, MODE_COLORS, MODE_NAMES, WELCOME_MESSAGES, STREAMING_DELAY

# Configuración de la página
st.set_page_config(
    page_title="Chatbot Constitución Española",
    page_icon="🇪🇸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def init_session_state():
    """Inicializa las variables de estado de la sesión"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "mode" not in st.session_state:
        st.session_state.mode = "ciudadano"
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

def render_header():
    """Renderiza el header de la aplicación"""
    st.markdown('<h1 class="main-header">🇪🇸 Chatbot Constitución Española</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Pregúntame sobre cualquier artículo o concepto constitucional</p>', unsafe_allow_html=True)

def render_mode_selector():
    """Renderiza el selector de modos"""
    st.markdown('<div class="mode-selector">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👨‍👩‍👧‍👦 Modo Ciudadano", 
                    use_container_width=True, 
                    key="btn_ciudadano",
                    help="Explicaciones simples y cercanas"):
            st.session_state.mode = "ciudadano"
    
    with col2:
        if st.button("🎓 Modo Estudiante", 
                    use_container_width=True,
                    key="btn_estudiante", 
                    help="Respuestas pedagógicas y estructuradas"):
            st.session_state.mode = "estudiante"
    
    with col3:
        if st.button("⚖️ Modo Profesional", 
                    use_container_width=True,
                    key="btn_profesional",
                    help="Análisis jurídico técnico"):
            st.session_state.mode = "profesional"
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_mode_indicator():
    """Renderiza el indicador del modo actual"""
    st.markdown(f"""
    <div style="background-color: {MODE_COLORS[st.session_state.mode]}; 
                color: white; 
                padding: 0.5rem; 
                border-radius: 5px; 
                text-align: center; 
                margin-bottom: 1rem;">
        <strong>Modo actual:</strong> {MODE_NAMES[st.session_state.mode]}
    </div>
    """, unsafe_allow_html=True)

def initialize_welcome_message():
    """Inicializa el mensaje de bienvenida según el modo"""
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant", 
            "content": WELCOME_MESSAGES[st.session_state.mode]
        })

def render_chat_history():
    """Renderiza el historial de chat"""
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><strong>🙋‍♂️ Tú:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot-message"><strong>🤖 Asistente:</strong> {message["content"]}</div>', unsafe_allow_html=True)

def render_user_input():
    """Renderiza el input del usuario y devuelve la entrada y el botón"""
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "Escribe tu pregunta:",
            placeholder="Ej: ¿Qué dice sobre la libertad de expresión?",
            key=f"user_input_{len(st.session_state.messages)}",
            label_visibility="visible"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        send_button = st.button("Enviar", type="primary", use_container_width=True)
    
    return user_input, send_button

def simulate_streaming_response(response_container, respuesta_completa):
    """Simula el efecto de streaming en la respuesta"""
    palabras = respuesta_completa.split()
    respuesta_parcial = ""
    
    for palabra in palabras:
        respuesta_parcial += palabra + " "
        response_container.markdown(
            f'<div class="chat-message bot-message"><strong>🤖 Asistente:</strong> {respuesta_parcial}<span style="opacity: 0.5;">▊</span></div>', 
            unsafe_allow_html=True
        )
        time.sleep(STREAMING_DELAY)
    
    # Mostrar respuesta final sin cursor
    response_container.markdown(
        f'<div class="chat-message bot-message"><strong>🤖 Asistente:</strong> {respuesta_completa}</div>', 
        unsafe_allow_html=True
    )

def process_user_question(user_input, send_button, qa_chain, supabase):
    """Procesa la pregunta del usuario"""
    # Verificar si se debe procesar la pregunta
    should_process = (
        (send_button and user_input.strip()) or 
        (user_input and user_input.strip() and st.session_state.get('last_input') != user_input)
    )
    
    if should_process and user_input.strip():
        st.session_state.last_input = user_input
        
        # Añadir pregunta al historial
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Mostrar pregunta inmediatamente
        st.markdown(f'<div class="chat-message user-message"><strong>🙋‍♂️ Tú:</strong> {user_input}</div>', unsafe_allow_html=True)
        
        # Contenedor para respuesta streaming
        response_container = st.empty()
        
        try:
            # Medir tiempo de respuesta
            start_time = time.time()
            
            # Obtener respuesta del chatbot
            respuesta_completa = get_response(qa_chain, user_input)
            
            # Calcular tiempo de respuesta
            tiempo_respuesta = time.time() - start_time
            
            # Simular streaming
            simulate_streaming_response(response_container, respuesta_completa)
            
            # Guardar en base de datos
            if supabase:
                save_conversation(
                    supabase, 
                    user_input, 
                    respuesta_completa, 
                    st.session_state.mode, 
                    tiempo_respuesta,
                    st.session_state.session_id
                )
            
            # Añadir respuesta al historial
            st.session_state.messages.append({"role": "assistant", "content": respuesta_completa})
            
            # Rerun para limpiar input
            time.sleep(0.5)
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error procesando pregunta: {e}")

def render_sidebar(supabase):
    """Renderiza la barra lateral con información y analytics"""
    with st.sidebar:
        st.markdown("### ℹ️ Información")
        st.markdown(f"""
        **Modo actual:** {MODE_NAMES[st.session_state.mode]}
        
        **🔄 Cambia de modo** arriba para diferentes estilos de respuesta:
        
        **👨‍👩‍👧‍👦 Ciudadano:** Explicaciones simples, ejemplos cotidianos
        **🎓 Estudiante:** Pedagógico, estructurado, perfecto para estudiar
        **⚖️ Profesional:** Técnico, preciso, análisis jurídico
        
        **Ejemplos de preguntas:**
        - ¿Cuáles son los derechos fundamentales?
        - ¿Qué dice sobre el Rey?
        - ¿Cómo se reforma la Constitución?
        - ¿Qué es el Tribunal Constitucional?
        """)
        
        # Analytics
        if supabase:
            st.markdown("### 📊 Estadísticas de Uso")
            analytics = get_analytics(supabase)
            
            if analytics:
                st.markdown(f"""
                <div class="analytics-card">
                    <strong>📈 Total conversaciones:</strong> {analytics['total_conversaciones']}<br>
                    <strong>⚡ Tiempo promedio:</strong> {analytics['tiempo_promedio']}s<br>
                    <strong>🎯 Modo más popular:</strong> {max(analytics['modos_populares'], key=analytics['modos_populares'].get)}<br>
                    <strong>👥 Sesiones únicas:</strong> {analytics['sesiones_unicas']}
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🔄 Actualizar estadísticas"):
                    st.rerun()
            else:
                st.info("📊 Aún no hay datos suficientes para mostrar estadísticas")
        
        # Botón limpiar chat
        if st.button("🗑️ Limpiar chat"):
            st.session_state.messages = []
            if "qa_chain" in st.session_state:
                clear_conversation_memory(st.session_state.qa_chain)
            st.rerun()

def main():
    """Función principal de la aplicación"""
    # Aplicar estilos CSS
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    
    # Inicializar estado de sesión
    init_session_state()
    
    # Inicializar Supabase
    supabase = init_supabase()
    
    # Renderizar header
    render_header()
    
    # Renderizar selector de modo
    render_mode_selector()
    
    # Renderizar indicador de modo
    render_mode_indicator()
    
    # Cargar componentes del chatbot
    db, llm = load_chatbot_components()
    
    if not db or not llm:
        st.error("❌ No se pudo cargar el chatbot. Verifica que existe la carpeta 'vectorstore/' y tu API key.")
        return
    
    # Crear/actualizar cadena conversacional si es necesario
    if ("qa_chain" not in st.session_state or 
        st.session_state.get("current_mode") != st.session_state.mode):
        
        st.session_state.qa_chain = create_conversational_chain(llm, db, st.session_state.mode)
        st.session_state.current_mode = st.session_state.mode
        st.session_state.messages = []  # Limpiar mensajes al cambiar modo
    
    # Inicializar mensaje de bienvenida
    initialize_welcome_message()
    
    # Renderizar historial de chat
    render_chat_history()
    
    # Renderizar input del usuario
    user_input, send_button = render_user_input()
    
    # Procesar pregunta del usuario
    process_user_question(user_input, send_button, st.session_state.qa_chain, supabase)
    
    # Renderizar sidebar
    render_sidebar(supabase)

if __name__ == "__main__":
    main()