import os
from sklearn.metrics import classification_report, confusion_matrix
from src.classify import classify_ticket
from src.dataset import load_dataset_split
from datetime import datetime
import time

#helepr fucntion to write to log file and to print to console
def log(message, file_handle):
    print(message)
    print(message, file=file_handle)

LOG_PATH = os.path.abspath("logs")

def main():
    dataset = load_dataset_split()
    instruction_list = dataset[1]["instruction"].tolist() #returns a list of instructions form test_df
    category_list = dataset[1]["category"].tolist() #returns a list of unique categories form train_df    



    #log file uses currents time for the file name
    now = datetime.now()
    time_compact = now.strftime("%H%M%S")


    count = 0
    total_pass = 0
    total_fail = 0

    true_labels = []
    predicted_labels = []

    #Calls classify ticket and passes in every line from instruction list then compares model output to expected answer to get an accuracy rating
    with open(os.path.join(LOG_PATH, "myfile" + time_compact + ".txt"), "w", encoding="utf-8") as f:
        for i in instruction_list:

            log("\nEvaluating message " + str(count+1) + " .....\n", f)

            response = classify_ticket(i)
            time.sleep(2) # Wait time to prevent exceeding groqs rate limit

            true_labels.append(category_list[count])
            predicted_labels.append(response)

            log("\nResponse: " + str(response), f)
            log("\nExpected response: " + category_list[count], f)
            if response == category_list[count]:
                total_pass += 1
                log("\nPASS\n", f)
            else:
                total_fail += 1
                log("FAIL\n", f)
            log("==================================================================\n", f)
            log("PASSED: " + str(total_pass) + " FAILED: " + str(total_fail), f)
            count += 1

        #tells how well model did for each category
        #Precision: how often a predicted category was actually correct.
        # Recall: how many of the examples for that category the model caught.
        # F1 score: a single score that combines precision and recall.
        # Support: how many cases of category is in test set
        log("\nClassification report:\n", f)
        log(classification_report(true_labels, predicted_labels), f)

        log("\nConfusion matrix:\n", f)
        log(str(confusion_matrix(true_labels, predicted_labels)), f)        

        log("\n==================================================================\n", f)
        accuracy = (total_pass / len(instruction_list))
        log(f"Accuracy: {accuracy:.2%}", f)

if __name__ == "__main__":
    main()
