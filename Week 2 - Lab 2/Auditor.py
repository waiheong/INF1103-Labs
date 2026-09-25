total_inventory = 0 
total_processed = 0
failed_entries = 0

while True:
    user_input = input("Enter stock quantity or type 'quit' to end the program:")

    if user_input.lower() == "quit":
        break
    elif not user_input.isdigit():
        print("Error: Please enter a valid whole number.")
        failed_entries += 1
        continue
    else:
        quantity = int(user_input)
        if quantity < 0:
            print("Error: Negative number are not allowed. Try again!")
            failed_entries += 1
            continue
        else:
            total_inventory += quantity
            total_processed += 1
    if total_inventory > 500:
        print("ALERT: Inventroy exceeds 500 units.")
        break

print(f"Rotal Units processed: {total_processed}")
print(f"Number of Failed / Rejected Entries: {failed_entries}")
        