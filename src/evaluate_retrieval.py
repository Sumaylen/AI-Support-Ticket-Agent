import os
import pandas as pd
from datetime import datetime
from src.retrieval import retrieve

K_VALUES = [1, 3, 5, 10]
MAX_K = max(K_VALUES)  # retrieve this many chunks once, then slice for smaller k

# q = customer question, expected = file(s) that should be retrieved
TEST_CASES = [
    {"q": "My card got declined at checkout, what happens to my order?", "expected": ["failed-payment.md"]},
    {"q": "Can I pay with bitcoin or a bank transfer?", "expected": ["accepted-payment-methods.md"]},
    {"q": "Can I split one order across two credit cards?", "expected": ["accepted-payment-methods.md"]},
    {"q": "My password reset link doesn't work anymore", "expected": ["password-reset.md"]},
    {"q": "Why was my account locked after I typed the wrong password a few times?", "expected": ["password-reset.md"]},
    {"q": "How long until a refund shows up on my card?", "expected": ["refund-timeline.md"]},
    {"q": "Can I get my money back for a sale item?", "expected": ["refund-policy.md"]},
    {"q": "I want to return a worn jacket I bought 2 weeks ago, will I get a refund?", "expected": ["refund-eligibility.md", "refund-policy.md"]},
    {"q": "Can I cancel my order? It already says shipped.", "expected": ["order-cancellation.md"]},
    {"q": "I cancelled my order yesterday, when will I get my money back?", "expected": ["order-cancellation.md", "refund-timeline.md"]},
    {"q": "How do I stop my monthly box from billing me?", "expected": ["subscription-cancellation.md"]},
    {"q": "Can I pause my subscription for a couple of months?", "expected": ["subscription-management.md"]},
    {"q": "Do you ship to Australia and how long does it take?", "expected": ["international-shipping.md"]},
    {"q": "How much does overnight shipping cost?", "expected": ["shipping-options.md"]},
    {"q": "Tracking says delivered but I never received my package", "expected": ["lost-or-damaged-packages.md"]},
    {"q": "I need an invoice with my company name and tax ID", "expected": ["invoice-requests.md"]},
    {"q": "Is there a phone number I can call?", "expected": ["contacting-support.md"]},
    {"q": "Will I be charged VAT if I order to Germany?", "expected": ["tax-and-vat.md"]},
    {"q": "Can I delete my account while I'm waiting for an order to arrive?", "expected": ["account-deletion.md"]},
    {"q": "How do I track an order I placed as a guest?", "expected": ["order-tracking.md"]},
]

# Retrieves once per question, calculates hit, recall, and precision for each k, and records failures at MAX_K.
def main():
    hit_k = []
    recall_k = [] 
    precision_k = []
    retreive_failed = []
    all_chunks = []
    
    #use MAX_k to call retreieve for the highets k in K_VALUES to avoid unecessary calls
    for test in TEST_CASES:
        all_chunks.append(retrieve(test["q"], MAX_K))

    #loop through all k values
    for k in K_VALUES:
        # Hit@k returns 1 if at least 1 relevant file is found
        hit_k_count = 0 
        recall_k_count= 0 
        precision_k_count= 0 
        test_number = 0
        #loop through all test cases
        for test in TEST_CASES:
            #retrieve k chunks for each test case from all_chunks
            chunk = all_chunks[test_number][:k]
            test_number += 1
            #helper function calls
            hit = check_hit(chunk, test)
            #checks if there is 0 matches even in MAX_K (usaully would mean a test error)
            if hit == 0 and k == MAX_K:
                retreive_failed.append(test)
            hit_k_count += hit
            recall_k_count += recall_and_precision(chunk, test)[0]
            precision_k_count += recall_and_precision(chunk, test)[1]
         
        hit_k.append(hit_k_count/len(TEST_CASES))
        recall_k.append(recall_k_count/len(TEST_CASES))
        precision_k.append((precision_k_count/k)/len(TEST_CASES))
        
    return hit_k, recall_k, precision_k, retreive_failed 

def check_hit(chunk,test):
 #loop through every chunk for each test case
    found = False
    for ch in chunk:
        #compare every source chunk to test expected chunk
        if ch["source"] in test["expected"]:
            found = True
            break   
    if found:
        return 1
    else:
        return 0

def recall_and_precision(chunk, test):
    retrieved_sources = []
    #loop through every chunk for each test case
    for ch in chunk:
        #append every source to list
        retrieved_sources.append(ch["source"])
    matched_expected = 0
    for retrieved_source in retrieved_sources:
    #loop through every expected test case
        for expected_file in test["expected"]:
            # Count each retrieved chunk whose source matches an expected file (including duplicates).
            if retrieved_source == expected_file:
                 matched_expected += 1

    #dict.fromkeys() is a method creates a dictionary where each list item becomes a key and keys can't repeat
    #then convert it back to a list
    unique_sources = list(dict.fromkeys(retrieved_sources))
    matched_unique_expected = 0
    #loop through every unique sources
    for unique_source in unique_sources:
        #loop through every expected test case
        for expected_file in test["expected"]:
            # Count each retrieved chunk whose source matches an expected file (unqiue only).
            if unique_source == expected_file:
                matched_unique_expected += 1

    recall_score = matched_unique_expected / len(test["expected"])
    return recall_score, matched_expected


#log file uses currents time for the file name
now = datetime.now()
time_compact = now.strftime("%H%M%S")


#helepr fucntion to write to log file and to print to console
def log(message, file_handle):
    print(message)
    print(message, file=file_handle)

LOG_PATH = os.path.abspath("logs")

def run_evaluation():
    run = main()
    data = {"hit_k": run[0],
            "recall_k": run[1],
            "precision_k": run[2]}
    df = pd.DataFrame(data, index=K_VALUES)
    df.index.name = 'k_value'

    with open(os.path.join(LOG_PATH, "myfile" + time_compact + ".txt"), "w", encoding="utf-8") as f:
        log("Retrieval results for " + str(len(TEST_CASES))  +" test cases\n", f)

        log("Metric definitions".center(60, "="), f)

        log("- Hit@k: 1 if at least one expected file appears in the top k, otherwise 0. This is the most forgiving metric: did we get anything useful?\n",f)
        log("- Recall@k: fraction of expected files that appear in the top k. This asks: did we find everything we needed?\n",f)
        log("- Precision@k: fraction of the top k chunks that came from an expected file. This asks: how much of what we retrieved is useful, and how much is noise?\n",f)
    
        log("Retrieval Results".center(60, "="), f)
        log(df.round(2), f)

        log("\nFailures (expected file missing from the MAX_K)".center(60, "="),f)
        if not run[3]:
            log("\nNo retrieval failures", f)
        else:
            log("\n",f)
            log(run[3], f)

if __name__ == "__main__":
    run_evaluation()
