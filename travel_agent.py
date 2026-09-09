import asyncio

from agent_framework import Agent, InMemoryHistoryProvider

from core import get_chat_client
from travel_tools import get_previous_trip


async def main():

    agent = Agent(
        client=get_chat_client(),
        name="TravelMate",
        instructions="""
            You are a corporate travel assistant.

            Help the user plan business trips.

            Ask for missing information rather than inventing it.

            If the user asks about a previous trip,
            retrieve the relevant interaction history using
            the available tool.
            """,
        context_providers=[InMemoryHistoryProvider()],
        tools=[
            get_previous_trip,
        ],
    )

    session = agent.create_session()

    # -------------------------------------------------
    # SESSION MEMORY TEST
    # -------------------------------------------------

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

    # -------------------------------------------------
    # INTERACTION MEMORY RETRIEVAL TEST
    # -------------------------------------------------

    response3 = await agent.run(
        "What happened on my previous Melbourne trip?",
        session=session,
    )

    print("\nInteraction Memory:")
    print(response3.text)

    # -------------------------------------------------
    # INSPECT SESSION MEMORY
    # -------------------------------------------------

    source_state = session.state.get(
        InMemoryHistoryProvider.DEFAULT_SOURCE_ID,
        {},
    )

    messages = source_state.get(
        "messages",
        [],
    )

    print("\nSession messages:")

    for message in messages:
        print(f"Message: {message.text}")


asyncio.run(main())
