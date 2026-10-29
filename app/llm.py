from langchain_openai import ChatOpenAI

from app.config import settings


def get_chat_model() -> ChatOpenAI:
    if not settings.openai_chat_model:
        raise RuntimeError('Es wurde kein OPENAI_CHAT_MODEL in der .env Datei gesetzt')
    if not settings.openai_api_key:
        raise RuntimeError('Es wurde kein OPENAI_API_KEY in der .env Datei gesetzt')
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
        temperature=0,
    )
