# Clinic Patient Management System

## Name
Clinic Patient Management System

## Description
A text-based appointment and clinic management system developed for the FIT5136 Software Engineering unit. 

**The system enables patients to:**
Register and securely log in using their Monash email
Book, cancel, and view appointments
Filter available time slots by clinic, GP, and date
Manage their profile and view past/upcoming appointment history
Receive appointment-related notifications

**Administrators can:**
Securely log in as admin
Add, update, or delete GP and clinic information
Configure GP availability and manage time slots
Cancel patient appointments and notify them
Generate reports on clinic and GP workloads and appointment statistics

The project is developed using Python 3.11 and strictly follows Agile methodology, object-oriented design, and user-centered development practices. No database is used — all data is stored in .csv and .txt files.

## Installation

### Requirements
- Python 3.11.x
- Compatible IDE (e.g., PyCharm, VSCode)
- No database is used — all data is stored in `.csv` or `.txt` files

### Steps
1. Clone the repository:
   ```bash
   git clone https://gitlab.com/your-repo/clinic-management.git
   cd clinic-management
   ```
2. Run the application:
   ```bash
   python main.py
   ```

## Usage
- **Patients** can log in to view and book available time slots, cancel appointments, and see their appointment history.
- **Admins** can add, edit, or delete GPs and clinics and configure schedules.

## Features

✅ Implemented (as of Sprint 4):
🧑‍⚕️ **Patient Features**
-  Monash-only email registration with validation
-  Password validation and login
-  View, filter, and book available appointments
-  Cancel appointments (with 24-hour policy)
-  View upcoming and past appointments
-  View/edit personal profile details
-  Receive system notifications (e.g., cancellations)

👩‍💼 **Admin Features**
- Admin login (fixed account)
-  Add, update, delete GPs and clinics
-  Manage appointment availability and capacity
-  Cancel appointments and notify patients
-  Auto-update appointments if GP/clinic info changes
-  Generate GP-wise and clinic-wise reports (CSV export)

📊 **Reporting**
- Appointment reports by:
 GP
 Clinic
- Reason for Visit (pie percentage format)
- Custom date filtering support
- Export reports to .csv or .txt

## Roadmap
- Sprint 1: Planning & setup ✅
- Sprint 2: Core functionality (login, booking, cancellation) ✅
- Sprint 3: Code review & refinement ✅
- Sprint 4: Final delivery & demonstration 🚀

## Contributing
This project is a group coursework assignment. Contributions are limited to team members and follow an Agile sprint workflow, using Trello and GitLab collaboratively. Each merge request must include peer-reviewed feedback and adhere to acceptance criteria.

## Authors and acknowledgment

| Name        | Role             | Responsibilities                                                                 |
|-------------|------------------|----------------------------------------------------------------------------------|
| Zang Hao    | Scrum Master    | Sprint planning, task tracking, coordination via Trello & GitLab                |
| Ma Yonghao   | Product Manager | User story refinement, backlog maintenance, and feature prioritization           |
| Ye Zihan  | Software Engineer | Appointment booking feature development and patient-side flow implementation    |
| Zhong Jiarui  | Software Engineer | Admin login and GP/clinic management module development                 |

## Project status
🟢 Active – Sprint 1，Sprint 2 and Sprint 3 are completed, Sprint 4 is in development.

## Note
All code commits are reviewed via GitLab Merge Requests.
UI/UX is entirely terminal-based (text interface).
System is fully testable via black-box testing.
Input validation and informative feedback have been integrated throughout.

