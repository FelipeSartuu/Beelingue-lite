"""
ai_model.py
-----------
Este arquivo cria o modelo de IA que será usado pelo LangChain.

Neste projeto, usamos:
- Gemini API como IA real;
- LangChain para conversar com essa IA;
- ChatGoogleGenerativeAI como classe de integração com Gemini.
"""

# ChatGoogleGenerativeAI é a classe do LangChain que conversa com a Gemini API.
from langchain_google_genai import ChatGoogleGenerativeAI

# Importamos as configurações do nosso projeto.
from config import get_settings


def get_llm(temperature: float = 0.4) -> ChatGoogleGenerativeAI:
    """
    Cria e retorna o modelo de IA.

    Parâmetro:
    - temperature controla o quanto a IA será criativa.
      0.0 = mais direta e previsível.
      1.0 = mais criativa e variável.

    Retorno:
    - um objeto ChatGoogleGenerativeAI pronto para ser usado pelo LangChain.
    """

    # Pega as configurações carregadas do .env.
    settings = get_settings()

    # Se a chave não foi configurada, interrompemos com uma mensagem clara.
    if not settings.google_api_key or settings.google_api_key == "cole_sua_chave_aqui":
        raise ValueError(
            "GOOGLE_API_KEY não configurada. "
            "Crie um arquivo .env com sua chave da Gemini API."
        )

    # A biblioteca langchain-google-genai lê a variável GOOGLE_API_KEY do ambiente.
    # Como o load_dotenv() já foi chamado em config.py, a chave já está disponível.
    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        temperature=temperature,
    )

    return llm
