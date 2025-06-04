import pandas as pd
from pydantic import BaseModel, Field
from aiclient import ai_chat
import json
import os
import re

from track_time import track_time
import tiktoken


@track_time
def mmas_classify(df):
    df["id"] = df["Financial Item"].astype("category").cat.codes + 1
    new_df = df[["id", "Financial Item"]].copy()
    uniq_df = new_df.drop_duplicates(subset="id")
    csv_text = uniq_df.to_csv(index=False, columns=["id", "Financial Item"])
    print(csv_text)

    with open("data/prompts/mmas-labeling-mmas-list.txt", "r") as file:
        prompts = file.read()

    with open("data/templates/mmas-energy-mapping.txt", "r") as file:
        mmas_industry_defn = file.read()

    template_sheets = pd.read_excel(
        "data/templates/mmas_template-sectioned.xlsx", sheet_name=None, header=None
    )

    count = 1
    topics = None
    for sheet_name, sheet_data in template_sheets.items():
        subtopics = "\n  - ".join(sheet_data[0].dropna().tolist())
        if topics == None:
            topics = f"{count}. {sheet_name}:\n  - {subtopics}\n\n"
        else:
            topics = f"{topics}\n\n{count}. {sheet_name}:\n  - {subtopics}\n\n"
        count += 1
    # for sheet_name, sheet_data in template_sheets.items():
    #     if sheet_name != "Current Assets" and sheet_name != "Non-current Assets":
    #         continue
    #
    #     subtopics = "\n  - ".join(
    #         sheet_data[[0, 1]]
    #         .dropna()
    #         .apply(lambda row: ": ".join(row.values.astype(str)), axis=1)
    #         .tolist()
    #     )
    #     if topics == None:
    #         topics = f"{count}. {sheet_name}:\n  - {subtopics}\n\n"
    #     else:
    #         topics = f"{topics}\n\n{count}. {sheet_name}:\n  - {subtopics}\n\n"
    #     count += 1
    # topics = "|Group|Item|Definition|\n|-----|----|----------|"
    # for sheet_name, sheet_data in template_sheets.items():
    #     if sheet_name != "Current Assets" and sheet_name != "Non-current Assets":
    #         continue
    #
    #     subtopics = f"\n|{sheet_name}|".join(
    #         sheet_data[[0, 1]]
    #         .dropna()
    #         .apply(lambda row: "|".join(row.values.astype(str)) + "|", axis=1)
    #         .tolist()
    #     )
    #     topics = f"{topics}\n|{sheet_name}|{subtopics}"
    #
    # with open("step_2_defn.md", "w") as file:
    #     file.write(topics or "EMPTY")

    response = ai_chat(
        messages=[
            {
                "role": "user",
                "content": prompts.format(
                    mmas_group_defn=topics,
                    mmas_industry_defn=mmas_industry_defn,
                    input=csv_text,
                ),
            }
        ],
        max_completion_tokens=4000,
    )
    res = response.choices[0].message.content or "{}"
    # Count tokens using tiktoken
    a = len(tiktoken.encoding_for_model("gpt-4o-mini").encode(res))
    print(f"Output Tokens: {a}")
    # return
    with open("out/step_2_raw_res.txt", "w") as file:
        file.write(res or "EMPTY")

    match = re.search(r"```.*?\n(.*?)\n```", res, re.DOTALL)
    if match:
        extracted_content = match.group(1).strip()
    else:
        # assumes that the result is already a json, just without the backticks
        extracted_content = res
    data = json.loads(extracted_content)
    labeled_df = pd.DataFrame(data["results"])

    output_labeled_file = "out/classfied_labeled.json"
    with open(output_labeled_file, "w") as file:
        file.write(res or "")

    merged_labeled_df = pd.merge(
        uniq_df.drop(columns=["Financial Item"]),
        labeled_df,
        on="id",
        how="inner",
    )
    print("############################# merged_labeled_df")
    print(merged_labeled_df)

    full_merged_df = pd.merge(df, merged_labeled_df, on="id", how="left")
    print("############################# full_merged_df")
    print(full_merged_df)

    output_full_file = "classified_full.csv"
    with open(output_full_file, "w") as file:
        file.write(full_merged_df.to_csv(index=False))

    return full_merged_df, output_labeled_file, output_full_file
