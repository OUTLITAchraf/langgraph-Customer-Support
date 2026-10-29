from db.transactions import find_customer_transactions


def main():
    email = "customer@example.com"

    transactions = find_customer_transactions(email)

    print(f"Transactions found: {len(transactions)}")

    for transaction in transactions:
        print(
            transaction["transaction_reference"],
            transaction["amount"],
            transaction["currency"],
            transaction["status"],
        )


if __name__ == "__main__":
    main()