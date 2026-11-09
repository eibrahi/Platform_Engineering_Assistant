from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Conversation, Message, User
from app.routers.common import DbSession
from app.schemas.assistant import ChatRequest, ChatResponse, ConversationRead, MessageRead

router = APIRouter(prefix='/api/assistant', tags=['assistant'])


def get_graph(request: Request) -> CompiledStateGraph:
    return request.app.state.graph


AssistantGraph = Annotated[CompiledStateGraph, Depends(get_graph)]


def get_current_user(db: DbSession, x_user_id: Annotated[int, Header()]) -> User:
    # Übergangslösung bis zum echten Login: Der Client sagt per Header, wer er ist
    user = db.get(User, x_user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, 'Unbekannter oder deaktivierter User')
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_own_conversation(db: Session, conversation_id: int, user: User) -> Conversation:
    # Fremde Unterhaltungen sehen aus wie nicht vorhandene (404 statt 403)
    conversation = db.get(Conversation, conversation_id)
    if conversation is None or conversation.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Unterhaltung nicht gefunden')
    return conversation


@router.post('/chat', response_model=ChatResponse)
def chat(data: ChatRequest, db: DbSession, graph: AssistantGraph, user: CurrentUser) -> ChatResponse:
    # 1. Unterhaltung: neu anlegen oder vorhandene laden
    if data.conversation_id is None:
        conversation = Conversation(user_id=user.id)
        db.add(conversation)
        db.flush()  # vergibt conversation.id, ohne schon endgültig zu speichern
    else:
        conversation = get_own_conversation(db, conversation_id=data.conversation_id, user=user)

    # 2. Frage des Users für den lesbaren Verlauf speichern
    db.add(Message(conversation_id=conversation.id, role='user', content=data.message))

    # 3. Graph aufrufen - thread_id ist die Unterhaltungs-ID
    config = {'configurable': {'thread_id': str(conversation.id)}}
    result = graph.invoke({'messages': [HumanMessage(data.message)]}, config)
    answer = result['messages'][-1].content

    # 4. Antwort speichern und alles gemeinsam festschreiben
    db.add(Message(conversation_id=conversation.id, role='assistant', content=answer))
    db.commit()

    return ChatResponse(conversation_id=conversation.id, answer=answer)


@router.get('/conversations', response_model=list[ConversationRead])
def list_conversations(db: DbSession, user: CurrentUser):
    query = (
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc(), Conversation.id.desc())
    )
    return db.scalars(query).all()


@router.get('/conversations/{conversation_id}/messages', response_model=list[MessageRead])
def list_messages(conversation_id: int, db: DbSession, user: CurrentUser):
    get_own_conversation(db, conversation_id, user)  # nur zur Prüfung: 404, wenn fremd oder unbekannt
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at, Message.id)
    )
    return db.scalars(query).all()
