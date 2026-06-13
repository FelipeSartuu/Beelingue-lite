"""
config.py
---------
Este arquivo é responsável por carregar configurações do projeto.

Aqui ficam coisas como:
- chave da Gemini API;
- nome do modelo de IA;
- caminho do arquivo de memória.

Por que separar isso em um arquivo?
Porque deixa o restante do código mais limpo. Em vez de espalhar
os.getenv(...) pelo projeto inteiro, centralizamos tudo aqui.
"""

# os permite acessar variáveis de ambiente do sistema.
# Exemplo: os.getenv("GOOGLE_API_KEY") pega a chave salva no .env.
import os

# dataclass cria uma classe simples só para guardar dados.
# É útil para criar uma estrutura de configurações sem escrever muito código.
from dataclasses import dataclass

# load_dotenv lê o arquivo .env e joga as variáveis dele no ambiente do Python.
# Sem isso, o Python não conseguiria ler GOOGLE_API_KEY do arquivo .env.
from dotenv import load_dotenv


# Carrega automaticamente as variáveis do arquivo .env, se ele existir.
load_dotenv()


@dataclass
class Settings:
    """
    Classe simples para guardar as configurações do projeto.

    dataclass permite criar uma classe sem precisar escrever um __init__ manual.
    """

    # Chave da API da Gemini.
    # Se não existir, fica como string vazia.
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")

    # Modelo que será usado.
    # Deixamos um valor padrão para facilitar o estudo.
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Caminho do arquivo JSON usado como memória simples.
    memory_file: str = os.getenv("MEMORY_FILE", "data/memory.json")


def get_settings() -> Settings:
    """
    Retorna um objeto Settings com as configurações do projeto.

    Em projetos maiores, esta função poderia validar mais coisas.
    Aqui ela é simples para ser didática.
    """

    return Settings()
