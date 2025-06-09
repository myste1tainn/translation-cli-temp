import pandas as pd
from aiclient import ai_chat
import re


def process_financial_statements():
    # Load the financial statements from the translated Excel file
    # financial_data = pd.read_excel("translated_gpsc_sheet3-gpt-4o-batch.xlsx")
    financial_data = pd.read_excel(
        "PTTEP_FINANCIAL_STATEMENTS_EN_Cut version.xlsx", sheet_name=None, header=None
    )

    # Load the MMAS template with all sheets
    template_sheets = pd.read_excel(
        "data/templates/mmas_template-sectioned.xlsx", sheet_name=None, header=None
    )

    output_file = "output.csv"

    # Write the header to the output file
    with open(output_file, "w") as file:
        file.write('Class,Topic,Type,Period,Value,"Original Financial Item"\n')

    # Load the content template for ai_chat
    with open("data/prompts/mmas-extraction-line-items-v2.txt", "r") as file:
        content_template = file.read()
    with open("data/templates/mmas-energy-mapping.txt", "r") as file:
        mmas_mappings = file.read()

    count = 1

    for fs_sheet_name, fs_data in financial_data.items():

        # Iterate over each sheet
        for sheet_name, data in template_sheets.items():
            # if sheet_name != "Current Assets":
            #     continue
            # Extract subtopics
            subtopics = "\n Subtopic".join(data[0].dropna().tolist())
            print(f"Sheet: {fs_sheet_name}, Topic is: {sheet_name}")

            # Format the string
            formatted_topics = f"{count}. Topic {sheet_name}:\nSubtopic {subtopics}\n\n"
            count += 1

            # Use the financial data to generate content for each topic
            response = ai_chat(
                messages=[
                    {
                        "role": "user",
                        "content": content_template.format(
                            financial_data=fs_data.to_dict(),
                            mmas_mappings=mmas_mappings,
                            formatted_topics=formatted_topics,
                        ),
                    }
                ],
                max_completion_tokens=4000,
            )
            res = response.choices[0].message.content
            with open("raw_res.txt", "w") as file:
                file.write(res or "EMPTY")

            # Save the response content to a file
            if res != None:
                with open(output_file, "a") as file:
                    match = re.search(r"```.*?\n(.*?)\n```", res, re.DOTALL)
                    if match:
                        extracted_content = match.group(1).strip()
                    else:
                        extracted_content = ""

                    file.write(extracted_content + "\n")
