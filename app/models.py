from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text, func, true
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

# Erlaubte Werte (werden in den Pydantic-Schemas validiert)
USER_ROLES = ('admin', 'platform_engineer', 'viewer')
ENVIRONMENTS = ('dev', 'test', 'prod')
PLATFORM_STATUSES = ('healthy', 'degraded', 'down', 'unknown')
DEPLOYMENT_STATUSES = ('planned', 'approved', 'running', 'succeeded', 'failed')
INCIDENT_SEVERITIES = ('low', 'medium', 'high', 'critical')
INCIDENT_STATUSES = ('open', 'investigating', 'resolved')
AGENT_RUN_STATUSES = ('running', 'succeeded', 'failed')
MESSAGE_ROLES = ('user', 'assistant', 'system', 'tool')


def created_at_column() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    role: Mapped[str] = mapped_column(String(50), default='viewer')
    # Deaktivieren statt löschen: Deployments und Chats verweisen weiter auf den User
    is_active: Mapped[bool] = mapped_column(server_default=true())
    created_at: Mapped[datetime] = created_at_column()

    deployments: Mapped[list['Deployment']] = relationship(back_populates='creator')
    conversations: Mapped[list['Conversation']] = relationship(back_populates='user')


class Platform(Base):
    __tablename__ = 'platforms'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    environment: Mapped[str] = mapped_column(String(20))
    cloud_provider: Mapped[str] = mapped_column(String(50), default='azure')
    azure_subscription_id: Mapped[str | None] = mapped_column(String(64))
    azure_region: Mapped[str | None] = mapped_column(String(50))
    databricks_workspace_url: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default='unknown')
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    deployments: Mapped[list['Deployment']] = relationship(back_populates='platform', cascade='all, delete-orphan')
    incidents: Mapped[list['Incident']] = relationship(back_populates='platform', cascade='all, delete-orphan')
    agent_runs: Mapped[list['AgentRun']] = relationship(back_populates='platform')
    conversations: Mapped[list['Conversation']] = relationship(back_populates='platform')


class Deployment(Base):
    __tablename__ = 'deployments'

    id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[int] = mapped_column(ForeignKey('platforms.id'), index=True)
    deployment_type: Mapped[str] = mapped_column(String(50), default='terraform')
    status: Mapped[str] = mapped_column(String(20), default='planned')
    git_commit: Mapped[str | None] = mapped_column(String(40))
    terraform_plan: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[int | None] = mapped_column(ForeignKey('users.id'), index=True)

    platform: Mapped['Platform'] = relationship(back_populates='deployments')
    creator: Mapped['User | None'] = relationship(back_populates='deployments')


class Incident(Base):
    __tablename__ = 'incidents'

    id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[int] = mapped_column(ForeignKey('platforms.id'), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), default='medium')
    status: Mapped[str] = mapped_column(String(20), default='open')
    root_cause: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_column()
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    platform: Mapped['Platform'] = relationship(back_populates='incidents')


class Document(Base):
    __tablename__ = 'documents'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(100))
    document_type: Mapped[str] = mapped_column(String(50))
    version: Mapped[str | None] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_column()
    # Später mit pgvector: Chunks mit embedding = Vector(1536) in eigener Tabelle


class AgentRun(Base):
    __tablename__ = 'agent_runs'

    id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[int | None] = mapped_column(ForeignKey('platforms.id'), index=True)
    agent_type: Mapped[str] = mapped_column(String(50))
    input: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    output: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20), default='running')
    started_at: Mapped[datetime] = created_at_column()
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    platform: Mapped['Platform | None'] = relationship(back_populates='agent_runs')


class Conversation(Base):
    __tablename__ = 'conversations'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    platform_id: Mapped[int | None] = mapped_column(ForeignKey('platforms.id'), index=True)
    created_at: Mapped[datetime] = created_at_column()

    user: Mapped['User'] = relationship(back_populates='conversations')
    platform: Mapped['Platform | None'] = relationship(back_populates='conversations')
    messages: Mapped[list['Message']] = relationship(
        back_populates='conversation', cascade='all, delete-orphan', order_by='Message.created_at'
    )


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey('conversations.id'), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_column()

    conversation: Mapped['Conversation'] = relationship(back_populates='messages')
