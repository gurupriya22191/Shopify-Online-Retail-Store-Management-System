import threading

import mysql.connector

# Establish database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="project8"
)
cursor = db.cursor()

# Define a function for a conflicting transaction
def update_product_quantity(product_id, new_quantity):
    cursor = db.cursor()
    try:
        # Initialize cursor within the try block to ensure proper scoping


        # Update the quantity of the product
        cursor.execute("UPDATE product SET product_qty = %s WHERE product_id = %s", (new_quantity, product_id))
        db.commit()
        print("Product quantity updated successfully!")
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Error updating product quantity: {err}")
    finally:
        cursor.close()

# Define two conflicting transactions
def user1_update_product_quantity():
    # Initialize cursor within the function to ensure proper scoping
    cursor = db.cursor()
    update_product_quantity(1001, 10)

def user2_update_product_quantity():
    # Initialize cursor within the function to ensure proper scoping
    cursor = db.cursor()
    update_product_quantity(1001, 20)

# Create threads for each conflicting transaction
thread1 = threading.Thread(target=user1_update_product_quantity)
thread2 = threading.Thread(target=user2_update_product_quantity)

# Start the threads
thread1.start()
thread2.start()

# Wait for the threads to finish
thread1.join()
thread2.join()

# Close database connection
db.close()


# Define functions for simulating transactions
# def simulate_user1_place_order():
#     product_name = "Pen"
#     quantity = 1 # Sufficient quantity
#     payment_type = "Credit Card"
#     acc_no = 1234567890  # Random account number for testing
#
#     try:
#         cursor.execute("SELECT product_id, product_price, product_qty FROM product WHERE product_name = %s",
#                        (product_name,))
#         product_details = cursor.fetchone()
#         if product_details:
#             product_id, product_price, available_quantity = product_details
#             if quantity <= available_quantity:
#                 total_order = product_price * quantity
#
#                 # Assuming user 1 is already logged in and their user_id is stored in st.session_state.user_id
#                 # Replace st.session_state.user_id with the actual user ID
#                 user_id = 1
#
#                 cursor.execute("SELECT user_email FROM user WHERE user_id = %s", (user_id,))
#                 user_email = cursor.fetchone()[0]
#
#                 cursor.execute("SELECT payment_type_id FROM PaymentType WHERE Type = %s", (payment_type,))
#                 payment_type_id = cursor.fetchone()[0]
#
#                 # Assuming shipping address is already available for user 1
#                 cursor.execute("SELECT shipping_id FROM user_address WHERE user_id = %s AND is_default = 1",
#                                (user_id,))
#                 shipping_id = cursor.fetchone()[0]
#
#                 cursor.execute("SELECT * FROM shipping_details WHERE shipping_id = %s", (shipping_id,))
#                 shipping_address = cursor.fetchone()
#                 if shipping_address:
#                     cursor.execute(
#                         "INSERT INTO shop_order (user_id, order_date, payment_id, shipping_addresss, order_total, order_status) VALUES (%s, NOW(), %s, %s, %s, 'Pending')",
#                         (user_id, payment_type_id, shipping_address[1], total_order))
#                     cursor.execute(
#                         "INSERT INTO order_line (product_item_id, order_id, qty, price) VALUES (%s, LAST_INSERT_ID(), %s, %s)",
#                         (product_id, quantity, product_price))
#                     cursor.execute(
#                         "UPDATE product SET product_qty = product_qty - %s WHERE product_id = %s",
#                         (quantity, product_id))
#                     db.commit()
#                     print("User 1 placed the order successfully!")
#                 else:
#                     print("Default shipping address not found for User 1.")
#             else:
#                 print("Insufficient quantity available for User 1.")
#         else:
#             print("Product not found.")
#     except mysql.connector.Error as err:
#         print(f"Error placing order for User 1: {err}")
#
# def simulate_user2_place_order():
#     product_name = "Pencil"
#     quantity = 1  # Insufficient quantity
#     payment_type = "Credit Card"
#     acc_no = 9876543210  # Random account number for testing
#
#     try:
#         cursor.execute("SELECT product_id, product_price, product_qty FROM product WHERE product_name = %s",
#                        (product_name,))
#         product_details = cursor.fetchone()
#         if product_details:
#             product_id, product_price, available_quantity = product_details
#             if quantity <= available_quantity:
#                 total_order = product_price * quantity
#
#                 # Assuming user 2 is already logged in and their user_id is stored in st.session_state.user_id
#                 # Replace st.session_state.user_id with the actual user ID
#                 user_id = 2
#
#                 cursor.execute("SELECT user_email FROM user WHERE user_id = %s", (user_id,))
#                 user_email = cursor.fetchone()[0]
#
#                 cursor.execute("SELECT payment_type_id FROM PaymentType WHERE Type = %s", (payment_type,))
#                 payment_type_id = cursor.fetchone()[0]
#
#                 # Assuming shipping address is already available for user 2
#                 cursor.execute("SELECT shipping_id FROM user_address WHERE user_id = %s AND is_default = 1",
#                                (user_id,))
#                 shipping_id = cursor.fetchone()[0]
#
#                 cursor.execute("SELECT * FROM shipping_details WHERE shipping_id = %s", (shipping_id,))
#                 shipping_address = cursor.fetchone()
#                 if shipping_address:
#                     cursor.execute(
#                         "INSERT INTO shop_order (user_id, order_date, payment_id, shipping_addresss, order_total, order_status) VALUES (%s, NOW(), %s, %s, %s, 'Pending')",
#                         (user_id, payment_type_id, shipping_address[1], total_order))
#                     cursor.execute(
#                         "INSERT INTO order_line (product_item_id, order_id, qty, price) VALUES (%s, LAST_INSERT_ID(), %s, %s)",
#                         (product_id, quantity, product_price))
#                     cursor.execute(
#                         "UPDATE product SET product_qty = product_qty - %s WHERE product_id = %s",
#                         (quantity, product_id))
#                     db.commit()
#                     print("User 2 placed the order successfully!")
#                 else:
#                     print("Default shipping address not found for User 2.")
#             else:
#                 print("Insufficient quantity available for User 2.")
#         else:
#             print("Product not found.")
#     except mysql.connector.Error as err:
#         print(f"Error placing order for User 2: {err}")

# # Execute transactions
# simulate_user1_place_order()  # Simulate User 1 placing an order
# simulate_user2_place_order()  # Simulate User 2 placing an order
#
# # Close database connection
# cursor.close()
# db.close()




# Define functions for simulating conflicting transactions
# def simulate_user1_update_balance():
#     try:
#         # Simulate user 1 updating balance
#         cursor.execute("SELECT balance FROM accounts WHERE user_id = 1")
#         user1_balance = cursor.fetchone()[0]
#         new_balance = user1_balance + 100  # Increment user 1's balance by 100
#
#         cursor.execute("UPDATE accounts SET balance = %s WHERE user_id = 1", (new_balance,))
#         db.commit()
#         print("User 1 updated balance successfully!")
#     except mysql.connector.Error as err:
#         db.rollback()
#         print(f"Error updating balance for User 1: {err}")
#
# def simulate_user2_update_balance():
#     try:
#         # Simulate user 2 updating balance
#         cursor.execute("SELECT balance FROM accounts WHERE user_id = 1")  # Assuming user_id 1 is being updated by both users
#         user1_balance = cursor.fetchone()[0]
#         new_balance = user1_balance - 50  # Decrement user 1's balance by 50
#
#         cursor.execute("UPDATE accounts SET balance = %s WHERE user_id = 1", (new_balance,))
#         db.commit()
#         print("User 2 updated balance successfully!")
#     except mysql.connector.Error as err:
#         db.rollback()
#         print(f"Error updating balance for User 2: {err}")
#
# # Execute conflicting transactions
# simulate_user1_update_balance()  # Simulate User 1 updating balance
# simulate_user2_update_balance()  # Simulate User 2 updating balance
#
# # Close database connection
# cursor.close()
# db.close()




# Define a function for a non-conflicting transaction
# def update_user_age(user_id, new_age):
#     try:
#         # Update the age of a user
#         cursor.execute("UPDATE user SET user_age = %s WHERE user_id = %s", (new_age, user_id))
#         db.commit()
#         print("User age updated successfully!")
#     except mysql.connector.Error as err:
#         db.rollback()
#         print(f"Error updating user age: {err}")
#
# # Execute the non-conflicting transaction
# update_user_age(1, 30)  # Update the age of user with ID 1 to 30
#
# # Close database connection
# cursor.close()
# db.close()


# Define a function for a non-conflicting transaction
# Define a function for a non-conflicting transaction
# def update_user_phone(user_id, new_phone_number):
#     try:
#         # Update the phone number of a user
#         cursor.execute("UPDATE user SET user_phone = %s WHERE user_id = %s", (new_phone_number, user_id))
#         db.commit()
#         print("User phone number updated successfully!")
#     except mysql.connector.Error as err:
#         db.rollback()
#         print(f"Error updating user phone number: {err}")
#
# # Execute the non-conflicting transaction
# update_user_phone(1, "9876543210")  # Update the phone number of user with ID 1
#
# # Close database connection
# cursor.close()
# db.close()

# Define a function for a non-conflicting transaction
# def delete_shipping_address(user_id, shipping_id):
#     try:
#         # Delete the specified shipping address for a user
#         cursor.execute("DELETE FROM user_address WHERE user_id = %s AND shipping_id = %s", (user_id, shipping_id))
#         db.commit()
#         print("Shipping address deleted successfully!")
#     except mysql.connector.Error as err:
#         db.rollback()
#         print(f"Error deleting shipping address: {err}")
#
# # Execute the non-conflicting transaction
# delete_shipping_address(1, 5)  # Delete the shipping address with ID 5 for user with ID 1
#
# # Close database connection
# cursor.close()
# db.close()



