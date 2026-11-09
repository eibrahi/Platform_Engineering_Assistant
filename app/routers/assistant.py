from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from app.models import Conversation, Message, User
from app.routers.common import DbSession
from app.schemas.assistant import ChatRequest, ChatResponse

router = APIRouter(prefix='/api/assistant', tags=['assistant'])


def get_graph(request: Request) -> CompiledStateGraph:
    return request.app.state.graph


AssistantGraph = Annotated[CompiledStateGraph, Depends(get_graph)]


@router.post('/chat', response_model=ChatResponse)
def chat(data: ChatRequest, db: DbSession, graph: AssistantGraph, x_user_id: Annotated[int, Header()]):
    # 1. User prüfen: muss existieren UND aktiv sein
    user = db.get(User, x_user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Unbekannter oder deaktivierter User')

    # 2. Unterhaltung: neu anlegen oder vorhandene laden
    if data.conversation_id is None:
        conversation = Conversation(user_id=user.id)
        db.add(conversation)
        db.flush()  # vergibt conversation.id, ohne schon endgültig zu speichern
    else:
        conversation = db.get(Conversation, data.conversation_id)
        if conversation is None or conversation.user_id != user.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, 'Unterhaltung nicht gefunden')

    # 3. Frage des Users für den lesbaren Verlauf speichern
    db.add(Message(conversation_id=conversation.id, role='user', content=data.message))

    # 4. Graph aufrufen - thread_id ist die Unterhaltungs-ID
    config = {'configurable': {'thread_id': str(conversation.id)}}
    result = graph.invoke({'messages': [HumanMessage(data.message)]}, config)
    answer = result['messages'][-1].content

    # 5. Antwort speichern und alles gemeinsam festschreiben
    db.add(Message(conversation_id=conversation.id, role='assistant', content=answer))
    db.commit()

    return ChatResponse(conversation_id=conversation.id, answer=answer)
