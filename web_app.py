import streamlit as st
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
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
</style>
""", unsafe_allow_html=True)

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
        
        # Crear memoria para recordar la conversación
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Usar ConversationalRetrievalChain en lugar de RetrievalQA
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=db.as_retriever(search_kwargs={"k": 3}),
            memory=memory,
            return_source_documents=True,
            verbose=False
        )
        
        return qa_chain
    except Exception as e:
        st.error(f"Error cargando el chatbot: {e}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🇪🇸 Chatbot Constitución Española</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Pregúntame sobre cualquier artículo o concepto constitucional</p>', unsafe_allow_html=True)
    
    # Cargar chatbot
    qa_chain = load_chatbot()
    
    if not qa_chain:
        st.error("No se pudo cargar el chatbot. Verifica que existe la carpeta 'vectorstore/' y tu API key.")
        return
    
    # Inicializar historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Mensaje de bienvenida
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "¡Hola! Soy tu asistente para consultas sobre la Constitución Española. Puedo recordar nuestra conversación, así que puedes hacer preguntas de seguimiento como '¿y qué más dice sobre eso?' o '¿puedes explicarlo mejor?'"
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
            key="user_input"
        )
    
    with col2:
        send_button = st.button("Enviar", type="primary")
    
    # Procesar pregunta
    if send_button and user_input.strip():
        # Añadir pregunta del usuario al historial
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Mostrar spinner mientras procesa
        with st.spinner("Consultando la Constitución..."):
            try:
                # Usar la nueva cadena conversacional
                resultado = qa_chain.invoke({"question": user_input})
                respuesta = resultado['answer']
                
                # Añadir respuesta al historial
                st.session_state.messages.append({"role": "assistant", "content": respuesta})
                
                # Rerun para mostrar la nueva conversación
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Sidebar con información
    with st.sidebar:
        st.markdown("### ℹ️ Información")
        st.markdown("""
        Este chatbot usa inteligencia artificial para responder preguntas sobre la Constitución Española de 1978.
        
        **🧠 Nuevo: Memoria conversacional**
        Ahora puedo recordar nuestra conversación. Puedes hacer preguntas como:
        - "¿Puedes explicarlo más simple?"
        - "¿Y qué más dice sobre eso?"
        - "Dame un ejemplo"
        
        **Ejemplos de preguntas:**
        - ¿Cuáles son los derechos fundamentales?
        - ¿Qué dice sobre el Rey?
        - ¿Cómo se reforma la Constitución?
        - ¿Qué es el Tribunal Constitucional?
        
        **Nota:** Las respuestas son orientativas. Para consultas legales específicas, consulta a un profesional.
        """)
        
        if st.button("🗑️ Limpiar chat"):
            st.session_state.messages = [{
                "role": "assistant", 
                "content": "¡Hola! Soy tu asistente para consultas sobre la Constitución Española. Puedo recordar nuestra conversación, así que puedes hacer preguntas de seguimiento como '¿y qué más dice sobre eso?' o '¿puedes explicarlo mejor?'"
            }]
            # También limpiar la memoria del modelo
            qa_chain.memory.clear()
            st.rerun()

if __name__ == "__main__":
    main()