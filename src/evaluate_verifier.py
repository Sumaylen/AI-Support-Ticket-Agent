
from src.retrieval import retrieve
from src.respond import check_faithfulness
from datetime import datetime
import os

TOP_K = 10  #

# q = customer question, good = reply that only uses facts from the knowledge base,
# bad = reply that mixes in invented or wrong claims
TEST_CASES = [
    {
        "q": "My card got declined at checkout, what happens to my order?",
        "good": "I'm sorry your payment didn't go through. Your order is held in Payment Pending status for 24 hours, so you can update your payment method to complete it. If no valid payment is provided in that time, the order is cancelled automatically.",
        "bad": "I'm sorry your payment didn't go through. Your order is held in Payment Pending status for 72 hours so you can update your payment method. Our support team can also see the exact reason the bank declined it.",
    },
    {
        "q": "Can I pay with bitcoin or a bank transfer?",
        "good": "Thanks for asking! We don't currently support bank transfers or cryptocurrency. You can pay with Visa, Mastercard, American Express, Discover, PayPal or Apple Pay.",
        "bad": "Thanks for asking! We accept bitcoin as well as Visa, Mastercard, American Express and Discover cards. Bank transfers are not supported.",
    },
    {
        "q": "How long until a refund shows up on my card?",
        "good": "Once your returned item is received and inspected, the refund is processed within 3 business days. After that it usually takes another 5-10 business days to appear on your statement, depending on your bank.",
        "bad": "Refunds are processed within 24 hours of you requesting the return, and they appear on your statement instantly after that.",
    },
    {
        "q": "Can I get my money back for a sale item?",
        "good": "Sale and clearance items are eligible for store credit only, not a refund to your original payment method, unless the item arrived damaged or defective.",
        "bad": "Sale items can be refunded to your original payment method within 60 days of purchase as long as they're unused.",
    },
    {
        "q": "Can I cancel my order? It already says shipped.",
        "good": "I'm sorry, but once an order has moved to Shipped it can no longer be cancelled. Instead, you can return it after delivery by following the standard return process.",
        "bad": "Shipped orders can still be cancelled for a full refund if you contact us within 24 hours. I've gone ahead and cancelled it for you.",
    },
    {
        "q": "Why was my account locked after a few wrong password attempts?",
        "good": "That's frustrating, sorry. After three failed login attempts within 15 minutes, an account is temporarily locked for 30 minutes as a security measure, and unfortunately that lock can't be lifted early, even by our support team.",
        "bad": "That's frustrating, sorry. After three failed login attempts the account is locked for 2 hours, but our support team can unlock it right away once you verify your identity.",
    },
    {
        "q": "Do you ship to Australia and how long does it take?",
        "good": "Yes, we ship to Australia. International orders take 10-20 business days depending on customs processing, and import duties or customs fees are the customer's responsibility. Expedited and Overnight shipping aren't available for international orders.",
        "bad": "Yes, we ship to Australia and orders usually arrive in 3-5 business days. Duties and customs fees are included in your order total, and Overnight shipping is available.",
    },
    {
        "q": "I need an invoice with my company name and tax ID.",
        "good": "Thanks for reaching out. A basic receipt is emailed at purchase, but for a formal invoice with your business name and tax ID, contact support with your order number and billing details. Formal invoices are typically issued within 2 business days.",
        "bad": "We can issue that invoice immediately, and we can also change the purchase date to the start of the month if that helps your expense report.",
    },
]

def main():
    with open(os.path.join(LOG_PATH, "myfile" + time_compact + ".txt"), "w", encoding="utf-8") as f:
        passed =  0
        failed_good = []
        failed_bad = []
        count = 1
        #loop through every test case
        for test in TEST_CASES:
            log("\nEvaluating message " + str(count) + " .....\n", f)
            log("Question: " + test["q"], f)
            #retrieve relevant chunks for each question
            chunks = retrieve(test["q"], TOP_K)
            good = check_good(test["good"], chunks)
            log("\nGood reply: " + test["good"], f)
            log("\nResponse: " + good[1], f)
            log("\nExpected response: true", f)
            # verification of the good reply passed
            if good[0] == True:
                passed += 1
                log("\nPASS\n", f)
            else:
                failed_good.append({"question": test["q"], "good":test["good"], "reasoning": good[1] })
                log("\nFAIL\n", f)

            bad = check_bad(test["bad"], chunks)
            log("\nBad reply: " + test["bad"], f)
            log("\nResponse: " + bad[1], f)
            log("\nExpected response: false", f)
            # rejection of a bad reply failed
            if bad[0] == True:
                passed += 1
                log("\nPASS\n", f)
            else:
                failed_bad.append({"question": test["q"], "bad":test["bad"], "reasoning": bad[1] })
                log("\nFAIL\n", f)
            log("PASSED: " + str(passed) + " FAILED: " + str(len(failed_good) + len(failed_bad)), f)
            log("\n==================================================================\n", f)
            count += 1
        accuracy = (passed / (2 * len(TEST_CASES))) * 100
        log("\nPASSED: " + str(passed) + " FAILED: " + str(len(failed_good) + len(failed_bad)), f)
        log("\nFailed good replies:\n", f)
        if not failed_good:
            log("None", f)
        for failure in failed_good:
            log("Question: " + failure["question"], f)
            log("Reply: " + failure["good"], f)
            log("Reason: " + failure["reasoning"] + "\n", f)
        log("\nFailed bad replies:\n", f)
        if not failed_bad:
            log("None", f)
        for failure in failed_bad:
            log("Question: " + failure["question"], f)
            log("Reply: " + failure["bad"], f)
            log("Reason: " + failure["reasoning"] + "\n", f)
        log("\n==================================================================\n", f)
        log(f"Accuracy: {accuracy:.2f}%", f)

# Checks whether the verifier accepts a good reply;
def check_good(msg, chunks):
    isGood = check_faithfulness(msg, chunks)
    if isGood.content.strip().lower().startswith("true"):
        return True , isGood.content
    else:
        return False , isGood.content

# Checks whether the verifier rejects a bad reply;
def check_bad(msg, chunks):
    isBad = check_faithfulness(msg, chunks)
    if isBad.content.strip().lower().startswith("false"):
        return True , isBad.content   
    else:
        return False , isBad.content   


#log file uses currents time for the file name
now = datetime.now()
time_compact = now.strftime("%H%M%S")


#helepr fucntion to write to log file and to print to console
def log(message, file_handle):
    print(message)
    print(message, file=file_handle)

LOG_PATH = os.path.abspath("logs")

if __name__ == "__main__":
    main()
