import sqlite3

def get_order_status(order_id, account_id=None):
    conn = sqlite3.connect("data/company.db")
    cursor = conn.cursor()        

    #Only fetch item data if orderd id corresponds to the account id
    cursor.execute(
            "SELECT status, item, expected_delivery FROM orders WHERE order_id = ? AND account_id = ?",
            (order_id, account_id),
        )

    result = cursor.fetchone()
    conn.close()
    return result

print(get_order_status(4501, 1013))