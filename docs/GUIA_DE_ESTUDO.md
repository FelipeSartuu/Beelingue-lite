# Guia de estudo do Beelingue Lite

Este guia explica os conceitos novos do projeto em linguagem simples.

---

## 1. O que é LangChain neste projeto?

LangChain é usado para montar a comunicação com o modelo de IA.

No projeto, ele aparece principalmente aqui:

```python
chain = prompt_template | llm
```

Isso significa:

```txt
prompt preenchido com dados do usuário
   ↓
modelo Gemini
   ↓
resposta da IA
```

O operador `|` no LangChain conecta uma etapa na outra.

---

## 2. O que é ChatPromptTemplate?

Está no arquivo `prompts.py`.

Exemplo:

```python
CORRECTION_PROMPT = ChatPromptTemplate.from_messages([...])
```

Ele cria um prompt de chat com mensagens organizadas.

Geralmente usamos:

- `system`: instrução de comportamento da IA;
- `user`: mensagem do usuário.

Exemplo mental:

```txt
System: Você é um professor de inglês didático.
User: Corrija a frase: I have 19 years old
```

---

## 3. O que é LangGraph?

LangGraph organiza a aplicação como um fluxo.

Em vez de fazer tudo em uma função gigante, dividimos em etapas:

```txt
carregar memória
entender pedido
escolher caminho
chamar IA
salvar histórico
```

Essas etapas são chamadas de `nodes`.

---

## 4. O que é State?

State é o estado do fluxo.

No projeto, ele está assim:

```python
class BeelingueState(TypedDict):
    user_text: str
    mode: str
    level: str
    intent: str
    history: str
    ai_answer: str
    error: str
```

Pense no state como uma mochila que passa de uma etapa para outra.

Cada node pode colocar ou atualizar algo dentro dessa mochila.

---

## 5. O que é Node?

Node é uma função que faz uma parte do trabalho.

Exemplo:

```python
def load_memory(state: BeelingueState) -> dict:
    memory = SimpleMemory()
    recent_history = memory.get_recent_history(limit=5)
    return {"history": recent_history}
```

Esse node:

1. recebe o state;
2. lê a memória;
3. devolve um pedaço novo do state.

---

## 6. O que é Edge?

Edge é uma seta ligando um node ao outro.

Exemplo:

```python
graph.add_edge(START, "load_memory")
graph.add_edge("load_memory", "understand_request")
```

Isso quer dizer:

```txt
comece em load_memory
quando terminar, vá para understand_request
```

---

## 7. O que é rota condicional?

É quando o fluxo muda dependendo de alguma informação.

No projeto:

```python
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
```

Se a intenção for `correction`, o grafo vai para `correct_phrase`.

Se for `quiz`, vai para `create_quiz`.

---

## 8. O que é invoke?

`invoke` executa alguma coisa.

No LangChain:

```python
response = chain.invoke({...})
```

Significa:

```txt
execute essa chain usando estes dados
```

No LangGraph:

```python
final_state = app.invoke(initial_state)
```

Significa:

```txt
execute o grafo inteiro começando com este estado inicial
```

---

## 9. O que é .env?

O `.env` guarda configurações sensíveis.

Exemplo:

```env
GOOGLE_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.5-flash
```

Nunca envie o `.env` para o GitHub.

Por isso ele está no `.gitignore`.

---

## 10. O que estudar primeiro?

Sugestão de ordem:

1. Rode o projeto.
2. Leia `app.py` para entender a interface.
3. Leia `graph.py` para entender o fluxo.
4. Leia `prompts.py` para entender os prompts.
5. Leia `ai_model.py` para entender a conexão com Gemini.
6. Leia `memory.py` para entender o histórico.
7. Altere um prompt e veja como a resposta muda.
8. Crie um novo modo, por exemplo: `Traduzir frase`.

---

## 11. Desafio extra

Tente criar um novo modo chamado:

```txt
Vocabulário
```

Ele deve receber um tema, por exemplo:

```txt
job interview
```

E devolver:

- 10 palavras em inglês;
- tradução;
- exemplo de frase;
- exercício final.

Para fazer isso, você precisaria:

1. Criar um novo prompt em `prompts.py`.
2. Criar um novo node em `graph.py`.
3. Adicionar a rota condicional.
4. Adicionar a opção no `selectbox` do `app.py`.
