"""
app.py
------
Este arquivo cria a interface web simples do Beelingue Lite.

Usamos Streamlit porque ele permite criar uma aplicação no navegador
usando apenas Python, sem precisar criar HTML, CSS, JavaScript ou backend separado.

Para rodar:
streamlit run app.py
"""

# Streamlit é a biblioteca que cria a interface no navegador.
import streamlit as st

# Função principal que executa o grafo do LangGraph.
from graph import run_beelingue

# Memória simples para exibir/apagar histórico.
from memory import SimpleMemory

# Configurações para checar se a chave da Gemini foi configurada.
from config import get_settings


# st.set_page_config configura título, ícone e layout da página.
st.set_page_config(
    page_title="Beelingue Lite",
    page_icon="🐝",
    layout="centered",
)


# CSS simples para deixar a interface mais bonita.
# unsafe_allow_html=True permite inserir HTML/CSS dentro do Streamlit.
st.markdown(
    """
    <style>
        .main-title {
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 0px;
        }

        .subtitle {
            font-size: 18px;
            color: #9ca3af;
            margin-top: 0px;
        }

        .bee-card {
            padding: 18px;
            border-radius: 18px;
            background: #f3ffe0;
            border: 1px solid #d9f99d;
            margin-bottom: 18px;
            color: #102016;
        }

        .bee-card b {
            color: #0f2a18;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# Título principal da aplicação.
st.markdown('<p class="main-title">🐝 Beelingue Lite</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Um agente didático de IA para estudar inglês usando Python, LangChain, LangGraph e Gemini API.</p>',
    unsafe_allow_html=True,
)


# Card explicativo inicial.
st.markdown(
    """
    <div class="bee-card">
        <b>Como funciona?</b><br>
        Você escolhe um modo, digita uma frase ou dúvida, e o Beelingue usa um fluxo com LangGraph para decidir o caminho da resposta.
    </div>
    """,
    unsafe_allow_html=True,
)


# Carregamos as configurações para verificar se a chave existe.
settings = get_settings()

# Se a chave não estiver configurada, mostramos um aviso claro.
if not settings.google_api_key or settings.google_api_key == "cole_sua_chave_aqui":
    st.warning(
        "Você ainda não configurou a GOOGLE_API_KEY. "
        "Crie um arquivo .env baseado no .env.example para usar a IA real."
    )


# Criamos a memória para consultar e limpar histórico.
memory = SimpleMemory()


# Sidebar é o menu lateral do Streamlit.
with st.sidebar:
    st.header("Configurações")

    # selectbox cria uma caixa de seleção.
    level = st.selectbox(
        "Nível de inglês",
        ["Iniciante", "Intermediário", "Avançado"],
        index=0,
    )

    mode = st.selectbox(
        "Modo do agente",
        [
            "Corrigir frase",
            "Conversar em inglês",
            "Gerar quiz",
            "Explicar dúvida",
        ],
        index=0,
    )

    st.divider()

    st.write("Modelo configurado:")
    st.code(settings.gemini_model)

    # Botão para limpar histórico.
    if st.button("Limpar histórico"):
        memory.clear()
        st.success("Histórico apagado.")


# Exemplos rápidos para ajudar o usuário a testar.
st.subheader("Exemplos para testar")

example_col_1, example_col_2 = st.columns(2)

with example_col_1:
    st.info("Correção: I have 19 years old")
    st.info("Dúvida: Qual a diferença entre do e does?")

with example_col_2:
    st.info("Conversa: Tell me about your day")
    st.info("Quiz: Simple Past")


# Área principal de input.
st.subheader("Digite sua mensagem")

# text_area permite digitar textos maiores que um input comum.
user_text = st.text_area(
    "Frase, dúvida ou tema:",
    placeholder="Exemplo: I have 19 years old",
    height=120,
)


# Botão principal.
# Quando ele for clicado, chamaremos o LangGraph.
if st.button("Enviar para o Beelingue", type="primary"):
    # Validação simples para evitar enviar texto vazio.
    if not user_text.strip():
        st.error("Digite alguma frase, dúvida ou tema antes de enviar.")
    else:
        # st.spinner mostra uma mensagem enquanto a IA responde.
        with st.spinner("O Beelingue está pensando..."):
            # Chamamos a função que executa o grafo do LangGraph.
            result = run_beelingue(
                user_text=user_text,
                mode=mode,
                level=level,
            )

        # Se o grafo retornou erro, mostramos para o usuário.
        if result.get("error"):
            st.error("Ocorreu um erro ao chamar a IA:")
            st.code(result["error"])
        else:
            # Caso contrário, mostramos a resposta final.
            st.subheader("Resposta do Beelingue")
            st.markdown(result.get("ai_answer", "Sem resposta."))

            # Mostramos também informações técnicas para estudo.
            with st.expander("Ver estado final do LangGraph"):
                st.json(result)


# Área de histórico.
st.divider()
st.subheader("Histórico recente")

# Lemos todas as interações salvas.
data = memory.read_all()
interactions = data.get("interactions", [])

# Se não houver histórico, mostramos uma mensagem simples.
if not interactions:
    st.write("Nenhuma interação salva ainda.")
else:
    # Mostramos as últimas 5 interações, da mais recente para a mais antiga.
    for item in reversed(interactions[-5:]):
        with st.expander(f"{item.get('mode')} | {item.get('level')} | {item.get('created_at')}"):
            st.write("**Aluno:**")
            st.write(item.get("user_text", ""))
            st.write("**Beelingue:**")
            st.markdown(item.get("ai_answer", ""))
