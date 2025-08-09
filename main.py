import datetime
import sqlite3

class Store:
    def __init__(self):
        self.conn = sqlite3.connect("store.db")
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                category TEXT,
                price REAL
            );
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT UNIQUE
            );
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                order_date TEXT,
                FOREIGN KEY(customer_id) REFERENCES customer(id),
                FOREIGN KEY(product_id) REFERENCES product(id)
            );
            """
        )

    
    def insert_simple_data(self):
        self.cursor.execute(
            "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
            ("iPhone 13", "Смартфони", "1399.99"),
        )

        self.cursor.execute(
            "SELECT id FROM customer WHERE email = ?", ("oleg@example.com",)
        )
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO customer (first_name, last_name, email) VALUES (?, ?, ?)",
                ("Олег", "Петренко", "oleg@example.com"),
            )
        
        self.cursor.execute(
            "INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?)",
            (1, 1, 2, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )

        self.cursor.execute(
            "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
            ("Samsung Galaxy S21", "Смартфони", "1199.99"),
        )

        self.cursor.execute(
            "SELECT id FROM customer WHERE email = ?", ("maria@example.com",)
        )
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO customer (first_name, last_name, email) VALUES (?, ?, ?)",
                ("Марія", "Іванова", "maria@example.com"),
            )
        
        self.cursor.execute(
            "INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?)",
            (2, 2, 1, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )

        self.conn.commit()

    def total_sales(self):
        result = self.cursor.execute(
            """
            SELECT SUM(p.price * o.quantity)
            FROM orders o
            JOIN products p ON o.product_id = p.id
            """
        ).fetchall()

        print(f"Загальний обсяг продажів: {result[0][0]} грн")

    def most_popular_category(self):
        result = self.cursor.execute(
            """
            SELECT p.category, COUNT(*) AS count
            FROM orders o
            JOIN products p ON o.product_id = p.id
            GROUP BY p.category
            ORDER BY count DESC
            LIMIT 1
            """
        ).fetchall()

        print(f"Найпопулярніша категрія: {result[0][0]}")

    def insert_order(self, customer_id, product_id, quantity):
        order_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?)",
            (customer_id, product_id, quantity, order_date),
        )

    def orders_per_customer(self):
        result = self.cursor.execute(
            """
            SELECT c.first_name || ' ' || c.last_name AS customer, COUNT(o.id) AS total_orders
            FROM customer c
            LEFT JOIN orders o ON c.id = o.customer_id
            GROUP BY c.id
            """
        ).fetchall()
        for row in result:
            print(f"{row[0]} – {row[1]} замовлень")
            
    def average_order_value(self):
        result = self.cursor.execute(
            """
            SELECT AVG(p.price * o.quantity)
            FROM orders o
            JOIN products p ON o.product_id = p.id
            """
        ).fetchone()
        
        print(f"Середній чек замовлення: {result[0]:.2f} грн")

    def product_per_category(self):
        result = self.cursor.execute(
            """
            SELECT category, COUNT(*) FROM products GROUP BY category
            """
        ).fetchall()

        for category, count in result:
            print(f"Категорія: {category} - {count} товарів")

    def update_prices(self):
        self.cursor.execute(
            "UPDATE products SET price = price * 1.10 WHERE category = 'смартфони'"
        )
        print("Ціни на смартфони оновлено на +10%")

    def run_cli(self):
        while True:
            print("\n📋 --- МЕНЮ ---")
            print("1. ➕ Додати товар")
            print("2. 👤 Додати клієнта")
            print("3. 🛒 Створити замовлення")
            print("4. 💰 Сумарний обсяг продажів")
            print("5. 📦 Кількість замовлень на клієнта")
            print("6. 💸 Середній чек замовлення")
            print("7. 🏆 Найпопулярніша категорія")
            print("8. 📊 Кількість товарів по категоріях")
            print("9. 📈 Збільшити ціни на смартфони на 10%")
            print("10. 💾 Зберегти зміни в базі")
            print("0. 🚪 Вихід")

            choice = input("Введіть номер опції: ")

            if choice == "1":
                name = input("Назва товару: ")
                category = input("Кагорія (смартфони/ноутбуки/планшети): ")
                price = float(input("Ціна: "))
                self.cursor.execute(
                    "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
                    (name, category, price),
                )
                print("Товар додано")

            elif choice == "2":
                first = input("Ім'я: ")
                last = input("Прізвище: ")
                email = input("Email: ")
                try:
                    self.cursor.execute(
                        "INSERT INTO customers (first_name, last_name, email) VALUES (?, ?, ?)",
                        (first, last, email),
                    )
                    print("Клієнта додано!")
                except sqlite3.IntegrityError:
                    print("Email вже існує!")

            elif choice == "3":
                try:
                    cid = int(input("ID клієнта: "))
                    pid = int(input("ID товару: "))
                    qty = int(input("Кількість: "))
                    self.insert_order(cid, pid, qty)
                    print("Замовлення додано")
                except Exception as e:
                    print("Помилка при створенні замовлення:", e)

            elif choice == "4":
                self.total_sales()

            elif choice == "5":
                self.orders_per_customer()

            elif choice == "6":
                self.average_order_value()

            elif choice == "7":
                self.most_popular_category()

            elif choice == "8":
                self.product_per_category()

            elif choice == "9":
                self.update_prices()

            elif choice == "10":
                self.conn.commit()

            elif choice == "0":
                self.conn.close()
                print("Гарного дня!")
                break
                
            else:
                print("Невідома команда. Спробуйте ще раз")
                
                
if __name__ == "__main__":
    store = Store()
    store.create_tables()
    store.insert_simple_data()
    store.run_cli()

