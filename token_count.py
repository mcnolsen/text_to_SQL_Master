import tiktoken
import json
import os
encoding = tiktoken.get_encoding("cl100k_base")

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
directories = ['proto_1', 'proto_2', 'proto_3', 'proto_4', 'proto_5']
# Encode all of the outputs from proto_3/cleaned json files and get the average token count
def get_token_count(directory):
    token_count = 0
    total_count = 0
    files = []
    token_counts = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as f:
                data = json.load(f)
                for item in data:
                    total_count += 1
                    token_count += len(encoding.encode(item))
                    files.append(filename)
                    token_counts.append(len(encoding.encode(item)))

    print("Total token count: ", token_count)
    print("Average token count: ", token_count/total_count)

    return token_counts, files


# Get the token count for each file
def get_token_count_per_file(token_counts, files):
    file_token_count = {}
    for i in range(len(files)):
        if files[i] not in file_token_count:
            file_token_count[files[i]] = token_counts[i]
        else:
            file_token_count[files[i]] += token_counts[i]

    for key in file_token_count:
        print(key, ":", file_token_count[key])

for directory in directories:
    token_counts, files = get_token_count(directory)
    get_token_count_per_file(token_counts, files)

    # check if token_count folder exists
    if not os.path.exists("token_count"):
        os.makedirs("token_count")
    
    with open("token_count/" + directory + "_token_count.txt", 'w') as f:
        file_token_count = {}
        for i in range(len(files)):
            if files[i] not in file_token_count:
                file_token_count[files[i]] = token_counts[i]
            else:
                file_token_count[files[i]] += token_counts[i]

        for key in file_token_count:
            f.write(key + " : " + str(file_token_count[key]) + "\n")


