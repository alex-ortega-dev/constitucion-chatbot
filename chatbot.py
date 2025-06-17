"""
Lógica del chatbot, prompts y configuración de LangChain
"""

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from config import MODEL_NAME, MODEL_TEMPERATURE, RETRIEVER_K

# Prompts para diferentes modos
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
def load_chatbot_components():
    """
    Carga los componentes base del chatbot (embeddings, vectorstore, LLM)
    
    Returns:
        tuple: (db, llm) o (None, None) si hay error
    """
    load_dotenv()
    
    try:
        # Cargar embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        
        # Cargar vectorstore
        db = FAISS.load_local("vectorstore/", embeddings, allow_dangerous_deserialization=True)
        
        # Crear LLM
        llm = ChatOpenAI(
            model=MODEL_NAME,
            temperature=MODEL_TEMPERATURE,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        return db, llm
        
    except Exception as e:
        st.error(f"❌ Error cargando componentes del chatbot: {e}")
        return None, None

def create_conversational_chain(llm, db, mode):
    """
    Crea la cadena conversacional con el prompt específico del modo
    
    Args:
        llm: Modelo de lenguaje
        db: Base de datos vectorial
        mode (str): Modo seleccionado ("ciudadano", "estudiante", "profesional")
        
    Returns:
        ConversationalRetrievalChain: Cadena configurada
    """
    # Crear memoria para la conversación
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    
    # Crear prompt personalizado según el modo
    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=PROMPTS[mode]
    )
    
    # Crear la cadena conversacional
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=db.as_retriever(search_kwargs={"k": RETRIEVER_K}),
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt},
        verbose=False
    )
    
    return qa_chain

def get_response(qa_chain, question):
    """
    Obtiene respuesta del chatbot
    
    Args:
        qa_chain: Cadena conversacional
        question (str): Pregunta del usuario
        
    Returns:
        str: Respuesta del chatbot
    """
    try:
        resultado = qa_chain.invoke({"question": question})
        return resultado['answer']
    except Exception as e:
        st.error(f"❌ Error generando respuesta: {e}")
        return "Lo siento, hubo un error procesando tu pregunta. Por favor, inténtalo de nuevo."

def clear_conversation_memory(qa_chain):
    """
    Limpia la memoria de la conversación
    
    Args:
        qa_chain: Cadena conversacional
    """
    if qa_chain and hasattr(qa_chain, 'memory'):
        qa_chain.memory.clear()