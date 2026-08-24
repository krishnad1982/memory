from dataclasses import dataclass
import os
from agent_framework_foundry import FoundryChatClient
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

load_dotenv()  # Load environment variables from .env file


@dataclass(frozen=True)
class FoundrySettings:
    project_endpoint: str
    model: str


def _get_foundry_settings() -> FoundrySettings:

    return FoundrySettings(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_MODEL"],
    )


def _create_foundry_chat_client():
    settings = _get_foundry_settings()
    return FoundryChatClient(
        project_endpoint=settings.project_endpoint,
        model=settings.model,
        credential=DefaultAzureCredential(),
    )


def get_chat_client() -> FoundryChatClient:
    return _create_foundry_chat_client()
