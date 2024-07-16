import sqlite3


# Connect to the database
conn = sqlite3.connect('C:\\Users\\IRAN PC\\Downloads\\Database.NET.36.1.8930.1.x64\\Database.NET.36.1.8930.1.x64\\Database_Files\\shop.db')
c = conn.cursor()
def get_users_with_monthly_orders(city):
    query1 = f"""
    SELECT u.user_id, u.name
    FROM users u
    JOIN orders o ON u.user_id = o.user_id
    WHERE u.city = '{city}'
    GROUP BY u.user_id
    HAVING COUNT(DISTINCT strftime('%Y-%m', o.order_date)) >= 1
    """
    c.execute(query1)
    return c.fetchall()

def get_top_purchasers(start_date, end_date, limit=5):
    query2 = f"""
    SELECT u.user_id, u.name, COUNT(o.order_id) AS total_orders
    FROM users u
    JOIN orders o ON u.user_id = o.user_id
    WHERE o.order_date BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY u.user_id
    ORDER BY total_orders DESC
    LIMIT {limit}
    """
    c.execute(query2)
    purchasers = []
    for row in c.fetchall():
        user_id, name, total_orders = row
        purchasers.append((name, total_orders))
    return purchasers

def get_most_profitable_products(month):
    query3 = f"""
    SELECT p.product_id, p.name, SUM((pr.price - pr.discount) * o.quantity) AS total_profit
    FROM products p
    JOIN prices pr ON p.product_id = pr.product_id
    JOIN orders o ON p.product_id = o.product_id
    WHERE strftime('%m', o.order_date) = '{month}'
    GROUP BY p.product_id
    ORDER BY total_profit DESC
    LIMIT 1
    """
    c.execute(query3)
    return c.fetchall()

def get_least_popular_brands():
    query4 = """
    SELECT b.brand_id, b.name, COUNT(o.order_id) AS total_orders
    FROM brands b
    JOIN products p ON b.brand_id = p.brand_id
    JOIN orders o ON p.product_id = o.product_id
    GROUP BY b.brand_id
    ORDER BY total_orders ASC
    LIMIT 1
    """
    c.execute(query4)
    least_popular_brand = c.fetchone()
    if least_popular_brand:
        return [(least_popular_brand[1],)]
    else:
        return []
def get_brands_with_max_one_item_per_month(start_date, end_date):
    query5 = f"""
     SELECT b.name
     FROM brands b
     JOIN products p ON b.brand_id = p.brand_id
     JOIN orders o ON p.product_id = o.product_id
     WHERE o.order_date BETWEEN '{start_date}' AND '{end_date}'
     GROUP BY b.brand_id, strftime('%m', o.order_date)
    HAVING COUNT(o.order_id) <= 1
     """
    c.execute(query5)
    return [row[0] for row in c.fetchall()]
def get_top_changed_products(start_date, end_date, limit=1):
    query = f"""
    SELECT p.name
    FROM products p
    JOIN prices pr ON p.product_id = pr.product_id
    WHERE pr.start_date BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY p.product_id
    ORDER BY COUNT(pr.price_id) DESC
    LIMIT {limit}
    """
    c.execute(query)
    return [row[0] for row in c.fetchall()]


def get_monthly_profit_by_city(start_date, end_date):
    query = f"""
    SELECT u.city, strftime('%m', o.order_date) AS month, SUM((pr.price - pr.discount) * o.quantity) AS total_profit
    FROM users u
    JOIN orders o ON u.user_id = o.user_id
    JOIN prices pr ON o.product_id = pr.product_id
    WHERE o.order_date BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY u.city, month
    """
    c.execute(query)
    result = c.fetchall()
    monthly_profit_by_city = {}
    for row in result:
        if len(row) == 3:
            city, month, profit = row
            if city not in monthly_profit_by_city:
                monthly_profit_by_city[city] = {}
            monthly_profit_by_city[city][month] = profit
        else:
            print(f"Unexpected number of columns in the result: {len(row)}")
    return monthly_profit_by_city
def get_top_discount_users(start_date, end_date, limit=1):
    query = f"""
    SELECT u.name
    FROM users u
    JOIN orders o ON u.user_id = o.user_id
    JOIN prices pr ON o.product_id = pr.product_id
    WHERE o.order_date BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY u.user_id
    ORDER BY SUM(pr.discount * o.quantity) DESC
    LIMIT {limit}
    """
    c.execute(query)
    return [row[0] for row in c.fetchall()]
def main():
    while True:
        print("\nChoose an option:")
        print("1. Get users with monthly orders")
        print("2. Get top purchasers")
        print("3. Get most profitable products")
        print("4. Get least popular brands")
        print("5. Get brands with max one item per month")
        print("6. Get top changed products")
        print("7. Get monthly profit by city")
        print("8. Get top discount users")
        print("9. Exit")

        choice = input("Enter your choice (1-9): ")
        start_date = input("Enter start date (YYYY-MM-DD): ")
        end_date = input("Enter end date (YYYY-MM-DD): ")

        if choice == "1":
            city = input("Enter the city: ")
            users = get_users_with_monthly_orders(city)
            if not users:
                print(f"No users found with monthly orders in {city}.")
            else:
                user_names = [user[1] for user in users]
                print(f"Users with monthly orders in {city}: {', '.join(user_names)}")
        # Rest of the code remains the same
        elif choice == "2":
            start_date = input("Enter the start date (YYYY-MM-DD): ")
            end_date = input("Enter the end date (YYYY-MM-DD): ")
            limit = int(input("Enter the limit (default is 5): ") or 5)
            purchasers = get_top_purchasers(start_date, end_date, limit)
            if isinstance(purchasers, list):
                purchasers_str = [f"{name} ({count})" for name, count in purchasers]
                print(f"Top {limit} purchasers: {', '.join(purchasers_str)}")
            else:
                print(f"Unexpected data type returned from get_top_purchasers: {type(purchasers)}")
        elif choice == "3":
                month = int(input("Enter the month (1-12): "))
                products = get_most_profitable_products(str(month).zfill(2))
                if products:
                    print(f"Most profitable products for month {month}:")
                    for product_id, name, total_profit in products:
                        print(f"- {name} (Product ID: {product_id}) - Total Profit: {total_profit:.2f}")
                else:
                    print(f"No data available for month {month}.")
        elif choice == "4":
                least_popular_brands = get_least_popular_brands()
                if least_popular_brands:
                    brand_names = [brand_name for brand_name, in least_popular_brands]
                    print(f"Least popular brands: {', '.join(brand_names)}")
                else:
                    print("No least popular brands found.")
        elif choice == "5":
            brands = get_brands_with_max_one_item_per_month(start_date, end_date)
            print("Brands with max 1 item per month:")
            for brand in brands:
                print(brand)
        elif choice == "6":
                limit = int(input("Enter the limit (default is 1): ") or 1)
                changed_products = get_top_changed_products(start_date, end_date, limit)
                if isinstance(changed_products, list):
                    changed_product_names = changed_products
                    print(f"Top {limit} changed products: {', '.join(changed_product_names)}")
                else:
                    print(f"Unexpected data type returned from get_top_changed_products: {type(changed_products)}")
        elif choice == "7":
            monthly_profit_by_city = get_monthly_profit_by_city(start_date, end_date)
            for city, monthly_profit in monthly_profit_by_city.items():
                print(f"City: {city}")
                for month, profit in monthly_profit.items():
                    print(f"Month: {month}, Profit: {profit}")
        elif choice == "8":
                        limit = int(input("Enter the limit (default is 1): ") or 1)
                        discount_users = get_top_discount_users(start_date, end_date, limit)
                        if isinstance(discount_users, list):
                            print(f"Top {limit} discount users: {', '.join(discount_users)}")
                        else:
                            print(f"Unexpected data type returned from get_top_discount_users: {type(discount_users)}")
        elif choice == "9":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

def update_price(product_id, price, start_date, end_date):

    query = """
    UPDATE prices
    SET price = ?, start_date = ?, end_date = ?
    WHERE product_id = ?
    """
    c.execute(query, (price, start_date, end_date, product_id))
    conn.commit()
    print(f"Price for product {product_id} updated successfully.")


def add_product(product_id, name, description, brand_id, created_at):

    query = """
    INSERT INTO products (product_id, name, description, brand_id, created_at)
    VALUES (?, ?, ?, ?, ?)
    """
    c.execute(query, (product_id, name, description, brand_id, created_at))
    conn.commit()
    print(f"New product {name} added successfully.")


def update_product(product_id, name, description):

    query = """
    UPDATE products
    SET name = ?, description = ?
    WHERE product_id = ?
    """
    c.execute(query, (name, description, product_id))
    conn.commit()
    print(f"Product {product_id} updated successfully.")


def delete_product(product_id):

    query = """
    DELETE FROM products
    WHERE product_id = ?
    """
    c.execute(query, (product_id,))
    conn.commit()
    print(f"Product {product_id} deleted successfully.")


def add_inventory(inventory_id, product_id, quantity):

    query = """
    INSERT INTO inventory (inventory_id, product_id, quantity)
    VALUES (?, ?, ?)
    """
    c.execute(query, (inventory_id, product_id, quantity))
    conn.commit()
    print(f"New inventory added for product {product_id}.")


def update_inventory(product_id, quantity):

    query = """
    UPDATE inventory
    SET quantity = ?
    WHERE product_id = ?
    """
    c.execute(query, (quantity, product_id))
    conn.commit()
    print(f"Inventory for product {product_id} updated successfully.")


def delete_inventory(product_id):

    query = """
    DELETE FROM inventory
    WHERE product_id = ?
    """
    c.execute(query, (product_id,))
    conn.commit()
    print(f"Inventory for product {product_id} deleted successfully.")


def add_price(price_id, product_id, price, discount, start_date, end_date):

    query = """
    INSERT INTO prices (price_id, product_id, price, discount, start_date, end_date)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    c.execute(query, (price_id, product_id, price, discount, start_date, end_date))
    conn.commit()
    print(f"New price added for product {product_id}.")


def update_price_and_discount(product_id, price, discount):

    query = """
    UPDATE prices
    SET price = ?, discount = ?
    WHERE product_id = ?
    """
    c.execute(query, (price, discount, product_id))
    conn.commit()
    print(f"Price and discount for product {product_id} updated successfully.")


def search_products_by_name_or_description(conn, search_term):
    query = f"""
    SELECT *
    FROM products
    WHERE name LIKE '%{search_term}%' OR description LIKE '%{search_term}%'
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def filter_products_by_price_and_satisfaction(conn, min_price, max_price, satisfaction_level):
    query = f"""
    SELECT p.*, pr.price, i.quantity, o.satisfaction_level
    FROM products p
    JOIN prices pr ON p.product_id = pr.product_id
    JOIN inventory i ON p.product_id = i.product_id
    JOIN orders o ON p.product_id = o.product_id
    WHERE pr.price BETWEEN {min_price} AND {max_price}
    AND o.satisfaction_level = '{satisfaction_level}'
    ORDER BY pr.price ASC
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def place_order(user_id, product_id, quantity, comment, satisfaction_level):

    query = """
    INSERT INTO orders (user_id, product_id, quantity, comment, satisfaction_level)
    VALUES (?, ?, ?, ?, ?)
    """
    c.execute(query, (user_id, product_id, quantity, comment, satisfaction_level))
    conn.commit()
    print("Order placed successfully!")

def update_order(order_id, comment, satisfaction_level):

    query = """
    UPDATE orders
    SET comment = ?, satisfaction_level = ?
    WHERE order_id = ?
    """
    c.execute(query, (comment, satisfaction_level, order_id))
    conn.commit()
    print("Order updated successfully!")

def these():
    conn = sqlite3.connect(
    'C:\\Users\\IRAN PC\\Downloads\\Database.NET.36.1.8930.1.x64\\Database.NET.36.1.8930.1.x64\\Database_Files\\shop.db')
    c = conn.cursor()

    if conn:
        while True:
            print("1. Search products by name or description")
            print("2. Filter products by price and satisfaction")
            print("3. Exit")
            choice = int(input("Enter your choice (1, 2, or 3): "))

            if choice == 1:
                search_term = input("Enter the search term: ")
                results = search_products_by_name_or_description(conn, search_term)
                for row in results:
                    print(row)
            elif choice == 2:
                min_price = float(input("Enter the minimum price: "))
                max_price = float(input("Enter the maximum price: "))
                satisfaction_level = input("Enter the satisfaction level (e.g., Satisfied, Dissatisfied): ")
                results = filter_products_by_price_and_satisfaction(conn, min_price, max_price, satisfaction_level)
                for row in results:
                    print(row)
            elif choice == 3:
                print("Exiting the program. Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1, 2, or 3.")

        conn.close()
    else:
        print("Error connecting to the database.")


these()

def switch_case():
    """
    Executes the appropriate function based on user input.
    """
    print("Available functions:")
    for func in functions:
        print(f"- {func}")

    function_name = input("Enter the function name: ")

    if function_name in functions:
        args = []
        func_params = functions[function_name].__annotations__
        for param, param_type in func_params.items():
            if param != "return":
                arg = input(f"Enter the value for {param} ({param_type.__name__}): ")
                if param_type == int:
                    args.append(int(arg))
                elif param_type == float:
                    args.append(float(arg))
                else:
                    args.append(arg)
        functions[function_name](*args)
    else:
        print(f"Error: '{function_name}' is not a valid function name.")

def update_price(product_id: int, price: float, start_date: str, end_date: str):

    print(f"Updating price for product {product_id} to {price} from {start_date} to {end_date}")


def add_product(product_id: int, name: str, description: str, brand_id: int, created_at: str):

    print(f"Adding new product with ID {product_id}, name '{name}', description '{description}', brand ID {brand_id}, created at {created_at}")

def update_product(product_id: int, name: str, description: str):

    print(f"Updating product with ID {product_id}, name to '{name}', description to '{description}'")

def delete_product(product_id: int):

    print(f"Deleting product with ID {product_id}")

def add_inventory(inventory_id: int, product_id: int, quantity: int):

    print(f"Adding inventory with ID {inventory_id} for product {product_id}, quantity {quantity}")

def update_inventory(product_id: int, quantity: int):

    print(f"Updating inventory for product {product_id}, new quantity {quantity}")

def delete_inventory(product_id: int):

    print(f"Deleting inventory for product {product_id}")

def add_price(price_id: int, product_id: int, price: float, discount: float, start_date: str, end_date: str):

    print(f"Adding new price with ID {price_id} for product {product_id}, price {price}, discount {discount}, from {start_date} to {end_date}")

def update_price_and_discount(product_id: int, price: float, discount: float):

    print(f"Updating price and discount for product {product_id}, new price {price}, new discount {discount}")

def place_order(user_id: int, product_id: int, quantity: int, comment: str, satisfaction_level: str):

    print(f"Placing new order for user {user_id}, product {product_id}, quantity {quantity}, comment '{comment}', satisfaction level '{satisfaction_level}'")

def update_order(order_id: int, comment: str, satisfaction_level: str):

    print(f"Updating order {order_id}, new comment '{comment}', new satisfaction level '{satisfaction_level}'")

functions = {
    'update_price': update_price,
    'add_product': add_product,
    'update_product': update_product,
    'delete_product': delete_product,
    'add_inventory': add_inventory,
    'update_inventory': update_inventory,
    'delete_inventory': delete_inventory,
    'add_price': add_price,
    'update_price_and_discount': update_price_and_discount,
    'place_order': place_order,
    'update_order': update_order
}
switch_case()

