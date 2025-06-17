import streamlit as st
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Configuración de la página
st.set_page_config(
    page_title="Chatbot Constitución Española",
    page_icon="🇪🇸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado
st.markdown("""
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
    .mode-button-selected {
        background-color: #d4af37 !important;
        color: white !important;
        border: 2px solid #b8941f !important;
    }
    .mode-button-selected:hover {
        background-color: #b8941f !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Diferentes prompts según el modo
PROMPTS = {
    "ciudadano": """
Eres un asistente constitucional amigable que ayuda a ciudadanos españoles a entender sus derechos y deberes.

PERSONALIDAD:
- Habla de forma cercana y accesible
- Evita jerga jurídica complicada
- Usa ejemplos cotidianos
- Sé empático con las preocupaciones ciudadanas

INSTRUCCIONES:
- Explica los conceptos de forma simple
- Menciona SIEMPRE el artículo específico (ej: "según el artículo 20...")
- Si no encuentras información, dilo claramente
- Ofrece ejemplos prácticos cuando sea útil

CONTEXTO DE LA CONSTITUCIÓN:
{context}

HISTORIAL DE CONVERSACIÓN:
{chat_history}

PREGUNTA DEL CIUDADANO:
{question}

RESPUESTA (como experto constitucional amigable):
""",

    "estudiante": """
Eres un profesor de Derecho Constitucional que ayuda a estudiantes a preparar exámenes.

PERSONALIDAD:
- Pedagógico y estructurado
- Incluye detalles importantes para exámenes
- Conecta conceptos entre sí
- Sugiere temas relacionados

INSTRUCCIONES:
- Estructura las respuestas de forma clara
- Cita artículos específicos SIEMPRE
- Explica el contexto histórico cuando sea relevante
- Relaciona con otros artículos o principios constitucionales
- Sugiere qué más estudiar sobre el tema

CONTEXTO DE LA CONSTITUCIÓN:
{context}

HISTORIAL DE CONVERSACIÓN:
{chat_history}

PREGUNTA DEL ESTUDIANTE:
{question}

RESPUESTA (como profesor de Derecho Constitucional):
""",

    "profesional": """
Eres un jurista experto en Derecho Constitucional que asesora a profesionales del derecho.

PERSONALIDAD:
- Técnico y preciso
- Usa terminología jurídica apropiada
- Analiza implicaciones legales
- Referencia jurisprudencia cuando sea relevante

INSTRUCCIONES:
- Usa lenguaje jurídico preciso
- Cita artículos exactos con numeración completa
- Analiza las implicaciones prácticas
- Menciona posibles interpretaciones doctrinales
- Señala conexiones con otras normas del ordenamiento

CONTEXTO DE LA CONSTITUCIÓN:
{context}

HISTORIAL DE CONVERSACIÓN:
{chat_history}

CONSULTA PROFESIONAL:
{question}

RESPUESTA (como jurista constitucionalista):
"""
}

@st.cache_resource
def load_chatbot():
    """Carga el chatbot una sola vez con memoria"""
    load_dotenv()
    
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        db = FAISS.load_local("vectorstore/", embeddings, allow_dangerous_deserialization=True)
        
        llm = ChatOpenAI(
            model="gpt-4.1",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        return db, llm
    except Exception as e:
        st.error(f"Error cargando el chatbot: {e}")
        return None, None

def create_chain_with_prompt(llm, db, mode):
    """Crea la cadena conversacional con el prompt específico"""
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    
    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=PROMPTS[mode]
    )
    
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=db.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt},
        verbose=False
    )
    
    return qa_chain

def main():
    # Header
    st.markdown('<h1 class="main-header">🇪🇸 Chatbot Constitución Española</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Pregúntame sobre cualquier artículo o concepto constitucional</p>', unsafe_allow_html=True)
    
    # Inicializar modo por defecto
    if "mode" not in st.session_state:
        st.session_state.mode = "ciudadano"
    
    # Selector de modo
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
    
    # Mostrar modo actual con estilo visual
    mode_colors = {
        "ciudadano": "#4CAF50",
        "estudiante": "#2196F3", 
        "profesional": "#9C27B0"
    }
    
    mode_names = {
        "ciudadano": "👨‍👩‍👧‍👦 Ciudadano - Explicaciones simples y cercanas",
        "estudiante": "🎓 Estudiante - Respuestas pedagógicas y estructuradas", 
        "profesional": "⚖️ Profesional - Análisis jurídico técnico"
    }
    
    st.markdown(f"""
    <div style="background-color: {mode_colors[st.session_state.mode]}; 
                color: white; 
                padding: 0.5rem; 
                border-radius: 5px; 
                text-align: center; 
                margin-bottom: 1rem;">
        <strong>Modo actual:</strong> {mode_names[st.session_state.mode]}
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar chatbot
    db, llm = load_chatbot()
    
    if not db or not llm:
        st.error("No se pudo cargar el chatbot. Verifica que existe la carpeta 'vectorstore/' y tu API key.")
        return
    
    # Crear cadena con el prompt del modo actual
    if "qa_chain" not in st.session_state or st.session_state.get("current_mode") != st.session_state.mode:
        st.session_state.qa_chain = create_chain_with_prompt(llm, db, st.session_state.mode)
        st.session_state.current_mode = st.session_state.mode
        # Limpiar mensajes al cambiar de modo
        st.session_state.messages = []
    
    # Inicializar historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Mensaje de bienvenida según el modo
    if not st.session_state.messages:
        welcome_messages = {
            "ciudadano": "¡Hola! Soy tu asistente para entender la Constitución Española. Puedes preguntarme sobre tus derechos, cómo funciona el Estado, o cualquier duda que tengas sobre la Constitución. ¡Hablaré de forma sencilla y con ejemplos!",
            "estudiante": "¡Bienvenido! Soy tu profesor virtual de Derecho Constitucional. Estoy aquí para ayudarte a estudiar, preparar exámenes y entender a fondo la Constitución Española. Te daré explicaciones estructuradas y conectaré conceptos entre sí.",
            "profesional": "Saludos. Soy su consultor en Derecho Constitucional. Puedo asistirle con análisis jurídicos, interpretaciones doctrinales y cuestiones técnicas sobre la Constitución Española de 1978. Procederé con la precisión técnica que requiere su práctica profesional."
        }
        st.session_state.messages.append({
            "role": "assistant", 
            "content": welcome_messages[st.session_state.mode]
        })
    
    # Mostrar historial de chat
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><strong>🙋‍♂️ Tú:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot-message"><strong>🤖 Asistente:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Input del usuario
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "Escribe tu pregunta:",
            placeholder="Ej: ¿Qué dice sobre la libertad de expresión?",
            key=f"user_input_{len(st.session_state.messages)}",
            label_visibility="visible"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Espaciado para alinear
        send_button = st.button("Enviar", type="primary", use_container_width=True)
    
    # Procesar pregunta (tanto con botón como con Enter)
    if (send_button and user_input.strip()) or (user_input and user_input.strip() and st.session_state.get('last_input') != user_input):
        # Evitar duplicados con Enter
        if user_input.strip():
            st.session_state.last_input = user_input
            
            # Añadir pregunta del usuario al historial
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Mostrar la pregunta inmediatamente
            st.markdown(f'<div class="chat-message user-message"><strong>🙋‍♂️ Tú:</strong> {user_input}</div>', unsafe_allow_html=True)
            
            # Contenedor para la respuesta streaming
            response_container = st.empty()
            
            try:
                # Invocar el chatbot
                resultado = st.session_state.qa_chain.invoke({"question": user_input})
                respuesta_completa = resultado['answer']
                
                # Simular streaming escribiendo palabra por palabra
                response_container.markdown(f'<div class="chat-message bot-message"><strong>🤖 Asistente:</strong> ', unsafe_allow_html=True)
                
                palabras = respuesta_completa.split()
                respuesta_parcial = ""
                
                for i, palabra in enumerate(palabras):
                    respuesta_parcial += palabra + " "
                    response_container.markdown(
                        f'<div class="chat-message bot-message"><strong>🤖 Asistente:</strong> {respuesta_parcial}<span style="opacity: 0.5;">▊</span></div>', 
                        unsafe_allow_html=True
                    )
                    # Pequeña pausa entre palabras
                    import time
                    time.sleep(0.05)
                
                # Mostrar respuesta final sin cursor
                response_container.markdown(
                    f'<div class="chat-message bot-message"><strong>🤖 Asistente:</strong> {respuesta_completa}</div>', 
                    unsafe_allow_html=True
                )
                
                # Añadir respuesta al historial
                st.session_state.messages.append({"role": "assistant", "content": respuesta_completa})
                
                # Rerun para limpiar el input
                time.sleep(0.5)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Sidebar con información
    with st.sidebar:
        st.markdown("### ℹ️ Información")
        st.markdown(f"""
        **Modo actual:** {mode_names[st.session_state.mode]}
        
        **🔄 Cambia de modo** arriba para diferentes estilos de respuesta:
        
        **👨‍👩‍👧‍👦 Ciudadano:** Explicaciones simples, ejemplos cotidianos
        **🎓 Estudiante:** Pedagógico, estructurado, perfecto para estudiar
        **⚖️ Profesional:** Técnico, preciso, análisis jurídico
        
        **Ejemplos de preguntas:**
        - ¿Cuáles son los derechos fundamentales?
        - ¿Qué dice sobre el Rey?
        - ¿Cómo se reforma la Constitución?
        - ¿Qué es el Tribunal Constitucional?
        
        **Nota:** Las respuestas son orientativas. Para consultas legales específicas, consulta a un profesional.
        """)
        
        if st.button("🗑️ Limpiar chat"):
            st.session_state.messages = []
            # También limpiar la memoria del modelo
            if "qa_chain" in st.session_state:
                st.session_state.qa_chain.memory.clear()
            st.rerun()

if __name__ == "__main__":
    main()