import sqlite3

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up the order status, order item, and expected delivery date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer"},
                    "account_id": {"type": "integer"}
                },
                "required": ["order_id", "account_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_account_info",
            "description": "Look up the account status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {"type": "integer"}
                },
                "required": ["account_id"]
            }
        }
    }
]
#Tool to get order status, order item and expected_delivery
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

#Tool to get account plan
def get_account_info(account_id):
     conn = sqlite3.connect("data/company.db")
     cursor = conn.cursor()     
     cursor.execute(
            "SELECT plan FROM accounts WHERE account_id = ?",
            (account_id,),
            )
     result = cursor.fetchone()
     conn.close()
     return result

