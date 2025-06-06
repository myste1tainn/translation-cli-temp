import pandas as pd
import openpyxl
from googletrans import Translator
import asyncio
import os
from openai import AzureOpenAI
import json
translator = Translator()
endpoint = os.getenv("ENDPOINT_URL", "https://models-east-us-1.openai.azure.com/")  
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o")  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "fa494cd96ff049b897f7557f142ab1c7")  
client = AzureOpenAI(  
    azure_endpoint=endpoint,  
    api_key=subscription_key,  
    api_version="2024-05-01-preview",  
)  

async def google_translate_text(value, dest_lang="en"):
    if isinstance(value, str) and value.strip():
        res = await translator.translate(value, dest=dest_lang)
        return res.text
    return value
def gen_ai_translate_text(value, company):
    if isinstance(value, str) and value.strip():
        return open_ai_translate(value, company)
    return value
def open_ai_translate(value, company):
    response = client.chat.completions.create(
        model=deployment,
        response_format={"type": "json_object"},
        messages=[
            { "role": "system", "content": "You are a financial service translator assistant." },
            { "role": "user", "content": [  
                { 
                    "type": "text", 
                    "text": f"""
Your job is to tranlsate input in Thai to output in English. Please be aware that the content you're translating is from financial statement of a company called: {company}.
input value: {value}
Please give the answer in json format:
{{
    "translated_value": "value"
}}
Example: 
For the request where the the input value: "ยอดคงเหลือต้นงวด"
The response should be:
{{
 "translated_value": "Equity balance at beginning of period"
}}
                    """ 
                }
            ] } 
        ],
        max_completion_tokens=1000
    )
    json_response = response.choices[0].message.content
    response = json.loads(json_response)
    result =  response.get("translated_value")
    print(f"translating {value}, translated {result}")
    return result
async def convert_using_openpyxl(file_path, output_path, company):
    startTime = pd.Timestamp.now()
    print(f"##### Start time: {startTime}")
    wb = openpyxl.load_workbook(file_path)
    sheetCount = 0
    for sheet in wb.worksheets:
        sheetCount = sheetCount + 1
        if sheetCount > 2: 
            break

        print(f"Sheet {sheetCount}: {sheet}")
        merged_ranges = sheet.merged_cells.ranges
        i = 0
        for row in sheet.iter_rows():
            print(f"Row no: {i}")
            i = i+1
            for cell in row:
                # Skip if the cell contains a formula
                if cell.data_type == "f":
                    continue
                for merged_range in merged_ranges:
                    if cell.coordinate in merged_range:
                        top_left_cell = sheet[merged_range.start_cell.coordinate]
                        if cell.coordinate == top_left_cell.coordinate and isinstance(cell.value, str):
                            cell.value = gen_ai_translate_text(cell.value, company)
                        break
                else:
                    cell.value = gen_ai_translate_text(cell.value, company)
    wb.save(output_path)

    endTime = pd.Timestamp.now()
    print(f"##### End time: {endTime}")
    print(f"######### Total time: {endTime - startTime}")

if __name__ == "__main__":
    print("Start converting\n\n")
    # Load Excel
    file_path = "./data/gpsc/FINANCIAL_STATEMENTS.XLSX"
    output_path = "translated_sheet2-test.xlsx"
    asyncio.run(convert_using_openpyxl(file_path, output_path, "Global Power Synergy Public Company Limited"))
    print("Done converting the file\n\n")
