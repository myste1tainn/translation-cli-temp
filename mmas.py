from openai import NotGiven
from openai.types.shared_params.response_format_text import ResponseFormatText
import pandas as pd
from aiclient import ai_chat
import pprint
import json
import os


def process_financial_statements():
    # Load the financial statements from the translated Excel file
    financial_data = pd.read_excel("translated_gpsc_sheet3-gpt-4o-batch.xlsx")

    # Load the MMAS template with all sheets
    template_sheets = pd.read_excel(
        "data/templates/mmas_template-sectioned.xlsx", sheet_name=None, header=None
    )

    # Clear the response output file before processing
    open("response_output.json", "w").close()

    # Load the content template for ai_chat
    with open("data/prompts/mmas-extraction-line-items.txt", "r") as file:
        content_template = file.read()

    count = 1

    # Iterate over each sheet
    for sheet_name, data in template_sheets.items():
        if sheet_name != "Current Assets":
            continue
        # Extract subtopics
        subtopics = "\n Subtopic".join(data[0].dropna().tolist())
        print(f"Topic is: {sheet_name}")

        # Format the string
        formatted_topics = f"{count}. Topic {sheet_name}:\nSubtopic {subtopics}\n\n"
        count += 1

        # Use the financial data to generate content for each topic
        response = ai_chat(
            messages=[
                {
                    "role": "user",
                    "content": content_template.format(
                        financial_data=financial_data.to_dict(),
                        formatted_topics=formatted_topics,
                    ),
                }
            ],
            max_completion_tokens=4000,
        )
        res = response.choices[0].message.content
        # Save the response content to a file
        if res != None:
            with open("response_output.json", "r+") as file:
                try:
                    existing_content = json.load(file)
                except json.JSONDecodeError:
                    print("decode JSON error")
                    existing_content = {"result": []}
                new_content = json.loads(res)
                existing_content["result"].extend(new_content.get("result", []))
                file.seek(0)
                json.dump(existing_content, file, indent=4)
                file.truncate()
