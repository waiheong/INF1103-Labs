#Week 3 - Lab 3

#for user input and validation
def get_validIinput():
    user_input = input("Enter stock quantity or type 'quit' to end the program:")
    if user_input.lower() == "quit":
        return "quit"
    if not user_input.isdigit():
        print("Error: Please enter a valid whole number.")
        return None
    quantity = int(user_input)
    if quantity < 0:
        print("Error: Negative number are not allowed. Try again!")
        return None
    return quantity

#for delivery
def process_delivery(current_total, new_total):
    return current_total + new_total

#for tax
def calculate_tax(amount):
    return amount * 0.10

#for report
def generate_report(total_units, fail_attempts):
    print(f"Rotal Units Processed: {total_units}")
    print(f"Number of Failed / Rejected Entries: {fail_attempts}")

#for main
def main():
    total_inventory = 0 
    total_processed = 0
    failed_entries = 0

    while True:
        result = get_validIinput()

        if result == "quit":
            break
        if result is None:
            failed_entries += 1
            continue

        print(f"Delivery tax is: {calculate_tax(result):.2f}") #showing 2 decimal point.

        total_inventory = process_delivery(total_inventory, result)
        total_processed += 1

        if total_inventory > 500:
            print("ALERT: Inventroy exceeds 500 units.")
            break

    generate_report(total_processed, failed_entries)

if __name__ == "__main__":
    main()



