import os
from utils.helpers import clear_screen, display_menu, input_with_validation
from utils.helpers import is_valid_date_format, load_csv_data, save_csv_data, get_next_id
from datetime import datetime, timedelta


DATA_DIR = '../data'
APPOINTMENTS_FILE = os.path.join(DATA_DIR, 'appointments.csv')
CLINICS_FILE = os.path.join(DATA_DIR, 'clinics.csv')
DOCTORS_FILE = os.path.join(DATA_DIR, 'doctors.csv')
SLOTS_FILE = os.path.join(DATA_DIR, 'slots.csv')
USERS_FILE = os.path.join(DATA_DIR, 'users.csv')
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, 'notifications.csv')

def patient_menu(patient_email):
    """Main patient menu"""
    while True:
        choice = display_menu("Patient Menu", [
            "Book Appointment",
            "View My Appointments",
            "Edit Profile",
            "View Notifications",
            "Logout"
        ])
        
        if choice == 1:
            book_appointment(patient_email)
        elif choice == 2:
            view_appointments(patient_email)
        elif choice == 3:  
            edit_profile(patient_email)
        elif choice == 4:
            view_notifications(patient_email)
        elif choice == 5:
            return  # Return to login screen
def edit_profile(patient_email):
    """Edit patient profile information"""
    clear_screen()
    print("\n===== Edit Profile =====")
    
    # 加载用户数据
    users = load_csv_data(USERS_FILE)
    
    # 查找当前患者
    patient = None
    patient_index = -1
    for i, user in enumerate(users):
        if user['email'].lower() == patient_email.lower() and user['role'] == 'patient':
            patient = user
            patient_index = i
            break
    
    if not patient:
        print("\n❌ Error: Patient profile not found.")
        input("\nPress Enter to continue...")
        return False
    
    # 显示当前资料
    print("\nCurrent Profile Information:")
    print(f"Email: {patient.get('email', 'Not set')}")
    print(f"First Name: {patient.get('first_name', 'Not set')}")
    print(f"Last Name: {patient.get('last_name', 'Not set')}")
    print(f"Mobile Number: {patient.get('mobile', 'Not set')}")
    print(f"Address: {patient.get('address', 'Not set')}")
    
    print("\nLeave any field blank to keep current value.")
    print("Note: Email cannot be changed as it is used for account identification.")
    
    # 收集更新的信息
    first_name = input_with_validation(
        f"\nFirst Name [{patient.get('first_name', '')}]: ",
        lambda x: x == "" or (x.strip() != "" and x.isalpha()),
        "First name must contain only letters."
    )
    
    last_name = input_with_validation(
        f"Last Name [{patient.get('last_name', '')}]: ",
        lambda x: x == "" or (x.strip() != "" and x.isalpha()),
        "Last name must contain only letters."
    )
    
    mobile = input_with_validation(
        f"Mobile Number [{patient.get('mobile', '')}]: ",
        lambda x: x == "" or (x.strip() != "" and x.strip().isdigit() and len(x.strip()) == 10 and x.strip().startswith(('04', '05'))),
        "Mobile number must be a valid 10-digit Australian number starting with 04 or 05."
    )
    
    address = input(f"Address [{patient.get('address', '')}]: ")
    
    # 确认更改
    print("\nReview your changes:")
    if first_name:
        print(f"First Name: {patient.get('first_name', 'Not set')} -> {first_name}")
    if last_name:
        print(f"Last Name: {patient.get('last_name', 'Not set')} -> {last_name}")
    if mobile:
        print(f"Mobile Number: {patient.get('mobile', 'Not set')} -> {mobile}")
    if address:
        print(f"Address: {patient.get('address', 'Not set')} -> {address}")
    
    if not (first_name or last_name or mobile or address):
        print("No changes made.")
        input("\nPress Enter to continue...")
        return False
    
    confirm = input("\nSave these changes? (y/n): ").strip().lower()
    if confirm != 'y':
        print("\n❌ Changes cancelled.")
        input("\nPress Enter to continue...")
        return False
    
    # 更新患者信息
    if first_name:
        patient['first_name'] = first_name
    if last_name:
        patient['last_name'] = last_name
    if mobile:
        patient['mobile'] = mobile
    if address:
        patient['address'] = address
    
    # 保存更改
    users[patient_index] = patient
    if save_csv_data(USERS_FILE, users, patient.keys()):
        print("\n✅ Profile updated successfully!")
        input("\nPress Enter to continue...")
        return True
    else:
        print("\n❌ Failed to update profile. Please try again.")
        input("\nPress Enter to continue...")
        return False
    
def book_appointment(patient_email):
    """Book a new appointment"""
    clear_screen()
    print("\n===== Book New Appointment =====")
    
    # Load required data
    slots = load_csv_data(SLOTS_FILE)
    doctors = load_csv_data(DOCTORS_FILE)
    clinics = load_csv_data(CLINICS_FILE)
    
    # Create lookup dictionaries
    doctor_lookup = {doc['id']: doc for doc in doctors}
    clinic_lookup = {clinic['id']: clinic for clinic in clinics}
    
    # Filter only available slots
    available_slots = [slot for slot in slots if slot['status'] == 'available']
    
    if not available_slots:
        print("No available appointment slots found.")
        input("\nPress Enter to continue...")
        return
    
    # --- 直接显示筛选方法菜单 ---
    clear_screen()
    print("\n===== Book New Appointment =====")
    print("\n--- Choose Filter Method ---")
    print("1. Filter by GP")
    print("2. Filter by Date")
    print("3. Filter by Clinic")
    print("4. No filters (show all)")
    
    filter_method = input("\nEnter your choice (1-4): ").strip()
    
    # 初始化筛选条件
    doctor_filter = ""
    date_filter = ""
    suburb_filter = ""
    
    # 根据用户选择获取相应的筛选条件
    if filter_method == "1":
        # 显示可用医生
        print("\nAvailable GPs:")
        unique_doctors = set(slot['doctor_id'] for slot in available_slots)
        for doc_id in unique_doctors:
            if doc_id in doctor_lookup:
                doctor = doctor_lookup[doc_id]
                print(f"{doc_id}: {doctor['full_name']} ({doctor['specialty']})")
                
        doctor_filter = input("\nEnter GP ID (or press Enter for all): ").strip()
    elif filter_method == "2":
        date_filter = input("\nEnter date (YYYY-MM-DD): ").strip()
        # 验证日期格式
        if date_filter and not is_valid_date_format(date_filter):
            print("Invalid date format. Using format YYYY-MM-DD.")
            date_filter = ""
    elif filter_method == "3":
        # 显示可用诊所和区域
        print("\nAvailable Clinic Suburbs:")
        unique_clinics = set(slot['clinic_id'] for slot in available_slots)
        for clinic_id in unique_clinics:
            if clinic_id in clinic_lookup:
                location = clinic_lookup[clinic_id].get('location', '')
                suburb = location.split(',')[0] if ',' in location else location
                print(f"{clinic_id}: {suburb}")
                
        suburb_filter = input("\nEnter Clinic ID: ").strip()
    elif filter_method == "4":
        pass  # 不进行筛选
    else:
        print("Invalid choice. Showing all available slots.")
    
    # 应用筛选条件
    filtered_slots = available_slots
    if doctor_filter:
        filtered_slots = [slot for slot in filtered_slots if slot['doctor_id'] == doctor_filter]
    if date_filter:
        filtered_slots = [slot for slot in filtered_slots if slot['date'] == date_filter]
    if suburb_filter:
        filtered_slots = [slot for slot in filtered_slots if slot['clinic_id'] == suburb_filter]
    
    if not filtered_slots:
        print("\nNo slots match your filter criteria.")
        input("\nPress Enter to continue...")
        return
    
    # Display available slots
    clear_screen()
    print("\n===== Available Appointment Slots =====")
    print(f"{'#':<4} {'Date':<12} {'Time':<8} {'Duration':<10} {'Doctor':<25} {'Clinic':<30}")
    print("-" * 89)
    
    for i, slot in enumerate(filtered_slots, 1):
        doctor_name = doctor_lookup.get(slot['doctor_id'], {}).get('full_name', 'Unknown')
        clinic_name = clinic_lookup.get(slot['clinic_id'], {}).get('name', 'Unknown')
        print(f"{i:<4} {slot['date']:<12} {slot['time']:<8} {slot['duration']+'min':<10} "
              f"{doctor_name:<25} {clinic_name:<30}")
    
    # Get user selection
    while True:
        selection = input("\nEnter slot number to view details (or 'c' to cancel): ").strip()
        
        if selection.lower() == 'c':
            return
        
        try:
            slot_index = int(selection) - 1
            if 0 <= slot_index < len(filtered_slots):
                selected_slot = filtered_slots[slot_index]
                display_slot_details(selected_slot, doctor_lookup, clinic_lookup)
                
                book_choice = input("\nWould you like to book this appointment? (y/n): ").strip().lower()
                if book_choice == 'y':
                    create_new_appointment(patient_email, selected_slot)
                    return
                else:
                    # Return to slot selection
                    clear_screen()
                    print("\n===== Available Appointment Slots =====")
                    print(f"{'#':<4} {'Date':<12} {'Time':<8} {'Duration':<10} {'Doctor':<25} {'Clinic':<30}")
                    print("-" * 89)
                    
                    for i, slot in enumerate(filtered_slots, 1):
                        doctor_name = doctor_lookup.get(slot['doctor_id'], {}).get('full_name', 'Unknown')
                        clinic_name = clinic_lookup.get(slot['clinic_id'], {}).get('name', 'Unknown')
                        print(f"{i:<4} {slot['date']:<12} {slot['time']:<8} {slot['duration']+'min':<10} "
                            f"{doctor_name:<25} {clinic_name:<30}")
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def display_slot_details(slot, doctor_lookup, clinic_lookup):
    """Display detailed information about a specific appointment slot"""
    clear_screen()
    print("\n===== Appointment Details =====")
    
    doctor = doctor_lookup.get(slot['doctor_id'], {})
    clinic = clinic_lookup.get(slot['clinic_id'], {})
    
    print(f"Date: {slot['date']}")
    print(f"Time: {slot['time']}")
    print(f"Duration: {slot['duration']} minutes")
    print(f"Doctor: {doctor.get('full_name', 'Unknown')}")
    print(f"Specialty: {doctor.get('specialty', 'Unknown')}")
    print(f"\nClinic: {clinic.get('name', 'Unknown')}")
    print(f"Address: {clinic.get('location', 'Unknown')}")
    print(f"Services: {clinic.get('services', 'Unknown')}")
    print(f"Operating Hours: {clinic.get('operating_hours', 'Unknown')}")
    
    print("\nCancellation Policy: Appointments can be cancelled at no charge up to 24 hours before the scheduled time.")

def create_new_appointment(patient_email, slot):
    """Create a new appointment based on the selected slot"""
    appointments = load_csv_data(APPOINTMENTS_FILE)
    new_id = get_next_id(appointments)
    
    # Ask for the reason for the appointment
    reason = input_with_validation("\nPlease enter the reason for your appointment: ", 
                                  lambda x: x.strip() != "", 
                                  "Reason cannot be empty.")
    
    # Create new appointment record
    new_appointment = {
        'id': new_id,
        'patient_email': patient_email,
        'doctor_id': slot['doctor_id'],
        'clinic_id': slot['clinic_id'],
        'date': slot['date'],
        'time': slot['time'],
        'duration': slot['duration'],
        'reason': reason,
        'status': 'confirmed'
    }
    
    # Display confirmation screen
    clear_screen()
    print("\n===== Appointment Confirmation =====")
    print("\nPlease review your appointment details:")
    
    # Load doctor and clinic information
    doctors = load_csv_data(DOCTORS_FILE)
    clinics = load_csv_data(CLINICS_FILE)
    doctor_lookup = {doc['id']: doc for doc in doctors}
    clinic_lookup = {clinic['id']: clinic for clinic in clinics}
    
    doctor = doctor_lookup.get(slot['doctor_id'], {})
    clinic = clinic_lookup.get(slot['clinic_id'], {})
    
    print(f"Date: {new_appointment['date']}")
    print(f"Time: {new_appointment['time']}")
    print(f"Duration: {new_appointment['duration']} minutes")
    print(f"Doctor: {doctor.get('full_name', 'Unknown')}")
    print(f"Specialty: {doctor.get('specialty', 'Unknown')}")
    print(f"Clinic: {clinic.get('name', 'Unknown')}")
    print(f"Address: {clinic.get('location', 'Unknown')}")
    print(f"Reason: {reason}")
    
    confirm = input("\nConfirm booking? (y/n): ").strip().lower()
    if confirm != 'y':
        print("\n❌ Booking cancelled.")
        input("\nPress Enter to continue...")
        return
    
    # Update slot status and save appointment
    update_slot_status(slot['id'], 'booked')
    appointments.append(new_appointment)
    
    # Save updated appointments
    if save_csv_data(APPOINTMENTS_FILE, appointments, new_appointment.keys()):
        print("\n✅ Appointment booked successfully!")
        
        # Ask if the user wants to view their appointments
        view_choice = input("\nWould you like to view your appointments? (y/n): ").strip().lower()
        if view_choice == 'y':
            view_appointments(patient_email)
            return
    else:
        print("\n❌ Failed to book appointment.")
    
    input("\nPress Enter to continue...")

def update_slot_status(slot_id, new_status):
    """Update a slot's status in the slots CSV file"""
    slots = load_csv_data(SLOTS_FILE)
    
    for slot in slots:
        if slot['id'] == slot_id:
            slot['status'] = new_status
            break
    
    fieldnames = slots[0].keys() if slots else []
    return save_csv_data(SLOTS_FILE, slots, fieldnames)

def view_appointments(patient_email):
    """View and filter existing appointments"""
    clear_screen()
    print("\n===== My Appointments =====")
    
    # Load data
    appointments = load_csv_data(APPOINTMENTS_FILE)
    doctors = load_csv_data(DOCTORS_FILE)
    clinics = load_csv_data(CLINICS_FILE)
    
    # Create lookup dictionaries
    doctor_lookup = {doc['id']: doc for doc in doctors}
    clinic_lookup = {clinic['id']: clinic for clinic in clinics}
    
    # 更新过期预约的状态
    now = datetime.now()
    updated = False
    for appt in appointments:
        if appt['patient_email'] == patient_email:
            try:
                appt_date = datetime.strptime(f"{appt['date']} {appt['time']}", "%Y-%m-%d %H:%M")
                # 如果预约已过期且状态仍为confirmed，标记为attended
                if appt_date < now and appt['status'] == 'confirmed':
                    appt['status'] = 'attended'
                    updated = True
            except ValueError:
                pass
    
    # 如果有状态更新，保存到文件
    if updated:
        save_csv_data(APPOINTMENTS_FILE, appointments, appointments[0].keys())
    
    # Filter appointments for this patient
    my_appointments = [appt for appt in appointments if appt['patient_email'] == patient_email]
    
    if not my_appointments:
        print("You have no appointments.")
        input("\nPress Enter to continue...")
        return
    
    # 初始化筛选变量
    filtered_appointments = my_appointments
    filter_active = False
    filter_description = "All appointments"
    view_mode = "all"  # 默认查看所有预约
    
    while True:
        clear_screen()
        print("\n===== My Appointments =====")
        
        # 显示当前的查看模式和筛选条件
        if view_mode == "upcoming":
            print("Viewing: Upcoming appointments")
        elif view_mode == "past":
            print("Viewing: Past appointments")
        else:
            print("Viewing: All appointments")
            
        if filter_active:
            print(f"Filter: {filter_description}")
        
        # 根据当前时间区分过去和未来的预约
        now = datetime.now()
        current_appts = []
        
        for appt in filtered_appointments:
            try:
                appt_date = datetime.strptime(f"{appt['date']} {appt['time']}", "%Y-%m-%d %H:%M")
                # 根据查看模式筛选预约
                if view_mode == "upcoming" and appt_date > now and appt['status'] == 'confirmed':
                    current_appts.append(appt)
                elif view_mode == "past" and (appt_date <= now or appt['status'] == 'cancelled' or 
                                              appt['status'] == 'cancelled by patient' or appt['status'] == 'attended'):
                    current_appts.append(appt)
                elif view_mode == "all":
                    current_appts.append(appt)
            except ValueError:
                # 日期格式错误的情况下，仍然显示该预约
                if (view_mode == "upcoming" and appt['status'] == 'confirmed') or \
                   (view_mode == "past" and (appt['status'] == 'cancelled' or appt['status'] == 'cancelled by patient' or 
                                            appt['status'] == 'attended')) or \
                   view_mode == "all":
                    current_appts.append(appt)
        
        # 按日期和时间排序
        current_appts.sort(key=lambda x: (x['date'], x['time']))
        
        # 只显示要求的四个字段
        print(f"\n{'#':<3} {'GP Name':<25} {'Date':<12} {'Time':<8} {'Clinic Suburb':<25} {'Status':<15}")
        print("-" * 98)
        
        if not current_appts:
            print("\nNo appointments found matching your criteria.")
        else:
            for i, appt in enumerate(current_appts, 1):
                doctor = doctor_lookup.get(appt['doctor_id'], {})
                clinic = clinic_lookup.get(appt['clinic_id'], {})
                
                doctor_name = doctor.get('full_name', 'Unknown')
                location = clinic.get('location', '')
                suburb = location.split(',')[0] if ',' in location else location
                
                # 美化状态显示
                status = appt['status']
                if status == 'confirmed':
                    status_display = "Confirmed"
                elif status == 'cancelled':
                    status_display = "Cancelled by Clinic"
                elif status == 'cancelled by patient':
                    status_display = "Cancelled by Patient"
                elif status == 'attended':
                    status_display = "Attended"
                else:
                    status_display = status.capitalize()
                
                print(f"{i:<3} {doctor_name:<25} {appt['date']:<12} {appt['time']:<8} "
                      f"{suburb:<25} {status_display:<15}")
        
        # 修改：菜单选项，移除不必要的"查看全部预约"选项
        print("\nOptions:")
        print("1. View appointment details")
        print("2. Cancel an appointment")
        print("3. View upcoming appointments")
        print("4. View past appointments")
        # 移除了选项5（View all appointments）
        print("5. Filter by date")         # 原先的选项6，现在是选项5
        print("6. Filter by GP")           # 原先的选项7，现在是选项6
        print("7. Filter by clinic suburb") # 原先的选项8，现在是选项7
        print("8. Clear filters")           # 原先的选项9，现在是选项8
        print("0. Return to main menu")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            # 查看预约详情
            if not current_appts:
                print("\nNo appointments to view.")
                input("\nPress Enter to continue...")
                continue
                
            appt_num = input_with_validation("\nEnter appointment number to view details (or 'c' to cancel): ",
                                           lambda x: x.lower() == 'c' or (x.isdigit() and 1 <= int(x) <= len(current_appts)),
                                           "Please enter a valid appointment number or 'c' to cancel.")
            
            if appt_num.lower() == 'c':
                continue
                
            # 显示选中预约的详细信息
            view_appointment_details(current_appts[int(appt_num) - 1], doctor_lookup, clinic_lookup)
            
        elif choice == '2':
            # 取消预约功能
            cancel_appointment(current_appts, patient_email)
            # 重新加载预约，以反映变化
            appointments = load_csv_data(APPOINTMENTS_FILE)
            my_appointments = [appt for appt in appointments if appt['patient_email'] == patient_email]
            # 重置筛选条件
            if filter_active:
                filtered_appointments = apply_filters(my_appointments, filter_description)
            else:
                filtered_appointments = my_appointments
                
        elif choice == '3':
            # 查看即将到来的预约
            view_mode = "upcoming"
            
        elif choice == '4':
            # 查看过去的预约
            view_mode = "past"
            
        elif choice == '5': # 原先的选项6
            # 按日期筛选
            date_filter = input_with_validation("Enter date (YYYY-MM-DD): ", 
                                              is_valid_date_format, 
                                              "Please enter a valid date format (YYYY-MM-DD)")
            filtered_appointments = [appt for appt in my_appointments if appt['date'] == date_filter]
            filter_active = True
            filter_description = f"Date: {date_filter}"
            view_mode = "all"  # 重置视图模式为全部
            
        elif choice == '6': # 原先的选项7
            # 按GP筛选
            print("\nYour doctors:")
            unique_doctors = set(appt['doctor_id'] for appt in my_appointments)
            for doc_id in unique_doctors:
                if doc_id in doctor_lookup:
                    print(f"- {doctor_lookup[doc_id]['full_name']}")
            
            gp_filter = input("Enter GP name (partial name is OK): ").strip()
            filtered_appointments = []
            
            for appt in my_appointments:
                doctor_name = doctor_lookup.get(appt['doctor_id'], {}).get('full_name', '').lower()
                if gp_filter.lower() in doctor_name:
                    filtered_appointments.append(appt)
                    
            filter_active = True
            filter_description = f"GP: {gp_filter}"
            view_mode = "all"  # 重置视图模式为全部
            
        elif choice == '7': # 原先的选项8
            # 按诊所区域筛选
            print("\nYour clinic suburbs:")
            unique_clinics = set(appt['clinic_id'] for appt in my_appointments)
            suburbs = []
            for clinic_id in unique_clinics:
                if clinic_id in clinic_lookup:
                    location = clinic_lookup[clinic_id].get('location', '')
                    suburb = location.split(',')[0] if ',' in location else location
                    suburbs.append(suburb)
                    print(f"- {suburb}")
            
            suburb_filter = input("Enter clinic suburb: ").strip()
            filtered_appointments = []
            
            for appt in my_appointments:
                clinic_location = clinic_lookup.get(appt['clinic_id'], {}).get('location', '').lower()
                suburb = clinic_location.split(',')[0].lower() if ',' in clinic_location else clinic_location.lower()
                if suburb_filter.lower() in suburb:
                    filtered_appointments.append(appt)
                    
            filter_active = True
            filter_description = f"Suburb: {suburb_filter}"
            view_mode = "all"  # 重置视图模式为全部
            
        elif choice == '8': # 原先的选项9
            # 清除筛选条件
            filtered_appointments = my_appointments
            filter_active = False
            filter_description = "All appointments"
            view_mode = "all"  # 重置视图模式为全部
            
        elif choice == '0':
            # 返回主菜单
            return
            
        # 添加一个"全部"选项的快捷方式
        elif choice == '9':
            view_mode = "all"
            filtered_appointments = my_appointments
            filter_active = False
            filter_description = "All appointments"
            
        else:
            input("Invalid choice. Press Enter to continue...")


def view_appointment_details(appointment, doctor_lookup, clinic_lookup):
    """显示单个预约的详细信息"""
    clear_screen()
    print("\n===== Appointment Details =====")
    
    # 获取医生和诊所信息
    doctor = doctor_lookup.get(appointment['doctor_id'], {})
    clinic = clinic_lookup.get(appointment['clinic_id'], {})
    
    # 显示详细信息
    print(f"\nDate: {appointment['date']}")
    print(f"Time: {appointment['time']}")
    print(f"Duration: {appointment.get('duration', 'N/A')} minutes")
    
    print(f"\nGP Information:")
    print(f"Name: {doctor.get('full_name', 'Unknown')}")
    print(f"Specialty: {doctor.get('specialty', 'Unknown')}")
    
    print(f"\nClinic Information:")
    print(f"Name: {clinic.get('name', 'Unknown')}")
    print(f"Address: {clinic.get('location', 'Unknown')}")
    print(f"Phone: {clinic.get('phone', 'Unknown')}")
    
    # 美化状态显示
    status = appointment.get('status', 'Unknown')
    if status == 'confirmed':
        status_display = "Confirmed"
    elif status == 'cancelled':
        status_display = "Cancelled by Clinic"
    elif status == 'cancelled by patient':
        status_display = "Cancelled by Patient"
    elif status == 'attended':
        status_display = "Attended"
    else:
        status_display = status.capitalize()
    
    print(f"\nAppointment Information:")
    print(f"Reason: {appointment.get('reason', 'Not specified')}")
    print(f"Status: {status_display}")
    
    # 确定预约是过去的还是未来的
    try:
        now = datetime.now()
        appt_date = datetime.strptime(f"{appointment['date']} {appointment['time']}", "%Y-%m-%d %H:%M")
        
        if appt_date > now:
            time_diff = appt_date - now
            days, remainder = divmod(time_diff.total_seconds(), 86400)
            hours, remainder = divmod(remainder, 3600)
            print(f"\nThis appointment is in the future.")
            print(f"Time until appointment: {int(days)} days and {int(hours)} hours")
        else:
            print(f"\nThis appointment is in the past.")
    except ValueError:
        pass
    
    input("\nPress Enter to return to appointment list...")

def apply_filters(appointments, filter_description):
    """根据筛选描述应用筛选条件"""
    if "Date:" in filter_description:
        date_filter = filter_description.split("Date:")[1].strip()
        return [appt for appt in appointments if appt['date'] == date_filter]
    elif "GP:" in filter_description:
        gp_filter = filter_description.split("GP:")[1].strip().lower()
        filtered = []
        from utils.helpers import load_csv_data
        doctors = load_csv_data(DOCTORS_FILE)
        doctor_lookup = {doc['id']: doc for doc in doctors}
        
        for appt in appointments:
            doctor_name = doctor_lookup.get(appt['doctor_id'], {}).get('full_name', '').lower()
            if gp_filter in doctor_name:
                filtered.append(appt)
        return filtered
    elif "Suburb:" in filter_description:
        suburb_filter = filter_description.split("Suburb:")[1].strip().lower()
        filtered = []
        from utils.helpers import load_csv_data
        clinics = load_csv_data(CLINICS_FILE)
        clinic_lookup = {clinic['id']: clinic for clinic in clinics}
        
        for appt in appointments:
            clinic_location = clinic_lookup.get(appt['clinic_id'], {}).get('location', '').lower()
            suburb = clinic_location.split(',')[0].lower() if ',' in clinic_location else clinic_location.lower()
            if suburb_filter in suburb:
                filtered.append(appt)
        return filtered
    else:
        return appointments


def cancel_appointment(appointments, patient_email):
    """Cancel an existing appointment"""
    if not appointments:
        print("\nNo appointments available to cancel.")
        input("\nPress Enter to continue...")
        return
    
    # 筛选出状态为confirmed的预约和未来的预约
    now = datetime.now()
    active_appointments = []
    
    for appt in appointments:
        try:
            appt_date = datetime.strptime(f"{appt['date']} {appt['time']}", "%Y-%m-%d %H:%M")
            if appt['status'] == 'confirmed' and appt_date > now:
                active_appointments.append(appt)
        except ValueError:
            # 如果日期格式有问题，仍然考虑该预约
            if appt['status'] == 'confirmed':
                active_appointments.append(appt)
    
    if not active_appointments:
        print("\nYou have no upcoming confirmed appointments to cancel.")
        input("\nPress Enter to continue...")
        return
    
    # 显示可取消的预约
    clear_screen()
    print("\n===== Cancel Appointment =====")
    print("\nYour upcoming appointments:")
    print(f"\n{'#':<3} {'GP Name':<25} {'Date':<12} {'Time':<8} {'Clinic Suburb':<25}")
    print("-" * 83)
    
    from utils.helpers import load_csv_data
    doctors = load_csv_data(DOCTORS_FILE)
    clinics = load_csv_data(CLINICS_FILE)
    doctor_lookup = {doc['id']: doc for doc in doctors}
    clinic_lookup = {clinic['id']: clinic for clinic in clinics}
    
    for i, appt in enumerate(active_appointments, 1):
        doctor = doctor_lookup.get(appt['doctor_id'], {})
        clinic = clinic_lookup.get(appt['clinic_id'], {})
        
        doctor_name = doctor.get('full_name', 'Unknown')
        location = clinic.get('location', '')
        suburb = location.split(',')[0] if ',' in location else location
        
        print(f"{i:<3} {doctor_name:<25} {appt['date']:<12} {appt['time']:<8} {suburb:<25}")
    
    appt_num = input_with_validation("\nEnter the number of the appointment to cancel (or 'c' to cancel): ",
                                   lambda x: x.lower() == 'c' or (x.isdigit() and 1 <= int(x) <= len(active_appointments)),
                                   "Please enter a valid appointment number or 'c' to cancel.")
    
    if appt_num.lower() == 'c':
        return
    
    # 获取选择的预约
    selected_appt = active_appointments[int(appt_num) - 1]
    
    # 计算当前时间与预约时间的差距
    now = datetime.now()
    appt_date = datetime.strptime(f"{selected_appt['date']} {selected_appt['time']}", "%Y-%m-%d %H:%M")
    time_diff = appt_date - now
    
    # 显示取消确认和可能的罚款
    clear_screen()
    print("\n===== Cancel Appointment =====")
    print(f"\nDate: {selected_appt['date']}")
    print(f"Time: {selected_appt['time']}")
    
    doctor = doctor_lookup.get(selected_appt['doctor_id'], {})
    clinic = clinic_lookup.get(selected_appt['clinic_id'], {})
    
    print(f"Doctor: {doctor.get('full_name', 'Unknown')}")
    print(f"Clinic: {clinic.get('name', 'Unknown')}")
    
    # 根据预约时间与当前时间的差距确定是否收取罚款
    free_cancellation = time_diff.total_seconds() >= 24 * 3600  # 24小时以秒表示
    
    if free_cancellation:
        print("\n✅ Free cancellation available (more than 24 hours before appointment)")
    else:
        hours_remaining = time_diff.total_seconds() / 3600
        print(f"\n⚠️ Late cancellation fee applies (less than 24 hours notice)")
        print(f"Hours until appointment: {hours_remaining:.1f} hours")
        print("A $20 cancellation fee may be charged to your account.")
    
    # 确认取消
    confirm = input("\nAre you sure you want to cancel this appointment? (y/n): ").strip().lower()
    if confirm != 'y':
        print("\nCancellation aborted.")
        input("\nPress Enter to continue...")
        return
    
    # 更新所有预约数据
    all_appointments = load_csv_data(APPOINTMENTS_FILE)
    for appt in all_appointments:
        if appt['id'] == selected_appt['id']:
            appt['status'] = 'cancelled by patient'  # 更新状态为"由患者取消"
            break
    
    # 保存更改
    if save_csv_data(APPOINTMENTS_FILE, all_appointments, all_appointments[0].keys() if all_appointments else []):
        # 释放时间槽以供其他人使用
        slots = load_csv_data(SLOTS_FILE)
        for slot in slots:
            if (slot['doctor_id'] == selected_appt['doctor_id'] and
                slot['date'] == selected_appt['date'] and
                slot['time'] == selected_appt['time']):
                slot['status'] = 'available'
                break
        
        save_csv_data(SLOTS_FILE, slots, slots[0].keys() if slots else [])
        
        # 显示取消确认通知
        clear_screen()
        print("\n===== Appointment Cancellation Confirmation =====")
        print("\n✅ Your appointment has been successfully cancelled.")
        
        if not free_cancellation:
            print("\n⚠️ Note: A late cancellation fee of $20 may apply to your account.")
            print("Please contact the clinic for any billing inquiries.")
        
        # 模拟发送邮件确认
        print(f"\nA cancellation confirmation has been sent to {patient_email}")
        print("\nCancellation Details:")
        print(f"Date: {selected_appt['date']}")
        print(f"Time: {selected_appt['time']}")
        print(f"Doctor: {doctor.get('full_name', 'Unknown')}")
        print(f"Clinic: {clinic.get('name', 'Unknown')}")
        
        input("\nPress Enter to continue...")
    else:
        print("\n❌ Failed to cancel appointment. Please try again.")
        input("\nPress Enter to continue...")

def view_notifications(patient_email):
    """View patient's notifications"""
    notifications = load_csv_data(NOTIFICATIONS_FILE)

    # 筛选出该用户的通知（以 email 为 user_id）
    my_notes = [n for n in notifications if n['user_id'].lower() == patient_email.lower()]

    if not my_notes:
        print("\nYou have no notifications.")
    else:
        print("\n=== Your Notifications ===")
        for n in my_notes:
            print(f"[{n['timestamp']}] {n['message']}")
            n['read'] = 'True'

        # 保存更新的通知状态（标记为已读）
        save_csv_data(NOTIFICATIONS_FILE, notifications, notifications[0].keys())

    input("\nPress Enter to return.")



if __name__ == "__main__":
    # For testing the module directly
    patient_menu("test@example.com")