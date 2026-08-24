from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ConversationMessage:
    conversation_id: str  # maps to MAF's create_session() id
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    referenced_entities: list[str] = field(
        default_factory=list
    )  # e.g. ["claims-processing-api"]


@dataclass
class ConversationSummary:
    conversation_id: str
    covers_message_count: int  # how many raw messages this summary replaces
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    summary_text: str | None = None  # the actual summary text


@dataclass
class ConversationState:
    conversation_id: str
    user_id: str
    tenant_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    messages: list[ConversationMessage] = field(default_factory=list)
    maf_session_state: dict = field(default_factory=dict)
    summary: ConversationSummary | None = None
    status: str = "active"  # active | idle | expired | closed
