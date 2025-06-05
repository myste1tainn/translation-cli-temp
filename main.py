from io import StringIO
import time
import asyncio
import sys
from mmas_v4 import mmas_spread
from mmas_classify import mmas_classify
from mmas_aggregate import mmas_aggregate
from fs_translate import translate
import pandas as pd
from track_time import track_time


@track_time
async def run(command, input_file):
    basename = input_file.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    if command == "translate":
        print("Start converting\n\n")
        output_path = f"out/{basename}_translated.xlsx"
        md_path, output_path = await translate(input_file, output_path, "PTTPE")
        print("Done converting the file")
        print(f"Output file is   : {output_path}")
        print(f"Markdown file is : {md_path}")
    elif command == "spread":
        print("Start processing financial statements\n\n")
        output_fp = f"out/{basename}_spreaded.csv"
        print("Input Markdown file is  :", input_file)
        with open(input_file, "r") as ifile:
            inputmd = ifile.read()

        spreaded_csv_text = await mmas_spread(inputmd)

        # # Count tokens using tiktoken
        # inputmd_tokens = len(tiktoken.encoding_for_model("gpt-4o-mini").encode(inputmd))
        # prompts_tokens = len(tiktoken.encoding_for_model("gpt-4o-mini").encode(prompts))
        #
        # # Print token counts
        # print(f"InputMD Tokens: {inputmd_tokens}, Prompts Tokens: {prompts_tokens}")
        print(f"Done spreading, CSV file {output_fp}")
        print("Spreaded DF:")
        print(spreaded_csv_text)

        with open(output_fp, "w") as output_file:
            output_file.write(spreaded_csv_text or "No data to write")

        classified_df, output_labeled_file, output_full_file = mmas_classify(
            pd.read_csv(StringIO(spreaded_csv_text))
        )
        print(f"Done classification")
        print(f"DF           : {classified_df}")
        print(f"Labeled file : {output_labeled_file}")
        print(f"Merged file  : {output_full_file}")
        aggregated_df = mmas_aggregate(
            classified_df,
            groupby=["Type", "mmas_group", "mmas_item", "Period", "Unit"],
        )
        groupby_group_n_item_file = f"out/{basename}_aggregated_group_item.csv"
        with open(groupby_group_n_item_file, "w") as file:
            file.write(aggregated_df.to_csv(index=False))

        aggregated_df = mmas_aggregate(
            classified_df,
            groupby=["Type", "mmas_group", "Period", "Unit"],
        )
        groupby_group_file = f"out/{basename}_aggregated_group.csv"
        with open(f"out/{basename}_aggregated_group.csv", "w") as file:
            file.write(aggregated_df.to_csv(index=False))
        print("Done processing financial statements\n\n")
        print("Output file is:")
        print(f"Group By Group & Item : {groupby_group_n_item_file}")
        print(f"Group By Group        : {groupby_group_file}")
    else:
        print("Invalid command. Use 'translate' or 'spread'.")


import tiktoken

if __name__ == "__main__":
    # with open(
    #     # "out/PTTEP_Financial statement_TH_2567_Cut version_translated.md", "r"
    #     "out/raw_res.txt",
    #     "r",
    # ) as file:
    #     a = len(tiktoken.encoding_for_model("gpt-4o-mini").encode(file.read()))
    #     print(f"Spreading Input Tokens: {a}")
    if len(sys.argv) != 3:
        print("Usage: python main.py <command> <input_file>")
    else:
        command = sys.argv[1]
        input_file = sys.argv[2]
        asyncio.run(run(command, input_file))
