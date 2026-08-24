from datetime import datetime, timezone
from agent_framework import GROUP_ANNOTATION_KEY, SUMMARY_OF_MESSAGE_IDS_KEY, Message

from model import (
    ConversationMessage,
    ConversationState,
    ConversationSummary,
    MessageRole,
)


def is_summary_message(message) -> bool:
    """True if this message is a synthetic summary MAF inserted during compaction,
    rather than an original user/assistant/tool message."""
    annotation = message.additional_properties.get(GROUP_ANNOTATION_KEY, {})
    return SUMMARY_OF_MESSAGE_IDS_KEY in annotation


async def sync_conversation_state(
    conversation_id: str,
    user_id: str,
    tenant_id: str,
    session,  # the AgentSession
    history,  # the InMemoryHistoryProvider
    prior_state: ConversationState | None = None,
) -> ConversationState:
    provider_state = session.state.setdefault(history.source_id, {})
    raw_messages = await history.get_messages(session.session_id, state=provider_state)

    state = prior_state or ConversationState(
        conversation_id=conversation_id,
        user_id=user_id,
        tenant_id=tenant_id,
    )

    summary_msgs = [m for m in raw_messages if is_summary_message(m)]
    raw_only = [m for m in raw_messages if not is_summary_message(m)]

    if summary_msgs:
        latest_summary = summary_msgs[0]  # most recent summarization event
        total_covered = _get_total_covered(summary_msgs)
        state.summary = ConversationSummary(
            conversation_id=state.conversation_id,
            summary_text=latest_summary.text,
            covers_message_count=total_covered,
            last_updated=datetime.now(timezone.utc),
        )

    state.messages = [
        ConversationMessage(
            conversation_id=state.conversation_id,
            role=MessageRole(m.role),
            content=m.text,
        )
        for m in raw_only
    ]
    state.last_active_at = datetime.now(timezone.utc)
    return state


def _get_total_covered(summary_messages: list[Message]):
    total_count = 0
    for summary_message in summary_messages:
        message_ids = summary_message.additional_properties.get(
            GROUP_ANNOTATION_KEY, {}
        ).get(SUMMARY_OF_MESSAGE_IDS_KEY, [])
        total_count += sum(1 for msg_id in message_ids if msg_id.startswith("msg_"))
    return total_count


# summary-4 has SUMMARY_OF_MESSAGE_IDS_KEY {summary3, msg0, msg1}
# summary-3 has SUMMARY_OF_MESSAGE_IDS_KEY {summary2, msg2, msg3}
# summary-2 has SUMMARY_OF_MESSAGE_IDS_KEY {summary1, msg4, msg5}
# finally SUMMARY_OF_MESSAGE_IDS_KEY {msg6, msg7}
