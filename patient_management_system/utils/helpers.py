import os
import csv
from datetime import datetime
import re
import socket

DATA_DIR = '../data'  # Data directory path

def validate_email(email):
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validate password strength:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 digit
    """
    return (
        len(password) >= 8 and 
        any(c.isupper() for c in password) and 
        any(c.isdigit() for c in password)
    )

def log_login_event(email):
    """Log login event with email, timestamp, and IP address to 'login_logs.csv'."""
    log_file = os.path.join(DATA_DIR, 'login_logs.csv')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
    except:
        ip_address = 'unknown'
    
    exists = os.path.isfile(log_file)
    with open(log_file, 'a', newline='') as file:
        writer = csv.writer(file)
        if not exists:
            writer.writerow(['email', 'timestamp', 'ip_address'])
        writer.writerow([email, timestamp, ip_address])

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_menu(title, options):
    """Display a numbered menu and get user selection."""
    clear_screen()
    print(f"\n===== {title} =====")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print(f"{len(options) + 1}. Return to previous menu")
    
    while True:
        try:
            choice = int(input("\nEnter your choice: "))
            if 1 <= choice <= len(options) + 1:
                return choice
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")

def input_with_validation(prompt, validation_func, error_msg):
    """Prompt user input with validation."""
    while True:
        user_input = input(prompt).strip()
        if validation_func(user_input):
            return user_input
        print(error_msg)

def is_valid_email(email):
    """Wrapper for email validation."""
    return validate_email(email)

def is_valid_time_format(time_str):
    """Validate time format as HH:MM."""
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False

def is_valid_date_format(date_str):
    """Validate date format as YYYY-MM-DD."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
        
def load_csv_data(filepath):
    """Load data from a CSV file."""
    data = []
    try:
        with open(filepath, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        return []

def save_csv_data(filepath, data, fieldnames):
    """Save data to a CSV file."""
    try:
        with open(filepath, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def get_next_id(data):
    """Get the next available ID by finding the maximum existing ID and adding 1."""
    if not data:
        return "1"
    try:
        max_id = max(int(item['id']) for item in data)
        return str(max_id + 1)
    except (ValueError, KeyError):
        return "1"
