from dataclasses import dataclass


@dataclass
class LLMConfig:
    """
    Data class representing a single LLM config.

    Attributes:
        model (str): The model to use for the LLM.
        api_key (str): The API key to use for the LLM.
        base_url (str): The base URL to use for the LLM.
    """

    model: str
    api_key: str
    base_url: str
