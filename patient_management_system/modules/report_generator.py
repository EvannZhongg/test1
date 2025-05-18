# patient_management_system/modules/report_generator.py

import os
import csv
from datetime import datetime
from utils.helpers import (
    clear_screen,
    input_with_validation,
    is_valid_date_format,
    load_csv_data
)

DATA_DIR = '../data'
APPOINTMENTS_FILE = os.path.join(DATA_DIR, 'appointments.csv')
CLINICS_FILE      = os.path.join(DATA_DIR, 'clinics.csv')
DOCTORS_FILE      = os.path.join(DATA_DIR, 'doctors.csv')


def _prompt_date_range():
    """Ask user for optional start/end dates in YYYY-MM-DD format."""
    print("\nEnter date range for the report (YYYY-MM-DD). Leave blank for no limit.")
    start = input_with_validation(
        "Start date: ",
        lambda x: x == "" or is_valid_date_format(x),
        "Invalid format. Use YYYY-MM-DD."
    )
    end = input_with_validation(
        "End date: ",
        lambda x: x == "" or is_valid_date_format(x),
        "Invalid format. Use YYYY-MM-DD."
    )
    # parse as midnight of that day
    start_dt = datetime.strptime(start, "%Y-%m-%d") if start else None
    end_dt   = datetime.strptime(end,   "%Y-%m-%d") if end   else None
    return start_dt, end_dt


def _filter_by_date(appts, start_dt, end_dt):
    """Keep only those appointments whose datetime falls within [start_dt, end_dt]."""
    if not start_dt and not end_dt:
        return appts

    filtered = []
    for a in appts:
        dt_str = f"{a['date']} {a['time']}"
        # parse "YYYY-MM-DD H:MM" or "YYYY-MM-DD HH:MM"
        try:
            a_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except ValueError:
            # in case seconds are present or unexpected format, you could add more patterns here
            raise ValueError(f"Cannot parse appointment datetime: {dt_str}")
        if (not start_dt or a_dt >= start_dt) and (not end_dt or a_dt <= end_dt):
            filtered.append(a)
    return filtered


def generate_clinic_report():
    clear_screen()
    print("\n===== Clinic Report =====")

    # load data
    appts   = load_csv_data(APPOINTMENTS_FILE)
    clinics = load_csv_data(CLINICS_FILE)
    doctors = {d['id']: d for d in load_csv_data(DOCTORS_FILE)}

    # # date filter
    # start_dt, end_dt = _prompt_date_range()
    # appts = _filter_by_date(appts, start_dt, end_dt)

    # date filter
    while True:
        print("\nEnter date range for the report (YYYY-MM-DD). Leave blank for no limit.")
        print("Type 'back' to return to the main menu.")
        start_date_input = input("Start date: ").strip()
        if start_date_input.lower() == 'back':
            print("Returning to the main menu...")
            return  # 或者调用主菜单函数，例如 main_menu()
        end_date_input = input("End date: ").strip()
        if end_date_input.lower() == 'back':
            print("Returning to the main menu...")
            return  # 或者调用主菜单函数，例如 main_menu()
    
        try:
            start_dt = datetime.strptime(start_date_input, "%Y-%m-%d") if start_date_input else None
            end_dt = datetime.strptime(end_date_input, "%Y-%m-%d") if end_date_input else None
            break
        except ValueError:
            print("Invalid date format. Please try again.")
    
    appts = _filter_by_date(appts, start_dt, end_dt)

    # aggregate
    agg = {}
    for a in appts:
        cid = a['clinic_id']
        clinic = agg.setdefault(cid, {'total': 0, 'by_gp': {}, 'by_type': {}})
        clinic['total'] += 1
        clinic['by_gp'][a['doctor_id']] = clinic['by_gp'].get(a['doctor_id'], 0) + 1
        reason = a.get('reason', 'Unknown')
        clinic['by_type'][reason] = clinic['by_type'].get(reason, 0) + 1

    # display
    for cid, data in agg.items():
        name = next((c['name'] for c in clinics if c['id'] == cid), 'Unknown')
        print(f"\nClinic: {name}  (Total patients: {data['total']})")
        print(" • Appointments per GP:")
        for gid, cnt in data['by_gp'].items():
            gname = doctors.get(gid, {}).get('full_name', 'Unknown')
            print(f"    - {gname}: {cnt}")
        print(" • Breakdown by type:")
        for typ, cnt in data['by_type'].items():
            print(f"    - {typ}: {cnt}")

    # export
    choice = input("\nExport report? (1) CSV  (2) Text  (Enter to skip): ").strip()
    if choice in ('1', '2'):
        fmt = 'csv' if choice == '1' else 'txt'
        start_tag = start_dt.date() if start_dt else 'all'
        end_tag   = end_dt.date()   if end_dt   else 'all'
        fname = f"clinic_report_{start_tag}_{end_tag}.{fmt}"
        path = os.path.join(DATA_DIR, fname)

        with open(path, 'w', newline='') as f:
            if fmt == 'csv':
                w = csv.writer(f)
                w.writerow(['Clinic', 'Total', 'GP', 'GP Count', 'Type', 'Type Count'])
                for cid, data in agg.items():
                    clinic_name = next((c['name'] for c in clinics if c['id'] == cid), '')
                    for gid, cnt in data['by_gp'].items():
                        for typ, tcnt in data['by_type'].items():
                            w.writerow([clinic_name, data['total'],
                                        doctors.get(gid, {}).get('full_name', ''),
                                        cnt, typ, tcnt])
            else:
                for cid, data in agg.items():
                    clinic_name = next((c['name'] for c in clinics if c['id'] == cid), '')
                    f.write(f"Clinic: {clinic_name} (Total: {data['total']})\n")
                    f.write("  GP Counts:\n")
                    for gid, cnt in data['by_gp'].items():
                        f.write(f"    {doctors.get(gid, {}).get('full_name', '')}: {cnt}\n")
                    f.write("  Type Breakdown:\n")
                    for typ, tcnt in data['by_type'].items():
                        f.write(f"    {typ}: {tcnt}\n")
                    f.write("\n")

        print(f"\n Report exported to {path}")

    input("\nPress Enter to continue...")


def generate_gp_report():
    clear_screen()
    print("\n===== GP Report =====")

    appts   = load_csv_data(APPOINTMENTS_FILE)
    doctors = load_csv_data(DOCTORS_FILE)

    # # date filter
    # start_dt, end_dt = _prompt_date_range()
    # appts = _filter_by_date(appts, start_dt, end_dt)

    while True:
        print("\nEnter date range for the report (YYYY-MM-DD). Leave blank for no limit.")
        print("Type 'back' to return to the main menu.")
        start_date_input = input("Start date: ").strip()
        if start_date_input.lower() == 'back':
            print("Returning to the main menu...")
            return
        end_date_input = input("End date: ").strip()
        if end_date_input.lower() == 'back':
            print("Returning to the main menu...")
            return

        try:
            start_dt = datetime.strptime(start_date_input, "%Y-%m-%d") if start_date_input else None
            end_dt = datetime.strptime(end_date_input, "%Y-%m-%d") if end_date_input else None
            break
        except ValueError:
            print("Invalid date format. Please try again.")

    appts = _filter_by_date(appts, start_dt, end_dt)

    # aggregate per GP
    agg = {}
    for a in appts:
        gid = a['doctor_id']
        gp  = agg.setdefault(gid, {'total': 0, 'by_clinic': {}, 'by_type': {}})
        gp['total'] += 1
        gp['by_clinic'][a['clinic_id']] = gp['by_clinic'].get(a['clinic_id'], 0) + 1
        reason = a.get('reason', 'Unknown')
        gp['by_type'][reason] = gp['by_type'].get(reason, 0) + 1

    # display
    for gid, data in agg.items():
        name = next((d['full_name'] for d in doctors if d['id'] == gid), 'Unknown')
        print(f"\nGP: {name}  (Total patients: {data['total']})")
        print(" • Appointments per Clinic:")
        clinics = load_csv_data(CLINICS_FILE)
        for cid, cnt in data['by_clinic'].items():
            cname = next((c['name'] for c in clinics if c['id'] == cid), 'Unknown')
            print(f"    - {cname}: {cnt}")
        print(" • Breakdown by type:")
        for typ, cnt in data['by_type'].items():
            print(f"    - {typ}: {cnt}")

    # export
    choice = input("\nExport report? (1) CSV  (2) Text  (Enter to skip): ").strip()
    if choice in ('1', '2'):
        fmt = 'csv' if choice == '1' else 'txt'
        start_tag = start_dt.date() if start_dt else 'all'
        end_tag   = end_dt.date()   if end_dt   else 'all'
        fname = f"gp_report_{start_tag}_{end_tag}.{fmt}"
        path = os.path.join(DATA_DIR, fname)

        with open(path, 'w', newline='') as f:
            if fmt == 'csv':
                w = csv.writer(f)
                w.writerow(['GP', 'Total', 'Clinic', 'Clinic Count', 'Type', 'Type Count'])
                for gid, data in agg.items():
                    gp_name = next((d['full_name'] for d in doctors if d['id'] == gid), '')
                    for cid, cnt in data['by_clinic'].items():
                        for typ, tcnt in data['by_type'].items():
                            w.writerow([gp_name, data['total'], cid, cnt, typ, tcnt])
            else:
                for gid, data in agg.items():
                    gp_name = next((d['full_name'] for d in doctors if d['id'] == gid), '')
                    f.write(f"GP: {gp_name} (Total: {data['total']})\n")
                    f.write("  Clinic Counts:\n")
                    clinics = load_csv_data(CLINICS_FILE)
                    for cid, cnt in data['by_clinic'].items():
                        cname = next((c['name'] for c in clinics if c['id'] == cid), '')
                        f.write(f"    {cname}: {cnt}\n")
                    f.write("  Type Breakdown:\n")
                    for typ, tcnt in data['by_type'].items():
                        f.write(f"    {typ}: {tcnt}\n")
                    f.write("\n")

        print(f"\n Report exported to {path}")

    input("\nPress Enter to continue...")
