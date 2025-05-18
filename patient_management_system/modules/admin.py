import os
from utils.helpers import (
    clear_screen,
    display_menu,
    input_with_validation,
    is_valid_email,
    load_csv_data,
    save_csv_data,
    get_next_id,
    is_valid_date_format  # newly needed for date prompts
)
from modules.report_generator import generate_clinic_report, generate_gp_report
from datetime import datetime


DATA_DIR = '../data'
APPOINTMENTS_FILE = os.path.join(DATA_DIR, 'appointments.csv')
SLOTS_FILE        = os.path.join(DATA_DIR, 'slots.csv')
USERS_FILE        = os.path.join(DATA_DIR, 'users.csv')
CLINICS_FILE = os.path.join(DATA_DIR, 'clinics.csv')
DOCTORS_FILE = os.path.join(DATA_DIR, 'doctors.csv')
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, 'notifications.csv')


def admin_menu():
    """Main administrator menu"""
    while True:
        choice = display_menu("Administrator Menu", [
            "Manage Clinics",
            "Manage GPs",
            "Manage GP Appointment Slots",
            "Generate Clinic Report",
            "Generate GP Report",
            "Cancel Appointment",
            "Logout"
        ])

        if choice == 1:
            manage_clinics()
        elif choice == 2:
            manage_doctors()
        elif choice == 3:
            manage_gp_slots()
        elif choice == 4:
            generate_clinic_report()
        elif choice == 5:
            generate_gp_report()
        elif choice == 6:
            cancel_appointment_admin()
        elif choice == 7 or choice == 8:
            return  # Return to login screen

def manage_clinics():
    """Handle clinic management options"""
    while True:
        choice = display_menu("Clinic Management", [
            "View All Clinics",
            "Add New Clinic",
            "Update Clinic",
            "Delete Clinic"
        ])
        
        if choice == 1:
            view_all_clinics()
        elif choice == 2:
            add_clinic()
        elif choice == 3:
            update_clinic()
        elif choice == 4:
            delete_clinic()
        elif choice == 5:
            return  # Return to admin menu

def view_all_clinics():
    """Display all clinics in a formatted table"""
    clinics = load_csv_data(CLINICS_FILE)
    
    clear_screen()
    print("\n===== All Clinics =====")
    
    if not clinics:
        print("No clinics found.")
    else:
        print(f"{'ID':<4} {'Name':<30} {'Location':<30} {'Services':<50} {'Operating Hours':<30}")
        print("-" * 150)
        for clinic in clinics:
            print(f"{clinic['id']:<4} {clinic['name']:<30} {clinic['location']:<30} {clinic['services']:<50} {clinic['operating_hours']:<30}")
    
    input("\nPress Enter to continue...")

def add_clinic():
    """Add a new clinic"""
    clear_screen()
    print("\n===== Add New Clinic =====")
    
    clinics = load_csv_data(CLINICS_FILE)
    new_id = get_next_id(clinics)
    
    # Get clinic details with validation
    name = input_with_validation("Enter clinic name: ", 
                                lambda x: x.strip() != "", 
                                "Clinic name cannot be empty.")
    
    location = input_with_validation("Enter clinic location: ", 
                                    lambda x: x.strip() != "", 
                                    "Location cannot be empty.")
    
    services = input("Enter services offered (comma separated): ").strip()
    
    operating_hours = input_with_validation("Enter operating hours: ", 
                                          lambda x: x.strip() != "", 
                                          "Operating hours cannot be empty.")
    
    # Create new clinic record
    new_clinic = {
        'id': new_id,
        'name': name,
        'location': location,
        'services': services,
        'operating_hours': operating_hours
    }
    
    clinics.append(new_clinic)
    
    # Save updated clinics list
    if save_csv_data(CLINICS_FILE, clinics, new_clinic.keys()):
        print("\n Clinic added successfully!")
    else:
        print("\n Failed to add clinic.")
    
    input("\nPress Enter to continue...")


def update_clinic():
    """Update an existing clinic"""
    clear_screen()
    print("\n===== Update Clinic =====")

    clinics = load_csv_data(CLINICS_FILE)

    if not clinics:
        print("No clinics found.")
        input("\nPress Enter to continue...")
        return

    # Display clinics for selection
    print(f"{'ID':<4} {'Name':<30} {'Location':<30}")
    print("-" * 64)
    for clinic in clinics:
        print(f"{clinic['id']:<4} {clinic['name']:<30} {clinic['location']:<30}")

    # Get clinic ID to update
    clinic_id = input("\nEnter the ID of the clinic to update (or 'c' to cancel): ").strip()
    if clinic_id.lower() == 'c':
        return

    # Find the clinic to update
    clinic_to_update = None
    for i, clinic in enumerate(clinics):
        if clinic['id'] == clinic_id:
            clinic_to_update = clinic
            clinic_index = i
            break

    if clinic_to_update is None:
        print("\nClinic not found.")
        input("\nPress Enter to continue...")
        return

    # 保存修改前的 clinic_id
    old_id = clinic_to_update['id']

    # Begin editing fields
    print(f"\nUpdating clinic: {clinic_to_update['name']}")

    # Allow changing the clinic's ID
    new_id = input(f"Enter new ID (current: {clinic_to_update['id']}) or press Enter to keep current: ").strip()
    if new_id:
        clinic_to_update['id'] = new_id

    # Edit name
    name = input_with_validation(
        f"Enter new name (current: {clinic_to_update['name']}) or press Enter to keep current: ",
        lambda x: True, ""
    )
    if name:
        clinic_to_update['name'] = name

    # Edit location
    location = input_with_validation(
        f"Enter new location (current: {clinic_to_update['location']}) or press Enter to keep current: ",
        lambda x: True, ""
    )
    if location:
        clinic_to_update['location'] = location

    # Edit services
    services = input(
        f"Enter new services (current: {clinic_to_update.get('services', '')}) or press Enter to keep current: "
    ).strip()
    if services:
        clinic_to_update['services'] = services

    # Edit operating hours
    operating_hours = input_with_validation(
        f"Enter new operating hours (current: {clinic_to_update.get('operating_hours', '')}) or press Enter to keep current: ",
        lambda x: True, ""
    )
    if operating_hours:
        clinic_to_update['operating_hours'] = operating_hours

    # Update the clinic in the list
    clinics[clinic_index] = clinic_to_update

    # Save updated clinics list
    if save_csv_data(CLINICS_FILE, clinics, clinic_to_update.keys()):
        print("\nClinic updated successfully!")
    else:
        print("\nFailed to update clinic.")

    # 如果 clinic_id 已更改，则同步更新 appointments.csv 和 slots.csv
    if old_id != clinic_to_update['id']:
        # 同步 appointments.csv
        appointments = load_csv_data(APPOINTMENTS_FILE)
        for appt in appointments:
            if appt['clinic_id'] == old_id:
                appt['clinic_id'] = clinic_to_update['id']
        save_csv_data(
            APPOINTMENTS_FILE,
            appointments,
            appointments[0].keys() if appointments else []
        )
        print("  • All affected appointments have been updated.")

        # 同步 slots.csv
        slots = load_csv_data(SLOTS_FILE)
        for slot in slots:
            if slot['clinic_id'] == old_id:
                slot['clinic_id'] = clinic_to_update['id']
        save_csv_data(
            SLOTS_FILE,
            slots,
            slots[0].keys() if slots else []
        )
        print("  • All affected slots have been updated.")

    input("\nPress Enter to continue...")

def delete_clinic():
    """Delete a clinic"""
    clear_screen()
    print("\n===== Delete Clinic =====")
    
    clinics = load_csv_data(CLINICS_FILE)
    doctors = load_csv_data(DOCTORS_FILE)
    
    if not clinics:
        print("No clinics found.")
        input("\nPress Enter to continue...")
        return
    
    # Display clinics for selection
    print(f"{'ID':<4} {'Name':<30} {'Location':<30}")
    print("-" * 64)
    for clinic in clinics:
        print(f"{clinic['id']:<4} {clinic['name']:<30} {clinic['location']:<30}")
    
    # Get clinic ID to delete
    clinic_id = input("\nEnter the ID of the clinic to delete (or 'c' to cancel): ").strip()
    if clinic_id.lower() == 'c':
        return
    
    # Check if any doctors are assigned to this clinic
    doctors_at_clinic = [d for d in doctors if d['clinic_id'] == clinic_id]
    if doctors_at_clinic:
        print(f"\n Cannot delete: There are {len(doctors_at_clinic)} doctors assigned to this clinic.")
        print("Please reassign or delete these doctors first.")
        input("\nPress Enter to continue...")
        return
    
    # Find the clinic to delete
    clinic_found = False
    updated_clinics = []
    for clinic in clinics:
        if clinic['id'] == clinic_id:
            clinic_found = True
            print(f"\nAre you sure you want to delete '{clinic['name']}'?")
            confirm = input("Type 'yes' to confirm: ").strip().lower()
            if confirm != 'yes':
                print("\nDeletion cancelled.")
                input("\nPress Enter to continue...")
                return
        else:
            updated_clinics.append(clinic)
    
    if not clinic_found:
        print("\n Clinic not found.")
        input("\nPress Enter to continue...")
        return
    
    # Save updated clinics list
    if save_csv_data(CLINICS_FILE, updated_clinics, clinics[0].keys() if clinics else []):
        print("\n Clinic deleted successfully!")
    else:
        print("\n Failed to delete clinic.")
    
    input("\nPress Enter to continue...")

def manage_doctors():
    """Handle GP management options"""
    while True:
        choice = display_menu("GP Management", [
            "View All GPs",
            "Add New GP",
            "Update GP",
            "Delete GP"
        ])
        
        if choice == 1:
            view_all_doctors()
        elif choice == 2:
            add_doctor()
        elif choice == 3:
            update_doctor()
        elif choice == 4:
            delete_doctor()
        elif choice == 5:
            return  # Return to admin menu

def view_all_doctors():
    """Display all doctors in a formatted table"""
    doctors = load_csv_data(DOCTORS_FILE)
    clinics = load_csv_data(CLINICS_FILE)
    
    # Create clinic lookup dictionary
    clinic_lookup = {clinic['id']: clinic['name'] for clinic in clinics}
    
    clear_screen()
    print("\n===== All General Practitioners =====")
    
    if not doctors:
        print("No GPs found.")
    else:
        print(f"{'ID':<4} {'Name':<25} {'Email':<30} {'Clinic':<25} {'Specialty':<25} {'Availability':<20}")
        print("-" * 150)
        for doctor in doctors:
            clinic_name = clinic_lookup.get(doctor['clinic_id'], 'Unknown Clinic')
            print(f"{doctor['id']:<4} {doctor['full_name']:<25} {doctor['email']:<30} "
                  f"{clinic_name:<25} {doctor['specialty']:<25} {doctor['availability']:<20}")
    
    input("\nPress Enter to continue...")

def add_doctor():
    """Add a new doctor"""
    clear_screen()
    print("\n===== Add New GP =====")
    
    doctors = load_csv_data(DOCTORS_FILE)
    clinics = load_csv_data(CLINICS_FILE)
    
    if not clinics:
        print(" No clinics available. Please add a clinic first.")
        input("\nPress Enter to continue...")
        return
    
    new_id = get_next_id(doctors)
    
    # Get doctor details with validation
    full_name = input_with_validation("Enter full name (with title, e.g., Dr. John Smith): ", 
                                     lambda x: x.strip() != "" and x.strip().startswith("Dr."), 
                                     "Name must start with 'Dr.' and cannot be empty.")
    
    email = input_with_validation("Enter email: ", 
                                 is_valid_email, 
                                 "Please enter a valid email address.")
    
    # Check if email is already in use
    if any(d['email'] == email for d in doctors):
        print("\n This email is already in use by another GP.")
        input("\nPress Enter to continue...")
        return
    
    # Show available clinics
    print("\nAvailable Clinics:")
    print(f"{'ID':<4} {'Name':<30} {'Location':<30}")
    print("-" * 64)
    for clinic in clinics:
        print(f"{clinic['id']:<4} {clinic['name']:<30} {clinic['location']:<30}")
    
    clinic_id = input_with_validation("\nEnter clinic ID: ", 
                                     lambda x: any(c['id'] == x for c in clinics), 
                                     "Invalid clinic ID. Please choose from the list.")
    
    specialty = input_with_validation("Enter specialty: ", 
                                     lambda x: x.strip() != "", 
                                     "Specialty cannot be empty.")
    
    availability = input_with_validation("Enter availability (e.g., Mon,Tue,Wed: 9am-5pm): ", 
                                        lambda x: x.strip() != "", 
                                        "Availability cannot be empty.")
    
    # Create new doctor record
    new_doctor = {
        'id': new_id,
        'full_name': full_name,
        'email': email,
        'clinic_id': clinic_id,
        'specialty': specialty,
        'availability': availability
    }
    
    doctors.append(new_doctor)
    
    # Save updated doctors list
    if save_csv_data(DOCTORS_FILE, doctors, new_doctor.keys()):
        print("\n GP added successfully!")
    else:
        print("\n Failed to add GP.")
    
    input("\nPress Enter to continue...")

def update_doctor():
    """Update an existing doctor"""
    clear_screen()
    print("\n===== Update GP =====")
    
    doctors = load_csv_data(DOCTORS_FILE)
    clinics = load_csv_data(CLINICS_FILE)
    
    if not doctors:
        print("No GPs found.")
        input("\nPress Enter to continue...")
        return
    
    # Create clinic lookup dictionary
    clinic_lookup = {clinic['id']: clinic['name'] for clinic in clinics}
    
    # Display doctors for selection
    print(f"{'ID':<4} {'Name':<25} {'Email':<30} {'Clinic':<25}")
    print("-" * 84)
    for doctor in doctors:
        clinic_name = clinic_lookup.get(doctor['clinic_id'], 'Unknown Clinic')
        print(f"{doctor['id']:<4} {doctor['full_name']:<25} {doctor['email']:<30} {clinic_name:<25}")
    
    # Get doctor ID to update
    doctor_id = input("\nEnter the ID of the GP to update (or 'c' to cancel): ").strip()
    if doctor_id.lower() == 'c':
        return
    
    # Find the doctor to update
    doctor_to_update = None
    for i, doctor in enumerate(doctors):
        if doctor['id'] == doctor_id:
            doctor_to_update = doctor
            doctor_index = i
            break
    
    if doctor_to_update is None:
        print("\n GP not found.")
        input("\nPress Enter to continue...")
        return
    
    # Update doctor details
    print(f"\nUpdating GP: {doctor_to_update['full_name']}")
    
    full_name = input_with_validation(f"Enter new name (current: {doctor_to_update['full_name']}) or press Enter to keep current: ", 
                                     lambda x: x == "" or (x.strip() != "" and x.strip().startswith("Dr.")), 
                                     "Name must start with 'Dr.'")
    if full_name:
        doctor_to_update['full_name'] = full_name
    
    email = input_with_validation(f"Enter new email (current: {doctor_to_update['email']}) or press Enter to keep current: ", 
                                 lambda x: x == "" or is_valid_email(x), 
                                 "Please enter a valid email address or leave blank.")
    if email:
        # Check if email is already in use by another doctor
        if email != doctor_to_update['email'] and any(d['email'] == email and d['id'] != doctor_id for d in doctors):
            print("\n This email is already in use by another GP.")
            input("\nPress Enter to continue...")
            return
        doctor_to_update['email'] = email
    
    # Show available clinics
    print("\nAvailable Clinics:")
    print(f"{'ID':<4} {'Name':<30} {'Location':<30}")
    print("-" * 64)
    for clinic in clinics:
        print(f"{clinic['id']:<4} {clinic['name']:<30} {clinic['location']:<30}")
    
    current_clinic_name = clinic_lookup.get(doctor_to_update['clinic_id'], 'Unknown Clinic')
    clinic_id = input_with_validation(f"\nEnter new clinic ID (current: {doctor_to_update['clinic_id']} - {current_clinic_name}) or press Enter to keep current: ", 
                                     lambda x: x == "" or any(c['id'] == x for c in clinics), 
                                     "Invalid clinic ID. Please choose from the list or leave blank.")
    if clinic_id:
        doctor_to_update['clinic_id'] = clinic_id
    
    specialty = input(f"Enter new specialty (current: {doctor_to_update['specialty']}) or press Enter to keep current: ")
    if specialty:
        doctor_to_update['specialty'] = specialty
    
    availability = input(f"Enter new availability (current: {doctor_to_update['availability']}) or press Enter to keep current: ")
    if availability:
        doctor_to_update['availability'] = availability
    
    # Update the doctor in the list
    doctors[doctor_index] = doctor_to_update
    
    # Save updated doctors list
    if save_csv_data(DOCTORS_FILE, doctors, doctor_to_update.keys()):
        print("\n GP updated successfully!")
    else:
        print("\n Failed to update GP.")

    # ── 同步 clinic_id 到 appointments.csv ──
    appointments = load_csv_data(APPOINTMENTS_FILE)
    for appt in appointments:
        if appt['doctor_id'] == doctor_to_update['id']:
            appt['clinic_id'] = doctor_to_update['clinic_id']
    save_csv_data(APPOINTMENTS_FILE,
                  appointments,
                  appointments[0].keys() if appointments else [])

    # ── 同步 clinic_id 到 slots.csv ──
    slots = load_csv_data(SLOTS_FILE)
    for slot in slots:
        if slot['doctor_id'] == doctor_to_update['id']:
            slot['clinic_id'] = doctor_to_update['clinic_id']
    save_csv_data(SLOTS_FILE,
                  slots,
                  slots[0].keys() if slots else [])

    input("\nPress Enter to continue...")

def delete_doctor():
    """Delete a doctor"""
    clear_screen()
    print("\n===== Delete GP =====")
    
    doctors = load_csv_data(DOCTORS_FILE)
    clinics = load_csv_data(CLINICS_FILE)
    
    if not doctors:
        print("No GPs found.")
        input("\nPress Enter to continue...")
        return
    
    # Create clinic lookup dictionary
    clinic_lookup = {clinic['id']: clinic['name'] for clinic in clinics}
    
    # Display doctors for selection
    print(f"{'ID':<4} {'Name':<25} {'Email':<30} {'Clinic':<25}")
    print("-" * 84)
    for doctor in doctors:
        clinic_name = clinic_lookup.get(doctor['clinic_id'], 'Unknown Clinic')
        print(f"{doctor['id']:<4} {doctor['full_name']:<25} {doctor['email']:<30} {clinic_name:<25}")
    
    # Get doctor ID to delete
    doctor_id = input("\nEnter the ID of the GP to delete (or 'c' to cancel): ").strip()
    if doctor_id.lower() == 'c':
        return
    
    # Find the doctor to delete
    doctor_found = False
    updated_doctors = []
    for doctor in doctors:
        if doctor['id'] == doctor_id:
            doctor_found = True
            print(f"\nAre you sure you want to delete '{doctor['full_name']}'?")
            print("Warning: This will also delete all associated appointments.")
            confirm = input("Type 'yes' to confirm: ").strip().lower()
            if confirm != 'yes':
                print("\nDeletion cancelled.")
                input("\nPress Enter to continue...")
                return
        else:
            updated_doctors.append(doctor)
    
    if not doctor_found:
        print("\n❌ GP not found.")
        input("\nPress Enter to continue...")
        return
    
    # Save updated doctors list
    if save_csv_data(DOCTORS_FILE, updated_doctors, doctors[0].keys() if doctors else []):
        print("\n✅ GP deleted successfully!")
        # Note: In a real system, we would also need to handle or delete associated appointments
    else:
        print("\n❌ Failed to delete GP.")
    
    input("\nPress Enter to continue...")

def cancel_appointment_admin():
    """管理员取消患者预约"""
    clear_screen()
    print("\n===== Admin: Cancel Appointment =====")

    print(f"Loading appointments from: {APPOINTMENTS_FILE}")
    appointments = load_csv_data(APPOINTMENTS_FILE)
    print(f"  → {len(appointments)} rows loaded")
    doctors   = load_csv_data(DOCTORS_FILE)
    clinics   = load_csv_data(CLINICS_FILE)
    users     = load_csv_data(USERS_FILE)

    now = datetime.now()
    upcoming = []
    for appt in appointments:
        dt_str = f"{appt.get('date','')} {appt.get('time','')}"
        try:
            appt_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        if appt.get('status','').strip().lower() == 'confirmed' and appt_dt > now:
            upcoming.append(appt)

    if not upcoming:
        print("No upcoming confirmed appointments to cancel.")
        input("\nPress Enter to continue...")
        return

    print(f"\n{'#':<3} {'Patient':<25} {'GP':<25} {'Date':<12} {'Time':<6} {'Clinic':<20}")
    print("-" * 95)
    for i, appt in enumerate(upcoming, start=1):
        doc = next((d for d in doctors if d['id'] == appt['doctor_id']), {})
        cli = next((c for c in clinics if c['id'] == appt['clinic_id']), {})
        print(f"{i:<3} {appt['patient_email']:<25} {doc.get('full_name',''):<25} "
              f"{appt['date']:<12} {appt['time']:<6} {cli.get('name',''):<20}")

    sel = input_with_validation(
        "\nEnter number to cancel (or 'c' to abort): ",
        lambda x: x.lower() == 'c' or (x.isdigit() and 1 <= int(x) <= len(upcoming)),
        "Invalid input."
    )
    if sel.lower() == 'c':
        return
    selected = upcoming[int(sel) - 1]

    confirm = input("Confirm cancel this appointment? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancellation aborted.")
        input("\nPress Enter to continue...")
        return

    # 修改 appointment 状态
    for appt in appointments:
        if appt['id'] == selected['id']:
            appt['status'] = 'cancelled by clinic'
            break

    if save_csv_data(APPOINTMENTS_FILE, appointments, appointments[0].keys()):
        # 恢复对应 slot 为可用
        slots = load_csv_data(SLOTS_FILE)
        for slot in slots:
            if (slot['doctor_id'] == selected['doctor_id'] and
                slot['date']      == selected['date'] and
                slot['time']      == selected['time']):
                slot['status'] = 'available'
                break
        save_csv_data(SLOTS_FILE, slots, slots[0].keys())

        # ── 写入通知中心 ──
        # 根据 patient_email 找到用户 ID
        patient = next((u for u in users if u.get('email') == selected['patient_email']), {})
        user_id = patient.get('id', selected['patient_email'])
        notifs = load_csv_data(NOTIFICATIONS_FILE)
        notifs.append({
            'user_id':   user_id,
            'message':   f"Your appointment {selected['date']} {selected['time']} has been canceled by clinic",
            'timestamp': now.strftime("%Y-%m-%d %H:%M"),
            'read':      'False'
        })
        save_csv_data(
            NOTIFICATIONS_FILE,
            notifs,
            notifs[0].keys() if notifs else ['user_id','message','timestamp','read']
        )

        # 显示取消确认
        clear_screen()
        doc = next((d for d in doctors if d['id'] == selected['doctor_id']), {})
        cli = next((c for c in clinics if c['id'] == selected['clinic_id']), {})
        print(f"\nNotification sent to patient {selected['patient_email']}")
        print("\nCancellation Details:")
        print(f"GP     : {doc.get('full_name','Unknown')}")
        print(f"Date   : {selected['date']}")
        print(f"Time   : {selected['time']}")
        print(f"Clinic : {cli.get('name','Unknown')}")
        input("\nPress Enter to continue...")
    else:
        print("Failed to cancel appointment. Please try again.")
        input("\nPress Enter to continue...")


def manage_gp_slots():
    """管理GP预约时段"""
    while True:
        choice = display_menu("Manage GP Appointment Slots", [
            "View GP Slots",
            "Add New Slots",
            "Update Slot Duration",
            "View Slot Statistics",
            "Return to Admin Menu"
        ])
        
        if choice == 1:
            view_gp_slots()
        elif choice == 2:
            add_new_slots()
        elif choice == 3:
            update_slot_duration()
        elif choice == 4:
            view_slot_statistics()
        elif choice == 5 or choice == 6:
            return

def view_gp_slots():
    """查看GP预约时段"""
    clear_screen()
    print("\n===== View GP Appointment Slots =====")
    
    # 加载数据
    slots = load_csv_data(SLOTS_FILE)
    doctors = load_csv_data(DOCTORS_FILE)
    clinics = load_csv_data(CLINICS_FILE)
    
    # 创建查找字典
    doctor_lookup = {doc['id']: doc for doc in doctors}
    clinic_lookup = {clinic['id']: clinic for clinic in clinics}
    
    # 显示筛选选项
    print("\nFilter Options:")
    print("1. Filter by GP")
    print("2. Filter by Clinic Suburb")
    print("3. Show all slots")
    print("4. Return to previous menu")  # 添加返回选项
    
    filter_choice = input_with_validation(
        "\nEnter your choice (1-4): ",  # 更新验证范围
        lambda x: x in ['1', '2', '3', '4'],
        "Please enter a valid choice (1-4)"
    ) 
    
    filtered_slots = slots
    
    if filter_choice == '1':
        # 显示所有GP
        print("\nAvailable GPs:")
        for doc in doctors:
            print(f"{doc['id']}: {doc['full_name']}")
        
        gp_id = input_with_validation(
            "\nEnter GP ID: ",
            lambda x: x in [doc['id'] for doc in doctors],
            "Please enter a valid GP ID"
        )
        filtered_slots = [slot for slot in slots if slot['doctor_id'] == gp_id]

    elif filter_choice == '4':
        return  # 返回上级菜单
        
    elif filter_choice == '2':
        # 显示所有诊所区域
        print("\nAvailable Clinic Suburbs:")
        suburbs = set()
        for clinic in clinics:
            location = clinic.get('location', '')
            suburb = location.split(',')[0] if ',' in location else location
            suburbs.add(suburb)
        
        # 显示带编号的选项
        suburb_list = sorted(list(suburbs))
        for i, suburb in enumerate(suburb_list, 1):
            print(f"{i}. {suburb}")
        
        # 验证用户输入
        suburb_choice = input_with_validation(
            "\nEnter suburb number: ",
            lambda x: x.isdigit() and 1 <= int(x) <= len(suburb_list),
            f"Please enter a number between 1 and {len(suburb_list)}"
        )
        
        selected_suburb = suburb_list[int(suburb_choice) - 1]
        clinic_ids = [c['id'] for c in clinics if selected_suburb.lower() in c.get('location', '').lower()]
        filtered_slots = [slot for slot in slots if slot['clinic_id'] in clinic_ids]
    
    # 显示筛选后的时段
    if not filtered_slots:
        print("\nNo slots found matching your criteria.")
    else:
        print(f"\n{'Date':<12} {'Time':<8} {'Duration':<10} {'GP':<25} {'Clinic':<25} {'Status':<15}")
        print("-" * 95)
        
        for slot in filtered_slots:
            doctor = doctor_lookup.get(slot['doctor_id'], {})
            clinic = clinic_lookup.get(slot['clinic_id'], {})
            
            print(f"{slot['date']:<12} {slot['time']:<8} {slot['duration']+'min':<10} "
                  f"{doctor.get('full_name', 'Unknown'):<25} "
                  f"{clinic.get('name', 'Unknown'):<25} "
                  f"{slot['status']:<15}")
    
    input("\nPress Enter to continue...")

def add_new_slots():
    """添加新的预约时段"""
    clear_screen()
    print("\n===== Add New Appointment Slots =====")
    
    # 加载数据
    doctors = load_csv_data(DOCTORS_FILE)
    clinics = load_csv_data(CLINICS_FILE)
    slots = load_csv_data(SLOTS_FILE)
    
    # 选择GP
    print("\nAvailable GPs:")
    for doc in doctors:
        print(f"{doc['id']}: {doc['full_name']}")
    
    gp_id = input_with_validation(
        "\nEnter GP ID (or input 'return' to exit): ",
        lambda x: x == 'return' or x in [doc['id'] for doc in doctors],
        "Please enter a valid GP ID or input 'return' to exit"
    )

    if gp_id == 'return':
        print("\nExiting to the previous menu...")
        return  # 返回上级菜单或退出当前操作
    
    # 选择诊所
    print("\nAvailable Clinics:")
    for clinic in clinics:
        print(f"{clinic['id']}: {clinic['name']} ({clinic.get('location', 'Unknown')})")
    
    clinic_id = input_with_validation(
        "\nEnter Clinic ID: ",
        lambda x: x in [c['id'] for c in clinics],
        "Please enter a valid Clinic ID"
    )
    
    # 选择日期
    date = input_with_validation(
        "\nEnter date (YYYY-MM-DD): ",
        is_valid_date_format,
        "Please enter a valid date format (YYYY-MM-DD)"
    )
    
    # 选择时段时长
    print("\nAvailable slot durations:")
    print("1. 15 minutes")
    print("2. 25 minutes")
    print("3. 40 minutes")
    print("4. 60 minutes")
    
    duration_choice = input_with_validation(
        "\nSelect duration (1-4): ",
        lambda x: x in ['1', '2', '3', '4'],
        "Please enter a valid choice (1-4)"
    )
    
    duration_map = {'1': '15', '2': '25', '3': '40', '4': '60'}
    duration = duration_map[duration_choice]
    
    # 选择时间段
    print("\nEnter time slots (24-hour format, e.g., 09:00, 10:00):")
    print("Enter times separated by commas, or 'done' to finish")
    
    new_slots = []
    while True:
        time_input = input("\nEnter time (or 'done'): ").strip()
        if time_input.lower() == 'done':
            break
            
        times = [t.strip() for t in time_input.split(',')]
        for time in times:
            # 验证时间格式
            try:
                datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            except ValueError:
                print(f"Invalid time format: {time}. Please use HH:MM format.")
                continue
            
            # 检查是否与现有时段冲突
            conflict = False
            for existing_slot in slots:
                if (existing_slot['doctor_id'] == gp_id and
                    existing_slot['date'] == date and
                    existing_slot['time'] == time):
                    print(f"Conflict: Slot already exists at {time}")
                    conflict = True
                    break
            
            if not conflict:
                new_slot = {
                    'id': str(get_next_id(slots)),
                    'doctor_id': gp_id,
                    'clinic_id': clinic_id,
                    'date': date,
                    'time': time,
                    'duration': duration,
                    'status': 'available'
                }
                new_slots.append(new_slot)
                print(f"Time slot {time} successfully added.")  # 添加反馈消息
    
    if new_slots:
        slots.extend(new_slots)
        if save_csv_data(SLOTS_FILE, slots, slots[0].keys()):
            print(f"\nSuccessfully added {len(new_slots)} new slots!")
        else:
            print("\nFailed to save new slots.")
    else:
        print("\nNo new slots were added.")
    
    input("\nPress Enter to continue...")

def update_slot_duration():
    """更新预约时段时长"""
    clear_screen()
    print("\n===== Update Slot Duration =====")
    
    # 加载数据
    slots = load_csv_data(SLOTS_FILE)
    doctors = load_csv_data(DOCTORS_FILE)
    
    # 选择GP
    print("\nAvailable GPs:")
    for doc in doctors:
        print(f"{doc['id']}: {doc['full_name']}")
    
    gp_id = input_with_validation(
        "\nEnter GP ID (or input 'return' to exit): ",
        lambda x: x == 'return' or x in [doc['id'] for doc in doctors],
        "Please enter a valid GP ID or input 'return' to exit"
    )

    if gp_id == 'return':
        print("\nExiting to the previous menu...")
        return  # 返回上级菜单或退出当前操作
    
    # 显示该GP的所有时段
    gp_slots = [slot for slot in slots if slot['doctor_id'] == gp_id]
    if not gp_slots:
        print("\nNo slots found for this GP.")
        input("\nPress Enter to continue...")
        return
    
    print(f"\n{'Date':<12} {'Time':<8} {'Current Duration':<15} {'Status':<15}")
    print("-" * 50)
    
    for slot in gp_slots:
        print(f"{slot['date']:<12} {slot['time']:<8} {slot['duration']+'min':<15} {slot['status']:<15}")
    
    # 选择要更新的时段
    date = input_with_validation(
        "\nEnter date to update (YYYY-MM-DD): ",
        is_valid_date_format,
        "Please enter a valid date format (YYYY-MM-DD)"
    )
    
    try:
        time = input_with_validation(
            "\nEnter time to update (HH:MM): ",
            lambda x: bool(datetime.strptime(f"{date} {x}", "%Y-%m-%d %H:%M")),
            "Please enter a valid time format (HH:MM)"
        )
    except ValueError:
        print("Invalid time format. Please use HH:MM format.")
        input("\nPress Enter to continue...")
        return
    
    # 选择新的时长
    print("\nAvailable slot durations:")
    print("1. 15 minutes")
    print("2. 25 minutes")
    print("3. 40 minutes")
    print("4. 60 minutes")
    
    duration_choice = input_with_validation(
        "\nSelect new duration (1-4): ",
        lambda x: x in ['1', '2', '3', '4'],
        "Please enter a valid choice (1-4)"
    )
    
    duration_map = {'1': '15', '2': '25', '3': '40', '4': '60'}
    new_duration = duration_map[duration_choice]
    
    # 更新时段
    updated = False
    for slot in slots:
        if (slot['doctor_id'] == gp_id and
            slot['date'] == date and
            slot['time'] == time):
            slot['duration'] = new_duration
            updated = True
            break
    
    if updated:
        if save_csv_data(SLOTS_FILE, slots, slots[0].keys()):
            print("\nSlot duration updated successfully!")
        else:
            print("\nFailed to update slot duration.")
    else:
        print("\nNo matching slot found.")
    
    input("\nPress Enter to continue...")

def view_slot_statistics():
    """查看预约时段统计信息"""
    clear_screen()
    print("\n===== Slot Statistics =====")
    
    # 加载数据
    slots = load_csv_data(SLOTS_FILE)
    doctors = load_csv_data(DOCTORS_FILE)
    clinics = load_csv_data(CLINICS_FILE)
    
    # 创建查找字典
    doctor_lookup = {doc['id']: doc for doc in doctors}
    clinic_lookup = {clinic['id']: clinic for clinic in clinics}
    
    # 按GP统计
    print("\nStatistics by GP:")
    print(f"{'GP Name':<25} {'Total Slots':<15} {'Available':<15} {'Booked':<15}")
    print("-" * 70)
    
    gp_stats = {}
    for slot in slots:
        gp_id = slot['doctor_id']
        if gp_id not in gp_stats:
            gp_stats[gp_id] = {'total': 0, 'available': 0, 'booked': 0}
        
        gp_stats[gp_id]['total'] += 1
        if slot['status'] == 'available':
            gp_stats[gp_id]['available'] += 1
        else:
            gp_stats[gp_id]['booked'] += 1
    
    for gp_id, stats in gp_stats.items():
        gp_name = doctor_lookup.get(gp_id, {}).get('full_name', 'Unknown')
        print(f"{gp_name:<25} {stats['total']:<15} {stats['available']:<15} {stats['booked']:<15}")
    
    # 按诊所区域统计
    print("\nStatistics by Clinic Suburb:")
    print(f"{'Suburb':<25} {'Total Slots':<15} {'Available':<15} {'Booked':<15}")
    print("-" * 70)
    
    suburb_stats = {}
    for slot in slots:
        clinic = clinic_lookup.get(slot['clinic_id'], {})
        location = clinic.get('location', '')
        suburb = location.split(',')[0] if ',' in location else location
        
        if suburb not in suburb_stats:
            suburb_stats[suburb] = {'total': 0, 'available': 0, 'booked': 0}
        
        suburb_stats[suburb]['total'] += 1
        if slot['status'] == 'available':
            suburb_stats[suburb]['available'] += 1
        else:
            suburb_stats[suburb]['booked'] += 1
    
    for suburb, stats in suburb_stats.items():
        print(f"{suburb:<25} {stats['total']:<15} {stats['available']:<15} {stats['booked']:<15}")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    # For testing the module directly
    admin_menu()