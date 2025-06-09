from io import StringIO
import asyncio
import sys
from fst.core.spread.mmas_v4 import mmas_spread
from fst.core.spread.mmas_classify import mmas_classify
from fst.core.spread.mmas_aggregate import mmas_aggregate
from fst.core.translate.fs_translate import translate
import pandas as pd
from fst.utils.track_time import track_time

debug = False


@track_time
async def _run(command: str, input_file: str):
    basename = input_file.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    if command == "translate":
        print("###### Step 1. Translation of FS from Thai to English")
        output_path = f"out/{basename}_translated.xlsx"
        md_path, output_path = await translate(input_file, output_path, "PTTPE")
        print("Done converting the file")
        print(f"Output file is   : {output_path}")
        print(f"Markdown file is : {md_path}")
        print("-- End of translation step --\n\n")
    elif command == "spread":
        print("###### Step 2. MMAS Spreading")
        output_path = f"out/{basename}_translated.xlsx"
        output_fp = f"out/{basename}_spreaded.csv"
        print("Input Markdown file is  :", input_file)
        with open(input_file, "r") as ifile:
            inputmd = ifile.read()

        print("###### Step 2.1. Standardization of spreading data")
        spreaded_csv_text = await mmas_spread(inputmd)

        # # Count tokens using tiktoken
        # inputmd_tokens = len(tiktoken.encoding_for_model("gpt-4o-mini").encode(inputmd))
        # prompts_tokens = len(tiktoken.encoding_for_model("gpt-4o-mini").encode(prompts))
        #
        # # Print token counts
        # print(f"InputMD Tokens: {inputmd_tokens}, Prompts Tokens: {prompts_tokens}")
        print(f"Done spreading, CSV file {output_fp}")
        if debug:
            print("Spreaded DF:")
            print(spreaded_csv_text)
        print("\n\n")

        with open(output_fp, "w") as output_file:
            output_file.write(spreaded_csv_text or "No data to write")

        print("###### Step 2.2. Grouping and classificatiion of the spreading")
        classified_df, output_labeled_file, output_full_file = mmas_classify(
            pd.read_csv(StringIO(spreaded_csv_text))
        )
        print(f"Done classification")
        if debug:
            print(f"DF           : {classified_df}")
        print(f"Labeled file : {output_labeled_file}")
        print(f"Merged file  : {output_full_file}")
        print("\n\n")
        aggregated_df = mmas_aggregate(
            classified_df,
            groupby=["Type", "mmas_group", "mmas_item", "Period", "Unit"],
        )
        groupby_group_n_item_file = f"out/{basename}_aggregated_group_item.csv"
        with open(groupby_group_n_item_file, "w") as file:
            file.write(aggregated_df.to_csv(index=False))

        print("###### Step 2.3. Aggregation per assigned group")
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
        print("-- End of MMAS spreading step --\n\n")
    else:
        print("Invalid command. Use 'translate' or 'spread'.")


def run():
    if len(sys.argv) != 3:
        print("Usage: python main.py <command> <input_file>")
    else:
        command = sys.argv[1]
        input_file = sys.argv[2]
        asyncio.run(_run(command, input_file))
