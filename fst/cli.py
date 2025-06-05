import sys
import asyncio
from main import run

def main():
    if len(sys.argv) != 3:
        print("Usage: fst <command> <input_file>")
    else:
        command = sys.argv[1]
        input_file = sys.argv[2]
        asyncio.run(run(command, input_file))
