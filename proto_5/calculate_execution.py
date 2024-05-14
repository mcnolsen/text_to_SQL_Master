# Calculate and print aggregate precision, recall and execution accuracy for the best_eval folder

import json
import os

difficulty = []

# Load difficulty levels from the combined queries

with open('../scoring/gt.json', 'r') as json_file:
    queries = json.load(json_file)

    for query in queries:
        difficulty.append(query["level_of_difficulty"])

with open('../merge_queries.json', 'r') as json_file:
    queries = json.load(json_file)

    for query in queries:
        difficulty.append(query["level_of_difficulty"])

# Find each file in the best_eval folder
best_eval_path = 'best_eval'
best_results = []

# Iterate through each file in the best_eval folder
for file in os.listdir(best_eval_path):
    file_path = os.path.join(best_eval_path, file)

    # Initialize precision and recall
    precision = []
    recall = []
    f1 = []
    low_precision = []
    low_recall = []
    low_f1 = []
    medium_precision = []
    medium_recall = []
    medium_f1 = []
    high_precision = []
    high_recall = []
    high_f1 = []
    execution_accuracy = []
    low_execution_accuracy = []
    medium_execution_accuracy = []
    high_execution_accuracy = []

    # Load the json file
    data = json.load(open(file_path))

    # Calculate the aggregate precision, recall and execution accuracy
    for query in data:
        precision.append(query['precision'])
        recall.append(query['recall'])
        f1.append(query['f1'])
        if query['did_pass']:
            execution_accuracy.append(1)
        else:
            execution_accuracy.append(0)

        if difficulty[query['query_index']] == 'low':
            low_precision.append(query['precision'])
            low_recall.append(query['recall'])
            low_f1.append(query['f1'])
            if query['did_pass']:
                low_execution_accuracy.append(1)
            else:
                low_execution_accuracy.append(0)
        elif difficulty[query['query_index']] == 'medium':
            medium_precision.append(query['precision'])
            medium_recall.append(query['recall'])
            medium_f1.append(query['f1'])
            if query['did_pass']:
                medium_execution_accuracy.append(1)
            else:
                medium_execution_accuracy.append(0)
        elif difficulty[query['query_index']] == 'high':
            high_precision.append(query['precision'])
            high_recall.append(query['recall'])
            high_f1.append(query['f1'])

            if query['did_pass']:
                high_execution_accuracy.append(1)
            else:
                high_execution_accuracy.append(0)


    # Calculate the aggregate precision, recall and execution accuracy
    aggregate_precision = sum(precision) / len(precision)
    aggregate_recall = sum(recall) / len(recall)
    if aggregate_precision + aggregate_recall == 0:
        aggregate_f1 = 0
    else:
        aggregate_f1 = 2 * ((aggregate_precision * aggregate_recall) / (aggregate_precision + aggregate_recall))
    aggregate_execution_accuracy = sum(execution_accuracy) / len(execution_accuracy)
    low_aggregate_precision = sum(low_precision) / len(low_precision)
    low_aggregate_recall = sum(low_recall) / len(low_recall)
    if low_aggregate_precision + low_aggregate_recall == 0:
        low_aggregate_f1 = 0
    else:
        low_aggregate_f1 = 2 * ((low_aggregate_precision * low_aggregate_recall) / (low_aggregate_precision + low_aggregate_recall))
    low_aggregate_execution_accuracy = sum(low_execution_accuracy) / len(low_execution_accuracy)
    medium_aggregate_precision = sum(medium_precision) / len(medium_precision)
    medium_aggregate_recall = sum(medium_recall) / len(medium_recall)
    if medium_aggregate_precision + medium_aggregate_recall == 0:
        medium_aggregate_f1 = 0
    else:
        medium_aggregate_f1 = 2 * ((medium_aggregate_precision * medium_aggregate_recall) / (medium_aggregate_precision + medium_aggregate_recall))
    medium_aggregate_execution_accuracy = sum(medium_execution_accuracy) / len(medium_execution_accuracy)
    high_aggregate_precision = sum(high_precision) / len(high_precision)
    high_aggregate_recall = sum(high_recall) / len(high_recall)
    if high_aggregate_precision + high_aggregate_recall == 0:
        high_aggregate_f1 = 0
    else:
        high_aggregate_f1 = 2 * ((high_aggregate_precision * high_aggregate_recall) / (high_aggregate_precision + high_aggregate_recall))
    high_aggregate_execution_accuracy = sum(high_execution_accuracy) / len(high_execution_accuracy)

    # Print the results
    print(file)
    print(f"Aggregate Precision: {aggregate_precision}")
    print(f"Aggregate Recall: {aggregate_recall}")
    print(f"Aggregate F1: {aggregate_f1}")
    print(f"Aggregate Execution Accuracy: {aggregate_execution_accuracy}")

    # Store the results
    best_results.append({
        'file': file,
        'aggregate_precision': aggregate_precision,
        'aggregate_recall': aggregate_recall,
        'aggregate_f1': aggregate_f1,
        'aggregate_execution_accuracy': aggregate_execution_accuracy,
        'low_aggregate_precision': low_aggregate_precision,
        'low_aggregate_recall': low_aggregate_recall,
        'low_aggregate_f1': low_aggregate_f1,
        'low_aggregate_execution_accuracy': low_aggregate_execution_accuracy,
        'medium_aggregate_precision': medium_aggregate_precision,
        'medium_aggregate_recall': medium_aggregate_recall,
        'medium_aggregate_f1': medium_aggregate_f1,
        'medium_aggregate_execution_accuracy': medium_aggregate_execution_accuracy,
        'high_aggregate_precision': high_aggregate_precision,
        'high_aggregate_recall': high_aggregate_recall,
        'high_aggregate_f1': high_aggregate_f1,
        'high_aggregate_execution_accuracy': high_aggregate_execution_accuracy
    })

# Make sure eval_results directory exists
if not os.path.exists('eval_results'):
    os.makedirs('eval_results')
    
# Sort the results by file name and save them to a json file
best_results = sorted(best_results, key=lambda x: x['file'])
with open('eval_results/best_results.json', 'w') as f:
    json.dump(best_results, f, indent=4)