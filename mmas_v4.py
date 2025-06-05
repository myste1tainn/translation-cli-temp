from openai import NotGiven
from openai.types.shared_params.response_format_text import ResponseFormatText
import pandas as pd
from aiclient import ai_chat
import re

from track_time import track_time
import tiktoken


@track_time
async def mmas_spread(inputmd):
    with open("data/prompts/mmas-extraction-line-items-v4.txt", "r") as file:
        prompts = file.read()

    a = len(tiktoken.encoding_for_model("gpt-4o-mini").encode(inputmd))
    print(f"Spreading Input Tokens: {a}")
    # Use the financial data to generate content for each topic
    response = ai_chat(
        messages=[
            {
                "role": "user",
                "content": prompts.format(
                    # financial_data=fs_data.to_dict(),
                    # additional_description="G: Type Justification - Stating how you determined the type of fs",
                    # additional_description="G: Scale Justification - Stating how you determined the Scale (Field F) for the row",
                    additional_description="",
                    financial_data=inputmd,
                ),
            }
        ],
        response_format={"type": "text"},
        max_completion_tokens=8000,
    )
    res = response.choices[0].message.content
    a = len(tiktoken.encoding_for_model("gpt-4o-mini").encode(res or ""))
    print(f"Spreading: {res}")
    print(f"Spreading Output Tokens: {a}")

    with open("out/raw_res.txt", "w") as file:
        file.write(res or "EMPTY")

    # Save the response content to a file
    headers = '"Financial Group","Financial Item","Notes","Type","Period","Value","Unit","Scale"\n'
    if res != None:
        match = re.search(r"```.*?\n(.*?)\n```", res, re.DOTALL)
        if match:
            content = match.group(1).strip()
            return f"{headers}{content}"
        else:
            return headers

    return headers
