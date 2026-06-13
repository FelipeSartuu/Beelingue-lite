"""
graph.py
--------
Aqui criamos o fluxo do agente Beelingue Lite usando:
- State: o estado que carrega os dados durante o fluxo;
- Nodes: funções que fazem uma parte do trabalho;
- Edges: setas que ligam um node ao outro;
- Conditional Edges: rotas condicionais, dependendo do modo escolhido.

Fluxo simplificado:

START
  ↓
load_memory
  ↓
understand_request
  ↓
[rota condicional]
  ├── correct_phrase
  ├── conversation_teacher
  ├── create_quiz
  └── explain_doubt
  ↓
save_interaction
  ↓
END
"""

# TypedDict permite definir quais chaves existem no estado do LangGraph.
# É parecido com um dicionário, mas com tipos definidos para estudar melhor.
from typing import TypedDict

# StateGraph cria o grafo.
# START representa o início do fluxo.
# END representa o fim do fluxo.
from langgraph.graph import StateGraph, START, END

# Importamos o modelo de IA configurado no arquivo ai_model.py.
from ai_model import get_llm

# Importamos os prompts do projeto.
from prompts import (
    CORRECTION_PROMPT,
    CONVERSATION_PROMPT,
    QUIZ_PROMPT,
    EXPLAIN_PROMPT,
)

# Importamos a memória simples em JSON.
from memory import SimpleMemory


class BeelingueState(TypedDict):
    """
    Estado do agente.

    No LangGraph, o estado é o conjunto de informações que passa de um node
    para o próximo.

    Cada node recebe esse estado e pode devolver novas informações para ele.
    """

    # Texto digitado pelo aluno.
    user_text: str

    # Modo escolhido na interface.
    # Exemplo: corrigir, conversar, quiz, explicar.
    mode: str

    # Nível do aluno.
    # Exemplo: iniciante, intermediário, avançado.
    level: str

    # Intenção normalizada pelo node understand_request.
    intent: str

    # Histórico recente carregado do arquivo JSON.
    history: str

    # Resposta final gerada pela IA.
    ai_answer: str

    # Campo opcional para salvar erro sem quebrar o app.
    error: str


def load_memory(state: BeelingueState) -> dict:
    """
    Node 1: carrega o histórico recente do aluno.

    Um node no LangGraph é apenas uma função Python.
    Ele recebe o estado atual e retorna um dicionário com as mudanças.
    """

    # Criamos a memória simples.
    memory = SimpleMemory()

    # Pegamos as últimas interações em formato de texto.
    recent_history = memory.get_recent_history(limit=5)

    # Retornamos apenas o campo que queremos adicionar/atualizar no estado.
    return {"history": recent_history}


def understand_request(state: BeelingueState) -> dict:
    """
    Node 2: entende qual caminho o fluxo deve seguir.

    Para manter o projeto didático, a intenção vem do modo escolhido na tela.
    Em um projeto mais avançado, poderíamos usar a própria IA para classificar
    a intenção automaticamente.
    """

    # Pegamos o modo escolhido pelo usuário.
    mode = state.get("mode", "corrigir")

    # Mapeamos textos da interface para nomes internos do grafo.
    mode_to_intent = {
        "Corrigir frase": "correction",
        "Conversar em inglês": "conversation",
        "Gerar quiz": "quiz",
        "Explicar dúvida": "explanation",
    }

    # Se o modo não existir no mapa, usamos correção como padrão.
    intent = mode_to_intent.get(mode, "correction")

    # Atualizamos o estado com a intenção.
    return {"intent": intent}


def route_by_intent(state: BeelingueState) -> str:
    """
    Função de roteamento condicional.

    Ela não é exatamente um node que muda o estado.
    Ela decide para qual node o fluxo deve ir.

    Retorno esperado:
    - correction
    - conversation
    - quiz
    - explanation
    """

    return state.get("intent", "correction")


def _run_chain(prompt_template, state: BeelingueState) -> str:
    """
    Função auxiliar para evitar repetição.

    Ela faz 3 coisas:
    1. cria o modelo Gemini;
    2. conecta prompt + modelo usando LangChain;
    3. executa a chamada e retorna o texto da IA.
    """

    # Cria o modelo de IA.
    llm = get_llm(temperature=0.4)

    # No LangChain, o operador | cria uma corrente.
    # Aqui temos: prompt -> modelo
    # Primeiro o prompt é preenchido, depois enviado para a IA.
    chain = prompt_template | llm

    # invoke executa a chain.
    response = chain.invoke(
        {
            "user_text": state["user_text"],
            "level": state["level"],
            "history": state.get("history", "Sem histórico ainda."),
        }
    )

    # A resposta do modelo vem como um objeto de mensagem.
    # O texto fica em response.content.
    return response.content


def correct_phrase(state: BeelingueState) -> dict:
    """
    Node 3A: corrige uma frase em inglês.
    """

    try:
        answer = _run_chain(CORRECTION_PROMPT, state)
        return {"ai_answer": answer, "error": ""}
    except Exception as exc:
        return {"ai_answer": "", "error": str(exc)}


def conversation_teacher(state: BeelingueState) -> dict:
    """
    Node 3B: conversa com o aluno em inglês.
    """

    try:
        answer = _run_chain(CONVERSATION_PROMPT, state)
        return {"ai_answer": answer, "error": ""}
    except Exception as exc:
        return {"ai_answer": "", "error": str(exc)}


def create_quiz(state: BeelingueState) -> dict:
    """
    Node 3C: cria um mini quiz de inglês.
    """

    try:
        answer = _run_chain(QUIZ_PROMPT, state)
        return {"ai_answer": answer, "error": ""}
    except Exception as exc:
        return {"ai_answer": "", "error": str(exc)}


def explain_doubt(state: BeelingueState) -> dict:
    """
    Node 3D: explica uma dúvida de inglês.
    """

    try:
        answer = _run_chain(EXPLAIN_PROMPT, state)
        return {"ai_answer": answer, "error": ""}
    except Exception as exc:
        return {"ai_answer": "", "error": str(exc)}


def save_interaction(state: BeelingueState) -> dict:
    """
    Node final: salva a interação na memória.

    Só salvamos se não houve erro e se existe resposta da IA.
    """

    # Se houve erro, não salvamos uma resposta vazia no histórico.
    if state.get("error"):
        return {}

    # Se não existe resposta, também não salvamos.
    if not state.get("ai_answer"):
        return {}

    # Criamos o objeto de memória.
    memory = SimpleMemory()

    # Salvamos a interação.
    memory.save_interaction(
        mode=state["mode"],
        level=state["level"],
        user_text=state["user_text"],
        ai_answer=state["ai_answer"],
    )

    # Não precisamos mudar nada no estado.
    return {}


def build_graph():
    """
    Monta e compila o grafo do LangGraph.

    Compilar significa transformar a estrutura declarada em algo executável.
    """

    # Criamos um StateGraph dizendo qual é o tipo do estado.
    graph = StateGraph(BeelingueState)

    # Registramos os nodes do grafo.
    # O primeiro argumento é o nome do node.
    # O segundo argumento é a função Python que será executada.
    graph.add_node("load_memory", load_memory)
    graph.add_node("understand_request", understand_request)
    graph.add_node("correct_phrase", correct_phrase)
    graph.add_node("conversation_teacher", conversation_teacher)
    graph.add_node("create_quiz", create_quiz)
    graph.add_node("explain_doubt", explain_doubt)
    graph.add_node("save_interaction", save_interaction)

    # Criamos as edges normais.
    # START -> load_memory significa: o primeiro node será load_memory.
    graph.add_edge(START, "load_memory")
    graph.add_edge("load_memory", "understand_request")

    # Criamos uma rota condicional.
    # Depois de understand_request, chamamos route_by_intent para decidir
    # qual node será executado.
    graph.add_conditional_edges(
        "understand_request",
        route_by_intent,
        {
            "correction": "correct_phrase",
            "conversation": "conversation_teacher",
            "quiz": "create_quiz",
            "explanation": "explain_doubt",
        },
    )

    # Depois de qualquer node principal, salvamos a interação.
    graph.add_edge("correct_phrase", "save_interaction")
    graph.add_edge("conversation_teacher", "save_interaction")
    graph.add_edge("create_quiz", "save_interaction")
    graph.add_edge("explain_doubt", "save_interaction")

    # Depois de salvar, encerramos o fluxo.
    graph.add_edge("save_interaction", END)

    # compile transforma a definição do grafo em um app executável.
    return graph.compile()


def run_beelingue(user_text: str, mode: str, level: str) -> dict:
    """
    Função simples para a interface chamar o agente.

    Parâmetros:
    - user_text: mensagem/frase digitada pelo aluno;
    - mode: modo escolhido na tela;
    - level: nível de inglês escolhido.

    Retorno:
    - estado final do grafo, contendo ai_answer ou error.
    """

    # Monta o grafo.
    app = build_graph()

    # Estado inicial que entra no grafo.
    initial_state = {
        "user_text": user_text,
        "mode": mode,
        "level": level,
        "intent": "",
        "history": "",
        "ai_answer": "",
        "error": "",
    }

    # Executa o grafo até o END.
    final_state = app.invoke(initial_state)

    # Devolve o resultado para a interface.
    return final_state
