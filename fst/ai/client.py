import os
import pprint
from openai import AzureOpenAI
from openai.types.chat import ChatCompletion
from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam


endpoint = os.getenv("ENDPOINT_URL", "https://llm-platform-gateway.azure-api.net")
deployment = os.getenv(
    "DEPLOYMENT_NAME", "gpt-4o"
)  # gemini-pro-1.5 #claude-3-5-sonnet-v2 #gpt-4o
subscription_key = os.getenv(
    "AZURE_OPENAI_API_KEY",
    "Bearer 824fd67a3fa8bd3a2f280cc72b7fbcf39de924d893c6a191572b40044078461c",
)
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-05-01-preview",
)


def get_ai_client():
    return client


def ai_chat(
    messages: list[ChatCompletionMessageParam],
    response_format: ResponseFormat = {"type": "json_object"},
    max_completion_tokens: int = 1000,
    debug: bool = False,
) -> ChatCompletion:
    if debug:
        content = messages[0].get("content")
        pprint.pprint(f"Prompt message is:\n{content}")
    return get_ai_client().chat.completions.create(
        model=deployment,
        user="gpt-bem-excel-batch",
        response_format=response_format,
        # extra_body={
        #     "store": True,  # Enables storing completion
        #     "metadata": metadata,  # Attach structured metadata
        #     "tags": tags  # Attach searchable tags
        messages=messages,
        max_completion_tokens=max_completion_tokens,
    )


def ai_chat_parse(
    messages: list[ChatCompletionMessageParam],
    response_format: type[object],
    max_completion_tokens: int = 1000,
    debug: bool = False,
):
    if debug:
        content = messages[0].get("content")
        pprint.pprint(f"Prompt message is:\n{content}")
    return get_ai_client().beta.chat.completions.parse(
        model=deployment,
        user="gpt-bem-excel-batch",
        response_format=response_format,
        # extra_body={
        #     "store": True,  # Enables storing completion
        #     "metadata": metadata,  # Attach structured metadata
        #     "tags": tags  # Attach searchable tags
        messages=messages,
        max_completion_tokens=max_completion_tokens,
    )


### You can also send "tags" or "metdata", keeping the code for reference
#   Not in used at the moment
# # Define Metadata
# metadata = {
#     "user_id": "12345",
#     "request_id": request_id,
#     "file_name": "BEM-Sheets",
#     "file_format": "xlsx",
#     "purpose": "document_processing",
#     "model_used": deployment  # Tracks the OpenAI model used
# }
#
# # Define Tags
# tags = {
#     "category": "document_translation",
#     "file_name": "BEM-Sheets",
#     "file_format": "xlsx",
#     "source": "AI-generated",
#     "request_id": request_id,
#     "model_used": deployment
# }
#
