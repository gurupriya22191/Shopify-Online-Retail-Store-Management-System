
import streamlit as st
import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Luvuhmom@78",
    database="project8"
)
cursor = db.cursor()

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None


# Function to execute SQL queries and display results
def execute_query(sql_query):
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
        st.write(result)
    except mysql.connector.Error as err:
        st.error(f"Error executing SQL query: {err}")


# Registration Section
def register_user():
    st.header("Register New Customer")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    user_age = st.number_input("Age", min_value=0, max_value=150, value=18)
    user_phone = st.text_input("Phone Number")
    if st.button("Register"):
        if username and email and password:
            try:
                # Check if user already exists
                cursor.execute("SELECT * FROM user WHERE user_email = %s", (email,))
                existing_user = cursor.fetchone()
                if existing_user:
                    st.warning("User already exists. Please login.")
                else:
                    # Insert new user into the database
                    cursor.execute(
                        "INSERT INTO user (user_name, user_email, user_password, user_age, user_phone) VALUES (%s, %s, %s, %s, %s)",
                        (username, email, password, user_age, user_phone))
                    db.commit()
                    st.success("User registered successfully!")
            except mysql.connector.Error as err:
                st.error(f"Error registering user: {err}")
        else:
            st.warning("Please fill in all required fields.")

#
# # Login Section
def login_user():
    st.header("Login")

    # Check if the maximum login attempts have been reached
    login_email = st.text_input("Email")
    if login_email:
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = {}  # Initialize login_attempts dictionary in session state
        if login_email in st.session_state.login_attempts:
            if st.session_state.login_attempts[login_email] >= 3:
                st.error("Maximum login attempts reached. Please try again later.")
                return  # Exit the function to disable further login attempts

    login_password = st.text_input("Password", type="password")
    if login_email and login_password:
        if st.button("Login"):
            try:
                # Check if username and password match
                cursor.execute("SELECT * FROM user WHERE user_email = %s AND user_password = %s",
                               (login_email, login_password))
                user = cursor.fetchone()
                if user:
                    st.session_state.user_id = user[0]  # Set user_id in session state
                    st.success("Login successful!")
                    # Reset login_attempts upon successful login
                    if login_email in st.session_state.login_attempts:
                        del st.session_state.login_attempts[login_email]  # Remove user from login_attempts
                else:
                    # Increment login_attempts upon failed login
                    if login_email in st.session_state.login_attempts:
                        st.session_state.login_attempts[login_email] += 1
                    else:
                        st.session_state.login_attempts[login_email] = 1
                    st.error("Invalid email or password. Please try again.")
            except mysql.connector.Error as err:
                st.error(f"Error logging in: {err}")



#
def place_order():
    st.header("Place Order")
    if st.session_state.user_id:
        product_name = st.text_input("Product Name")
        quantity = st.number_input("Quantity", min_value=1, value=1)

        # Fetch payment type options from PaymentType table
        cursor.execute("SELECT Type FROM PaymentType")
        payment_options = [row[0] for row in cursor.fetchall()]

        payment_type = st.selectbox("Payment Type", payment_options)
        acc_no = st.number_input("Account Number")
        if st.button("Place Order"):
            if product_name:
                try:
                    # Start a transaction by setting autocommit to False
                    db.autocommit = False

                    # Fetch product details from database
                    cursor.execute("SELECT product_id, product_price, product_qty FROM product WHERE product_name = %s",
                                   (product_name,))
                    product_details = cursor.fetchone()
                    if product_details:
                        product_id, product_price, available_quantity = product_details
                        if quantity <= available_quantity:
                            total_order = product_price * quantity  # Calculate total order
                            # Fetch user's email from database
                            cursor.execute("SELECT user_email FROM user WHERE user_id = %s",
                                           (st.session_state.user_id,))
                            user_email_result = cursor.fetchone()
                            if user_email_result:
                                user_email = user_email_result[0]
                            else:
                                raise ValueError("User email not found.")

                            # Fetch payment type id from PaymentType table
                            cursor.execute("SELECT payment_type_id FROM PaymentType WHERE Type = %s", (payment_type,))
                            payment_type_result = cursor.fetchone()
                            if payment_type_result:
                                payment_type_id = payment_type_result[0]
                            else:
                                raise ValueError("Payment type not found.")

                            # Fetch shipping address from user_address table
                            cursor.execute("SELECT shipping_id FROM user_address WHERE user_id = %s AND is_default = 1",
                                           (st.session_state.user_id,))
                            shipping_id_result = cursor.fetchone()
                            if shipping_id_result:
                                shipping_id = shipping_id_result[0]
                                cursor.execute("SELECT * FROM shipping_details WHERE shipping_id = %s", (shipping_id,))
                                shipping_address_result = cursor.fetchone()
                                if shipping_address_result:
                                    shipping_address = shipping_address_result
                                else:
                                    raise ValueError("Shipping address not found.")
                            else:
                                raise ValueError("Shipping ID not found.")

                            # Insert order details into database
                            cursor.execute(
                                "INSERT INTO shop_order (user_id, order_date, payment_id, shipping_addresss, order_total, order_status) VALUES ( %s, NOW(), (SELECT payment_id FROM payment WHERE user_id = %s ORDER BY payment_id DESC LIMIT 1), %s, %s, 'Pending')",
                                (st.session_state.user_id, st.session_state.user_id, shipping_address[1],
                                 total_order))
                            # Insert order line details into database
                            cursor.execute(
                                "INSERT INTO order_line (product_item_id, order_id, qty, price) VALUES (%s, LAST_INSERT_ID(), %s, %s)",
                                (product_id, quantity, product_price))
                            # Update product quantity
                            cursor.execute("UPDATE product SET product_qty = product_qty - %s WHERE product_id = %s",
                                           (quantity, product_id))

                            # Commit the transaction
                            db.commit()
                            st.success("Order placed successfully!")

                            # Show order details
                            st.subheader("Order Details")
                            cursor.execute(
                                "SELECT * FROM shop_order WHERE user_id = %s ORDER BY order_id DESC LIMIT 1",
                                (st.session_state.user_id,))
                            order_details = cursor.fetchone()
                            st.write("Order ID:", order_details[0])
                            st.write("Total Order:", total_order)
                            st.write("Payment Type:", payment_type)
                            # Print shipping address
                            st.subheader("Shipping Address")
                            st.write("Unit Number:", shipping_address[1])
                            st.write("Street Number:", shipping_address[2])
                            st.write("Region:", shipping_address[3])
                            st.write("City:", shipping_address[4])
                            st.write("Postal Code:", shipping_address[5])
                            st.write("Country:", shipping_address[6])
                        else:
                            st.warning("Insufficient quantity available.")
                    else:
                        st.error("Product not found.")
                except mysql.connector.Error as err:
                    st.error(f"Error placing order: {err}")
                    # Rollback the transaction in case of error
                    db.rollback()
                except ValueError as err:
                    st.error(f"Error placing order: {err}")
                    # Rollback the transaction in case of error
                    db.rollback()
                finally:
                    # Reset autocommit to True after the transaction
                    db.autocommit = True
            else:
                st.warning("Please enter product name.")
    else:
        st.error("Please login to place an order.")

# Inventory Management Section



def inventory_management():
    st.header("Inventory Management")
    product_name = st.text_input("Product Name")
    brand_name = st.text_input("Brand Name")
    product_specifications = st.text_input("Product Specifications")
    product_price = st.number_input("Product Price", min_value=0)
    product_qty = st.number_input("Product Quantity", min_value=0)
    product_discount = st.number_input("Product Discount", min_value=0)
    category_id = st.number_input("Category ID", min_value=1)
    vendor_name = st.text_input("Vendor Name")
    vendor_password = st.text_input("Vendor Password", type="password")

    if st.button("Add Product"):
        if product_name and brand_name and product_price and product_qty and category_id and vendor_name and vendor_password:
            try:
                # Fetch vendor_id based on vendor_name and vendor_password
                cursor.execute(
                    "SELECT vendor_id FROM vendor WHERE vendor_username = %s AND vendor_password = %s",
                    (vendor_name, vendor_password))
                vendor_id = cursor.fetchone()
                if vendor_id:
                    vendor_id = vendor_id[0]  # Extract the vendor_id from the result tuple
                    # Insert new product into the database
                    cursor.execute(
                        "INSERT INTO product (product_name, brand_name, product_specifications, product_price, "
                        "product_qty, product_discount, category_id, vendor_id) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (product_name, brand_name, product_specifications, product_price, product_qty,
                         product_discount, category_id, vendor_id))
                    db.commit()
                    st.success("Product added successfully!")
                else:
                    st.error("Invalid vendor name or password.")
            except mysql.connector.Error as err:
                st.error(f"Error adding product: {err}")
        else:
            st.warning("Please fill in all required fields.")




# Customer Analysis Section
def customer_analysis():
    st.header("Customer Analysis")
    cursor.execute(
        "SELECT u.user_name, COUNT(so.order_id) AS order_count FROM user u LEFT JOIN shop_order so ON u.user_id = so.user_id GROUP BY u.user_name")
    customer_data = cursor.fetchall()
    df = pd.DataFrame(customer_data, columns=["User Name", "Order Count"])
    st.write(df)

    # Plot most active users
    st.subheader("Most Active Users")
    plt.figure(figsize=(10, 6))
    plt.bar(df["User Name"], df["Order Count"])
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("User Name")
    plt.ylabel("Order Count")
    plt.title("Most Active Users")
    st.pyplot(plt)

    cursor.execute(
        "SELECT p.product_name, COUNT(ol.order_id) AS order_count FROM product p INNER JOIN order_line ol ON p.product_id = ol.product_item_id GROUP BY p.product_name")
    product_data = cursor.fetchall()
    df_products = pd.DataFrame(product_data, columns=["Product Name", "Order Count"])
    st.write(df_products)

    # Plot most bought products
    st.subheader("Most Bought Products")
    plt.figure(figsize=(10, 6))
    plt.bar(df_products["Product Name"], df_products["Order Count"])
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Product Name")
    plt.ylabel("Order Count")
    plt.title("Most Bought Products")
    st.pyplot(plt)

def order_history():
    st.header("Order History")
    if st.session_state.user_id:
        try:
            # Fetch order history for the logged-in user
            cursor.execute(
                "SELECT order_id, order_date, order_total, order_status FROM shop_order WHERE user_id = %s ORDER BY order_date DESC",
                (st.session_state.user_id,))
            order_history_data = cursor.fetchall()
            if order_history_data:
                # Display order history in a table
                order_history_df = pd.DataFrame(order_history_data, columns=["Order ID", "Order Date", "Total", "Status"])
                st.write(order_history_df)
            else:
                st.info("No order history found.")
        except mysql.connector.Error as err:
            st.error(f"Error fetching order history: {err}")
    else:
        st.error("Please login to view order history.")
# # Main function to run the application

def manage_payment_methods():
    st.header("Manage Payment Methods")
    if st.session_state.user_id:
        st.subheader("Add Payment Method")
        payment_type = st.selectbox("Payment Type", ["Credit Card", "Debit Card", "PayPal", "Cash", "Check"])
        account_number = st.text_input("Account Number")

        if st.button("Add Payment Method"):
            if payment_type and account_number:
                try:
                    # Insert new payment method into the database
                    cursor.execute(
                        "INSERT INTO payment (user_id, payment_type_id, account_number) VALUES (%s, (SELECT payment_type_id FROM PaymentType WHERE Type = %s), %s)",
                        (st.session_state.user_id, payment_type, account_number))
                    db.commit()
                    st.success("Payment method added successfully!")
                except mysql.connector.Error as err:
                    st.error(f"Error adding payment method: {err}")
            else:
                st.warning("Please fill in all required fields.")

        st.subheader("View Payment Methods")
        # Fetch and display user's payment methods
        cursor.execute("SELECT Type, account_number FROM payment JOIN PaymentType ON payment.payment_type_id = PaymentType.payment_type_id WHERE user_id = %s", (st.session_state.user_id,))
        payment_methods = cursor.fetchall()
        if payment_methods:
            st.write("Your Payment Methods:")
            for method in payment_methods:
                st.write(f"- {method[0]}: {method[1]}")
        else:
            st.write("No payment methods found.")
    else:
        st.error("Please login to manage payment methods.")

# Main function to run the application
def main():
    st.title("Online Shopping App")

    # Navigation sidebar
    navigation = st.sidebar.radio("Navigation", ["Home", "Register", "Login", "Place Order", "Inventory Management",
                                                 "Customer Analysis", "Order History", "Payment Methods"])
    if navigation == "Home":
        st.subheader("Home")
        st.write("Welcome to the Online Shopping App!")

    elif navigation == "Register":
        register_user()

    elif navigation == "Login":
        login_user()

    elif navigation == "Place Order":
        place_order()

    elif navigation == "Inventory Management":
        inventory_management()

    elif navigation == "Customer Analysis":
        customer_analysis()

    elif navigation == "Order History":
        order_history()

    elif navigation == "Payment Methods":
        manage_payment_methods()
if __name__ == "__main__":
    main()