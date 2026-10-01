import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Carrega a chave do .env que está na mesma pasta deste arquivo
load_dotenv(Path(__file__).parent / ".env", override=True)

# Cliente do Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Se este modelo der erro de limite ou "não encontrado", troque por outro
# disponível no Google AI Studio (ex.: "gemini-2.5-flash-lite")
MODEL = "gemini-3.8-flash"

SYSTEM_PROMPT = (
    "Você é a ShopAI, assistente virtual de uma loja online. "
    "Ajude os clientes com dúvidas sobre produtos, pedidos, entregas, "
    "trocas e pagamentos. Seja educada, clara e objetiva."
)

st.set_page_config(page_title="ShopAI", page_icon="🛍️")
st.title("🛍️ ShopAI")
st.caption("Assistente virtual da sua loja online")

# Histórico da conversa (user/assistant)
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Mostra o histórico
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada do usuário
if prompt := st.chat_input("Como posso ajudar você hoje?"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # O Gemini chama o assistente de "model" em vez de "assistant"
    history = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part(text=m["content"])],
        )
        for m in st.session_state["messages"]
    ]

    # Envia todo o histórico para a API
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=history,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
        answer = response.text
    except Exception as e:
        answer = f"⚠️ Erro ao chamar o Gemini: {e}"

    # Exibe e salva a resposta
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state["messages"].append({"role": "assistant", "content": answer})