import os
from classify import classify_ticket
from dataset import load_dataset_split
from datetime import datetime
import time

dataset = load_dataset_split()
instruction_list = dataset[1]["instruction"].tolist() #returns a list of instructions form test_df
category_list = dataset[1]["category"].tolist() #returns a list of unique categories form train_df    



#log file uses currents time for the file name
now = datetime.now()
time_compact = now.strftime("%H%M%S")


#helepr fucntion to write to log file and to print to console
def log(message, file_handle):
    print(message)
    print(message, file=file_handle)

LOG_PATH = os.path.abspath("logs")

count = 0
total_pass = 0
total_fail = 0

#Calls classify ticket and passes in every line from instruction list then compares model output to expected answer to get an accuracy rating
with open(os.path.join(LOG_PATH, "myfile" + time_compact + ".txt"), "w") as f:
    for i in instruction_list:
        log("\nEvaluating message " + str(count+1) + " .....\n", f)
        response = classify_ticket(i)
        time.sleep(2) # Wait time to prevent exceeding groqs rate limit
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

    log("\n==================================================================\n", f)
    accuracy = (total_pass / len(instruction_list))
    log(f"Accuracy: {accuracy:.2%}", f)

