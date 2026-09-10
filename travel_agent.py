import asyncio

from agent_framework import Agent, InMemoryHistoryProvider

from core import get_chat_client
from travel_tools import get_previous_trip, get_user_profile, save_user_preference


async def main():

    agent = Agent(
        client=get_chat_client(),
        name="TravelMate",
        instructions="""
            You are a corporate travel assistant.
            Help the user plan business trips.
            Ask for missing information rather than inventing it.

            If the user asks about previous trips,
            use the interaction-history tool.

            If the user explicitly asks you to remember
            a durable travel preference,
            use save_user_preference.

            If stored user preferences are relevant
            to the current request,
            use get_user_profile.
            """,
        context_providers=[InMemoryHistoryProvider()],
        tools=[get_previous_trip, get_user_profile, save_user_preference],
    )

    session = agent.create_session()
    session.state["user_id"] = "123"

    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ("exit", "quit"):
            break
        response = await agent.run(
            user_input,
            session=session,
        )
        print(f"\nAgent: {response.text}")

    # -------------------------------------------------
    # SESSION MEMORY TEST
    # -------------------------------------------------
    # I want to travel from Sydney to Melbourne.
    # 15 October 2026.

    # -------------------------------------------------
    # INTERACTION MEMORY RETRIEVAL TEST
    # -------------------------------------------------
    # What happened on my previous Melbourne trip?

    # -------------------------------------------------
    # USER PROFILE MEMORY
    # -------------------------------------------------
    # Remember that my preferred airline is Qantas.
    # Remember that I prefer aisle seats.
    # Restart the program and ask: What are my travel preferences?

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
