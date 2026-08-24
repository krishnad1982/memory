import asyncio
from dataclasses import asdict
from datetime import datetime
from enum import Enum

from agent_framework import (
    Agent,
    AgentSession,
    CompactionProvider,
    InMemoryHistoryProvider,
    SummarizationStrategy,
)

from core import get_chat_client
from model import ConversationState
from state import sync_conversation_state

# A cheaper/faster model is recommended for summarization specifically —
# separate from the main reasoning model the assistant uses.
# At 26:
# Summary of 1–6
# Raw 7–26

# After six more messages:
# Updated summary of 1–12
# Raw 13–32

# After another six:
# Updated summary of 1–18
# Raw 19–38

summarization = SummarizationStrategy(
    client=get_chat_client(),  # your summarization model
    target_count=2,  # Always keep the last 2 messages in raw form, and summarize the rest
    threshold=1,  # fires once count exceeds target_count + threshold == 3
    prompt=(
        "Summarize this architecture review conversation. "
        "Preserve: requirements discussed, options considered, decisions made, "
        "risks raised, and any user preferences stated. Do not preserve raw tool output."
    ),
)

history = InMemoryHistoryProvider(source_id="message_summary")
is_new_conversation = False

compaction = CompactionProvider(
    before_strategy=summarization,  # compacts before each model call
    after_strategy=summarization,  # compacts after each model call
    source_id="summary",
    history_source_id=history.source_id,
)

agent = Agent(
    client=get_chat_client(),  # your primary reasoning model
    name="SolutionArchitectAssistant",
    instructions="""You are a solution architect assistant. You help users design and evaluate software architectures. 
    Always provide responses in fewer than 50 words.""",
    context_providers=[history, compaction],
)


def _json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Cannot serialize {type(obj)}")


def save_session(state: ConversationState):
    """Save the session state to a file or database for later retrieval."""
    import json

    with open(f"session_{state.conversation_id}.json", "w") as f:
        json.dump(asdict(state), f, indent=2, default=_json_default)


def load_session(conversation_id: str) -> AgentSession:
    """Load the session state from a file or database."""
    import json

    with open(f"session_{conversation_id}.json") as f:
        state = json.load(f)
    session = AgentSession.from_dict(state["maf_session_state"])
    return session


async def execute():
    conversation_state = None
    user_input = input("Do you want to start a new conversation? (yes/no): ")
    if user_input.lower() in ["yes", "y"]:
        session = (
            agent.create_session()
        )  # this is our `conversation_id`, per our earlier agreement
    else:
        user_input = input("Enter conversation ID to resume:")
        session = load_session(user_input)

    while True:
        user_input = input("user:")
        if user_input.lower() in ["exit", "quit"]:
            break
        message = user_input
        result = await agent.run(message, session=session)
        # print(f"assistant: {result.text}")
        conversation_state = await sync_conversation_state(
            conversation_id=session.session_id,
            user_id="krish",
            tenant_id="krishpinky",
            session=session,
            history=history,
            prior_state=conversation_state,
        )
    if conversation_state is not None:
        conversation_state.maf_session_state = session.to_dict()
        save_session(conversation_state)


asyncio.run(execute())
# What is a three-tier architecture?
# When should I use microservices?
# What is an API gateway?
# How can I improve application scalability?
# When should I use a message queue?
# What is the difference between SQL and NoSQL?
# How do I secure an API?
# What is a single point of failure?
# When should I use serverless architecture?
# How can I reduce cloud costs?
