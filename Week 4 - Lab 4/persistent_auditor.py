#import json and file path libraries
import json
from pathlib import Path

#creating a orders.txt file
ORDERS_FILE = Path(__file__).parent / "orders.txt"

#checking for the highest orders id and auto increment from there
def get_next_order_id(orders):
    highest_id = 0

    for order in orders:
        order_id = str(order.get("id", ""))
        if order_id.startswith("UUID"):
            number = order_id[4:]
            if number.isdigit():
                highest_id = max(highest_id, int(number))

    return highest_id + 1

#read and load all save orders from order.txt
def load_orders():
    try:
        with open(ORDERS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

#write and save all orders to orders.txt
def save_orders(orders):
    with open(ORDERS_FILE, "w") as file:
        json.dump(orders, file, indent=4)

    print("\nOrders successfully saved to orders.txt")

#getting a valid quantity from user input
def get_quantity():
    quantity = input("Enter Product Quantity: ")

    if not quantity.isdigit():
        print("Error: Enter a valid whole number.")
        return None

    return int(quantity)

#displaying all orders
def display_orders(orders):
    if not orders:
        print("\nNo orders found.")
        return

    print("\nCurrent Orders:")
    for order in orders:
        print(
            f"{order['id']} : "
            f"{order['name']} | "
            f"{order['quantity']}"
        )

#adding new orders
def add_order(total_inventory, history, orders):
    order_name = input("\nEnter Product Name: ")
    quantity = get_quantity()

    if quantity is None:
        return total_inventory

    order_id = f"UUID{get_next_order_id(orders)}"
    order = {
        "id": order_id,
        "name": order_name,
        "quantity": quantity
    }

    orders.append(order)
    history.append({
        "id": order_id,
        "name": order_name,
        "quantity": quantity
    })
    total_inventory += quantity

    print(
        f"\nNew Order added:"
        f"\n{order['id']},{order['name']},{order['quantity']}"
    )
    save_orders(orders)
    return total_inventory

#editing orders by using UUID
def edit_order(total_inventory, history, orders):
    order_id = input("\nEnter the UUID of the order to edit: ")

    for index, order in enumerate(orders):
        if order["id"] == order_id:
            print(f"Current Order: {order['name']},{order['quantity']}")

            new_name = input("\nEnter New Product Name: ")
            new_quantity = get_quantity()

            if new_quantity is None:
                return total_inventory

            old_quantity = order["quantity"]

            order["name"] = new_name
            order["quantity"] = new_quantity

            total_inventory -= old_quantity
            total_inventory += new_quantity

            history[index] = {
                "id": order_id,
                "name": new_name,
                "quantity": new_quantity
            }

            save_orders(orders)
            return total_inventory

    print("Order UUID not found.")
    return total_inventory

#main function running in a loop until user quits the program
def main():
    orders = load_orders()
    history = [
        {
            "id": order.get("id", ""),
            "name": order.get("name", ""),
            "quantity": order.get("quantity", 0)
        }
        for order in orders
    ]
    total_inventory = sum(order.get("quantity", 0) for order in orders)

    display_orders(orders)

    while True:
        print("\n1. Add order")
        print("2. Edit order by UUID")
        print("3. Display orders")
        print("4. Quit")

        choice = input("Choose an option: ")

        if choice == "1":
            total_inventory = add_order(
                total_inventory,
                history,
                orders
            )

        elif choice == "2":
            total_inventory = edit_order(
                total_inventory,
                history,
                orders
            )

        elif choice == "3":
            display_orders(orders)

        elif choice == "4" or choice.lower() == "quit":
            print("Successfully exited the program.")
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()