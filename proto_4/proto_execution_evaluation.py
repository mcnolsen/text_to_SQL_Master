import json
import os


# Define the paths
model_results_path = './model_results'
gt_path = '../scoring/gt_results'


def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def extract_ids(data):
    return {item['id'] for item in data if 'id' in item}

def compare_ids(model_data, gt_data):
    # Extract IDs
    model_ids = extract_ids(model_data)
    gt_ids = extract_ids(gt_data)
    
    # Compare IDs
    missing_in_model = gt_ids - model_ids
    unexpected_in_model = model_ids - gt_ids
    print(f"Length of missing in model: {len(missing_in_model)}, {len(gt_ids)}")
    print(f"Length of unexpected in model: {len(unexpected_in_model)}, {len(model_ids)}")

    if len(model_data) > 0 and model_data[0].get('name') == "Failed to execute query." :
        precision = 0
        recall = 0
        f1 = 0
        did_pass = False
        return did_pass, precision, recall, f1
    else:
        if len(model_ids) == 0:
            precision = 0
        else:
            precision = 1 - len(unexpected_in_model) / len(model_ids)
        
        if len(gt_ids) == 0:
            recall = 0
        else:
            recall = 1 - len(missing_in_model) / len(gt_ids)
        
        if precision + recall == 0:
            f1 = 0
        else:
            f1 = (2 * precision * recall) / (precision + recall)
        did_pass = len(missing_in_model) == 0 and len(unexpected_in_model) == 0
        # If there are no missing IDs and no unexpected IDs, then it's a pass
        return did_pass, precision, recall, f1

def process_model_results(model_results_path, gt_path):
    for model_folder in os.listdir(model_results_path):
        model_folder_path = os.path.join(model_results_path, model_folder)
        if not os.path.isdir(model_folder_path):
            continue  # Skip files, process only directories

        best_results = []
        for query_index, model_file in enumerate(os.listdir(model_folder_path)):
            print(f"Processing query {query_index}...")
            # Read the json file            
            model_file_path = os.path.join(model_folder_path, f'{query_index}.json')
            print(model_file_path)

            model_data = load_json(model_file_path)
            # Load the ground truth data
            gt_file_path = os.path.join(gt_path, f'{query_index}')
            print(gt_file_path)

            # Initialize precision and recall
            query_precision = []
            query_recall = []
            query_f1 = []
            query_did_pass = False

            # If question 21, then compare the exact query instead of the results, since the results are not deterministic
            if query_index == 20:
                # Load the query from the cleaned folder
                query_twenty = load_json(os.path.join('cleaned', f'{os.path.basename(model_folder_path)}.json'))[query_index]

                if query_twenty == "SELECT * FROM hotels ORDER BY RAND() LIMIT 1;" or query_twenty == "SELECT * FROM hotels ORDER BY RAND() LIMIT 1" or "ORDER BY RAND()" in query_twenty:
                    did_pass = True
                    precision = 1
                    recall = 1
                    f1 = 1
                else:
                    did_pass = False
                    precision = 0
                    f1 = 0
                    recall = 0
                best_results.append({
                    'query_index': query_index,
                    'precision': precision,
                    'recall': recall,
                    'did_pass': did_pass,
                    'f1': f1
                })
                continue

            for gt_file in os.listdir(gt_file_path):
                gt_data = load_json(os.path.join(gt_file_path, gt_file))
                did_pass, precision, recall, f1 = compare_ids(model_data, gt_data)
                query_precision.append(precision)
                query_recall.append(recall)
                query_f1.append(f1)
                if did_pass:
                    print(f"Query {query_index} passed.")
                    query_did_pass = True
                else:
                    print(f"Query {query_index} failed.")
            
            print(f"Query {query_index} precision: {query_precision}")
            print(f"Query {query_index} recall: {query_recall}")
            print(f"Query {query_index} did pass: {query_did_pass}")

            # If the query did not pass, find the max combined precision and recall
            if not query_did_pass:
                max_index = max(range(len(query_precision)), key=lambda i: query_f1[i])
                query_precision = query_precision[max_index]
                query_recall = query_recall[max_index]
                query_f1 = query_f1[max_index]
            
            else:
                query_precision = 1
                query_recall = 1
                query_f1 = 1

            best_results.append({
                'query_index': query_index,
                'precision': query_precision,
                'recall': query_recall,
                'did_pass': query_did_pass,
                'f1': query_f1
            })
            
            if not model_file_path.endswith('.json'):
                continue
        
        # Save the best results to a json file
        print(os.path.basename(model_folder_path))
        best_results_path = os.path.join('best_eval', f'{os.path.basename(model_folder_path)}.json')

        # Create the directory if it does not exist
        os.makedirs('best_eval', exist_ok=True)
        with open(best_results_path, 'w') as file:
            json.dump(best_results, file, indent=4)


# Process the model results and compare them with the ground truth
process_model_results(model_results_path, gt_path)
