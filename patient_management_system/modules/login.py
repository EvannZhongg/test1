import os
import csv
from datetime import datetime
from utils.helpers import clear_screen, input_with_validation, is_valid_email, validate_password, log_login_event

DATA_DIR = '../data'
USERS_FILE = os.path.join(DATA_DIR, 'users.csv')


def login():
    clear_screen()
    print("\n===== Monash Patient Management System =====")
    print("Login")

    for attempt in range(3):
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        user = authenticate(email, password)
        if user:
            print(f"\n✅ Login successful! Welcome, {user['role']}!")
            log_login_event(email)
            return user
        else:
            print("❌ Incorrect email or password.\n")
    print("🚫 Too many failed attempts. Returning to main menu.")
    input("\nPress Enter to continue...")
    return None


def authenticate(email, password):
    users = load_users()
    for user in users:
        if user['email'].lower() == email.lower() and user['password'] == password:
            return user
    return None


def load_users():
    users = []
    try:
        with open(USERS_FILE, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append(row)
    except FileNotFoundError:
        print(f"User data file not found at {USERS_FILE}. Please ensure the file exists.")
    return users


def register():
    clear_screen()
    print("\n===== Patient Registration =====")
    users = load_users()

    # email校验允许student和staff邮箱
    email = input_with_validation("Enter Monash email (@student.monash.edu or @monash.edu): ",
                                  lambda x: is_valid_email(x) and (x.endswith('@student.monash.edu') or x.endswith('@monash.edu')),
                                  "❌ Invalid email. Must be Monash email.")
    if any(u['email'].lower() == email.lower() for u in users):
        print("\n❌ Email already registered.")
        input("\nPress Enter to continue...")
        return

    password = input_with_validation("Enter password (≥8 chars, 1 uppercase, 1 number): ",
                                     validate_password,
                                     "❌ Weak password.")
    first_name = input_with_validation("Enter first name: ", lambda x: x.strip() != "", "❌ Cannot be empty.")
    last_name = input_with_validation("Enter last name: ", lambda x: x.strip() != "", "❌ Cannot be empty.")

    dob = input_with_validation("Enter date of birth (dd/mm/yyyy): ",
                                is_valid_dob,
                                "❌ Invalid DOB. Use dd/mm/yyyy and ensure it’s not a future date.")
    gender = input("Enter gender (optional): ").strip()
    mobile = input_with_validation("Enter Australian mobile number (starts with 04, 10 digits): ",
                                   is_valid_au_mobile,
                                   "❌ Invalid format. Must start with 04 and be 10 digits.")
    address = input("Enter address (optional): ").strip()

    new_user = {
        'email': email,
        'password': password,
        'role': 'patient',
        'first_name': first_name,
        'last_name': last_name,
        'dob': dob,
        'gender': gender,
        'mobile': mobile,
        'address': address
    }

    users.append(new_user)
    save_users(users, new_user.keys())
    print("\n✅ Registration successful! Please return to the main menu to log in.")
    input("\nPress Enter to continue...")


def reset_password():
    clear_screen()
    print("\n===== Password Reset =====")
    users = load_users()
    email = input_with_validation("Enter registered email: ", is_valid_email, "Invalid email.")
    for user in users:
        if user['email'].lower() == email.lower():
            new_password = input_with_validation("Enter new password (≥8 chars, 1 uppercase, 1 number): ",
                                                 validate_password,
                                                 "❌ Weak password.")
            user['password'] = new_password
            save_users(users, user.keys())
            print("\n✅ Password reset successful!")
            input("\nPress Enter to continue...")
            return
    print("\n❌ Email not found.")
    input("\nPress Enter to continue...")


def save_users(users, fieldnames):
    with open(USERS_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)


# === 新增辅助校验函数 ===

def is_valid_dob(dob_str):
    try:
        dob = datetime.strptime(dob_str, "%d/%m/%Y")
        return dob <= datetime.now() and dob.year > 1900
    except:
        return False

def is_valid_au_mobile(mobile):
    return mobile.isdigit() and mobile.startswith("04") and len(mobile) == 10


if __name__ == "__main__":
    login()
