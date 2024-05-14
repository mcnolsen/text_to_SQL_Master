# Convert the llama-3-70b.txt file to a json file

import json

# Load the prompts from the queries.txt file
with open("llama-3-70b.txt", "r") as f:
    prompts = f.readlines()

# Dump the prompts to a json file
with open("llama-3-70b.json", "w") as f:
    json.dump(prompts, f, indent=4)