"""
memory.py
---------
Este arquivo cuida da memória simples do projeto.

Importante:
- Esta NÃO é uma memória avançada de produção.
- É apenas um arquivo JSON para estudo.
- Serve para o agente lembrar as últimas interações do aluno.

Em um projeto profissional, isso poderia ser trocado por:
- banco de dados PostgreSQL;
- Redis;
- memória/checkpointer persistente do LangGraph;
- banco vetorial.
"""

# json permite ler e escrever arquivos no formato JSON.
# JSON parece um dicionário/lista do Python, mas salvo como texto.
import json

# Path ajuda a trabalhar com caminhos de arquivos de forma mais segura.
from pathlib import Path

# datetime e timezone ajudam a salvar a data/hora de cada interação.
from datetime import datetime, timezone

# Importamos as configurações para saber onde está o arquivo de memória.
from config import get_settings


def _now_iso() -> str:
    """
    Retorna a data/hora atual em formato ISO.

    Exemplo de retorno:
    2026-06-15T18:30:00+00:00
    """

    return datetime.now(timezone.utc).isoformat()


class SimpleMemory:
    """
    Classe responsável por salvar e carregar o histórico do aluno.

    A ideia é ser simples:
    - tudo fica em um arquivo JSON;
    - cada nova conversa é adicionada em uma lista;
    - o agente usa as últimas mensagens como contexto.
    """

    def __init__(self, file_path: str | None = None):
        """
        Inicializa a memória.

        Parâmetro:
        - file_path: caminho opcional do arquivo JSON.
          Se não for passado, usamos o caminho definido no .env.
        """

        # Carrega configurações do projeto.
        settings = get_settings()

        # Define o caminho do arquivo de memória.
        self.file_path = Path(file_path or settings.memory_file)

        # Garante que a pasta data/ exista.
        # parents=True cria pastas intermediárias se necessário.
        # exist_ok=True evita erro se a pasta já existir.
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Se o arquivo ainda não existir, cria um JSON inicial vazio.
        if not self.file_path.exists():
            self.file_path.write_text(
                json.dumps({"interactions": []}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    def read_all(self) -> dict:
        """
        Lê todo o conteúdo do arquivo de memória.

        Retorna:
        - um dicionário Python com a chave "interactions".
        """

        try:
            # Lê o texto do arquivo.
            raw_text = self.file_path.read_text(encoding="utf-8")

            # Converte o texto JSON para dicionário Python.
            return json.loads(raw_text)
        except Exception:
            # Se o arquivo estiver quebrado, retorna memória vazia.
            # Isso evita que o app inteiro pare por causa do histórico.
            return {"interactions": []}

    def get_recent_history(self, limit: int = 5) -> str:
        """
        Retorna as últimas interações em formato de texto.

        Parâmetro:
        - limit: quantidade máxima de interações recentes.

        Por que retornar texto?
        Porque esse texto será colocado dentro do prompt da IA.
        """

        # Lê todas as interações salvas.
        data = self.read_all()
        interactions = data.get("interactions", [])

        # Pega apenas as últimas N interações.
        recent = interactions[-limit:]

        # Se não houver histórico, avisamos a IA.
        if not recent:
            return "Sem histórico ainda."

        # Montamos uma lista de linhas de texto.
        lines = []
        for item in recent:
            lines.append(f"Aluno: {item.get('user_text', '')}")
            lines.append(f"Beelingue: {item.get('ai_answer', '')[:300]}")
            lines.append("---")

        # Junta tudo em uma string só.
        return "\n".join(lines)

    def save_interaction(self, mode: str, level: str, user_text: str, ai_answer: str) -> None:
        """
        Salva uma nova interação no arquivo JSON.

        Parâmetros:
        - mode: modo escolhido pelo usuário;
        - level: nível de inglês;
        - user_text: mensagem do aluno;
        - ai_answer: resposta gerada pela IA.
        """

        # Lê o arquivo atual.
        data = self.read_all()

        # Garante que exista uma lista chamada interactions.
        interactions = data.setdefault("interactions", [])

        # Adiciona a nova interação.
        interactions.append(
            {
                "created_at": _now_iso(),
                "mode": mode,
                "level": level,
                "user_text": user_text,
                "ai_answer": ai_answer,
            }
        )

        # Salva novamente o JSON formatado.
        self.file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def clear(self) -> None:
        """
        Apaga o histórico do aluno.
        """

        self.file_path.write_text(
            json.dumps({"interactions": []}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
