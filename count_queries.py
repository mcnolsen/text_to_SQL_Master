import json


# Load the prompts from the queries.txt file
with open("queries.txt", "r") as f:
    prompts = f.readlines()

with open("scoring/gt.json", "r") as f:
    gt = json.load(f)
    difficulty = []
    for query in gt:
        difficulty.append(query["level_of_difficulty"])
# Get the queries from the queries.json file
with open("merge_queries.json", "r") as f:
    queries = json.load(f)

    for query in queries:
        prompts.append(query["nl_query"])
        difficulty.append(query["level_of_difficulty"])

# Length 

print(len(prompts))

# Count for each difficulty level
low = 0
medium = 0
high = 0
for d in difficulty:
    if d == "low":
        low += 1
    elif d == "medium":
        medium += 1
    else:
        high += 1

print(f"Low: {low}")
print(f"Medium: {medium}")
print(f"High: {high}")