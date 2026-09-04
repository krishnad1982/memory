import asyncio

from agent_framework import Agent, InMemoryHistoryProvider
from core import get_chat_client


async def main():

    agent = Agent(
        client=get_chat_client(),
        name="TravelMate",
        instructions="""
            You are a corporate travel assistant.

            Help the user plan business trips.

            Ask for missing information rather than inventing it.
            """,
        context_providers=[InMemoryHistoryProvider()],
    )

    # -----------------------------
    # SESSION MEMORY
    # -----------------------------

    session = agent.create_session()

    response1 = await agent.run(
        "I want to travel from Sydney to Melbourne.",
        session=session,
    )

    print("Turn 1:")
    print(response1.text)

    response2 = await agent.run(
        "15 October 2026.",
        session=session,
    )

    print("\nTurn 2:")
    print(response2.text)

    # Get the messages from the session memory
    source_state = session.state.get(InMemoryHistoryProvider.DEFAULT_SOURCE_ID, {})
    messages = source_state.get("messages", [])
    for message in messages:
        print(f"Message: {message.text}")


asyncio.run(main())
