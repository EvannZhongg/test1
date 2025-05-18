import csv
import os
from datetime import datetime, timedelta

DATA_DIR = '../data'
os.makedirs(DATA_DIR, exist_ok=True)

def create_users_csv():
    """Create sample users data"""
    filepath = os.path.join(DATA_DIR, 'users.csv')
    with open(filepath, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['email', 'password', 'role'])
        writer.writerow(['admin@example.com', 'admin123', 'admin'])
        writer.writerow(['doctor@example.com', 'doctor123', 'doctor'])
        writer.writerow(['patient@example.com', 'patient123', 'patient'])
        writer.writerow(['user@example.com', 'user123', 'patient'])
    print(f"Created {filepath}")

def create_clinics_csv():
    """Create sample clinics data"""
    filepath = os.path.join(DATA_DIR, 'clinics.csv')
    with open(filepath, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'name', 'location', 'services', 'operating_hours'])
        writer.writerow(['1', 'Monash Medical Center', 'Clayton, VIC 3168', 'General Practice, Pediatrics, Dermatology', 'Mon-Fri: 8am-6pm, Sat: 9am-1pm'])
        writer.writerow(['2', 'City Health Clinic', 'Melbourne CBD, VIC 3000', 'General Practice, Psychology, Nutrition', 'Mon-Fri: 7am-8pm, Sat-Sun: 9am-5pm'])
        writer.writerow(['3', 'Eastside Family Practice', 'Ringwood, VIC 3134', 'General Practice, Women\'s Health, Immunization', 'Mon-Fri: 8:30am-5:30pm'])
    print(f"Created {filepath}")

def create_doctors_csv():
    """Create sample doctors data"""
    filepath = os.path.join(DATA_DIR, 'doctors.csv')
    with open(filepath, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'full_name', 'email', 'clinic_id', 'specialty', 'availability'])
        writer.writerow(['1', 'Dr. John Smith', 'john.smith@example.com', '1', 'General Practitioner', 'Mon,Tue,Thu,Fri: 9am-5pm'])
        writer.writerow(['2', 'Dr. Sarah Johnson', 'sarah.johnson@example.com', '1', 'Pediatrician', 'Mon,Wed,Fri: 8am-4pm'])
        writer.writerow(['3', 'Dr. Michael Chen', 'michael.chen@example.com', '2', 'General Practitioner', 'Mon-Fri: 7am-3pm'])
        writer.writerow(['4', 'Dr. Lisa Wong', 'lisa.wong@example.com', '2', 'Psychologist', 'Tue,Thu: 10am-6pm, Sat: 9am-1pm'])
        writer.writerow(['5', 'Dr. James Wilson', 'james.wilson@example.com', '3', 'General Practitioner', 'Mon,Wed,Fri: 9am-6pm'])
    print(f"Created {filepath}")

def create_slots_csv():
    """Create available appointment slots"""
    filepath = os.path.join(DATA_DIR, 'slots.csv')
    
    # Generate dates for the next 14 days
    start_date = datetime.now()
    dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 15)]
    
    with open(filepath, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'doctor_id', 'clinic_id', 'date', 'time', 'duration', 'status'])
        
        slot_id = 1
        # Generate slots for each doctor across dates
        for doctor_id in range(1, 6):
            clinic_id = str((doctor_id - 1) // 2 + 1)  # Map doctors to clinics
            for date in dates:
                # Morning slots (9:00 - 12:00)
                for hour in [9, 10, 11]:
                    # 15分钟时段
                    writer.writerow([str(slot_id), str(doctor_id), clinic_id, date, f"{hour}:00", "15", "available"])
                    slot_id += 1
                    writer.writerow([str(slot_id), str(doctor_id), clinic_id, date, f"{hour}:15", "15", "available"])
                    slot_id += 1
                    writer.writerow([str(slot_id), str(doctor_id), clinic_id, date, f"{hour}:30", "15", "available"])
                    slot_id += 1
                    writer.writerow([str(slot_id), str(doctor_id), clinic_id, date, f"{hour}:45", "15", "available"])
                    slot_id += 1
                
                # Afternoon slots (13:00 - 17:00)
                for hour in [13, 14, 15, 16]:
                    # 15分钟时段
                    writer.writerow([str(slot_id), str(doctor_id), clinic_id, date, f"{hour}:00", "15", "available"])
                    slot_id += 1
                    writer.writerow([str(slot_id), str(doctor_id), clinic_id, date, f"{hour}:15", "15", "available"])
                    slot_id += 1
                    writer.writerow([str(slot_id), str(doctor_id), clinic_id, date, f"{hour}:30", "15", "available"])
                    slot_id += 1
                    writer.writerow([str(slot_id), str(doctor_id), clinic_id, date, f"{hour}:45", "15", "available"])
                    slot_id += 1
    
    print(f"Created {filepath}")

def create_appointments_csv():
    """Create empty appointments file with header"""
    filepath = os.path.join(DATA_DIR, 'appointments.csv')
    with open(filepath, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'patient_email', 'doctor_id', 'clinic_id', 'date', 'time', 'duration', 'reason', 'status'])
    print(f"Created {filepath}")

def main():
    """Set up all required data files"""
    os.makedirs(DATA_DIR, exist_ok=True)
    create_users_csv()
    create_clinics_csv()
    create_doctors_csv()
    create_slots_csv()
    create_appointments_csv()
    print("All sample data files created successfully!")

if __name__ == "__main__":
    main()