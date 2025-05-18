from utils.helpers import clear_screen
from modules.login import login, register, reset_password
from modules.admin import admin_menu
from modules.patient import patient_menu


def main():
    while True:
        clear_screen()
        print("\n===== Monash Patient Management System =====")
        print("1. Login")
        print("2. Register (Patient only)")
        print("3. Reset Password")
        print("4. Exit")

        choice = input("\nEnter your choice: ").strip()

        if choice == '1':
            user = login()
            if user:
                if user['role'] == 'admin':
                    admin_menu()
                elif user['role'] == 'patient':
                    patient_menu(user['email'])
                elif user['role'] == 'doctor':
                    print("\nDoctor interface is currently under development.")
                    input("\nPress Enter to continue...")
        elif choice == '2':
            register()
        elif choice == '3':
            reset_password()
        elif choice == '4':
            clear_screen()
            print("\nThank you for using Monash Patient Management System.")
            break
        else:
            input("Invalid choice. Press Enter to continue...")


if __name__ == "__main__":
    main()
