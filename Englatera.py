import datetime


# ---------------- GLOBAL DATA ---------------- #
patients = {}  # patient_name -> {'password': ..., 'contact': ...}
appointments = []  # List of dicts: {'patient': ..., 'date': ..., 'time': ..., 'status': ...}
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# ---------------- LOGIN & REGISTER ---------------- #
def register_patient():
    print("\n=== Patient Registration ===")
    name = input("Enter name: ").strip()
    if name in patients:
        print("Account already exists.")
        return
    password = input("Create password: ").strip()
    contact = input("Enter contact: ").strip()
    patients[name] = {"password": password, "contact": contact}
    print("Registration successful. You can now log in.")


def login():
    print("\n=== LOGIN ===")
    username = input("Username: ").strip()
    password = input("Password: ").strip()


    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        print("Admin logged in.")
        admin_menu()
    elif username in patients and patients[username]["password"] == password:
        print(f"Welcome, {username}.")
        patient_menu(username)
    else:
        print("Invalid credentials.")
        reg = input("Not registered? Type 'register' to register, or press Enter to try again: ").strip().lower()
        if reg == "register":
            register_patient()


# ---------------- PATIENT FEATURES ---------------- #
def view_schedules():
    print("\nAvailable Schedules: Monday–Friday 9AM–5PM")
    scheduled = [a for a in appointments if a["status"] == "scheduled"]
    if scheduled:
        print("Scheduled Appointments:")
        for a in scheduled:
            t = datetime.datetime.strptime(a["time"], "%H:%M").strftime("%I:%M %p")
            print(f"{a['date']} at {t}: {a['patient']}")
    else:
        print("No scheduled appointments.")


def patient_book(name):
    date = input("Enter date (YYYY-MM-DD): ").strip()
    try:
        d = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        today = datetime.date.today()
        if d < today or d.weekday() >= 5:
            print("Invalid date. Must be Mon–Fri, today or future.")
            return
    except ValueError:
        print("Invalid date format.")
        return
    time_slot = input("Enter time (HH:MM AM/PM): ").strip()
    try:
        t_obj = datetime.datetime.strptime(time_slot, "%I:%M %p").time()
        if not (datetime.time(9,0) <= t_obj <= datetime.time(17,0)):
            print("Time must be between 9AM–5PM.")
            return
        time_24 = t_obj.strftime("%H:%M")
    except ValueError:
        print("Invalid time format.")
        return


    if sum(1 for a in appointments if a["date"] == date and a["status"] in ["pending","scheduled"]) >= 5:
        print("Daily limit reached.")
        return
    if any(a["date"] == date and a["time"] == time_24 and a["status"] in ["pending","scheduled"] for a in appointments):
        print("Slot not available.")
        return


    appointments.append({"patient": name, "date": date, "time": time_24, "status": "pending"})
    print("Appointment request submitted. Waiting for admin approval.")


def patient_view_status(name):
    user_appts = [a for a in appointments if a["patient"] == name]
    if user_appts:
        for a in user_appts:
            t = datetime.datetime.strptime(a["time"], "%H:%M").strftime("%I:%M %p")
            print(f"Date: {a['date']}, Time: {t}, Status: {a['status']}")
    else:
        print("No appointments found.")


def patient_cancel(name):
    for a in appointments:
        if a["patient"] == name and a["status"] == "pending":
            appointments.remove(a)
            print("Pending request canceled.")
            return
    print("No pending request found.")


# ---------------- ADMIN FEATURES ---------------- #
def admin_manage_patients():
    while True:
        print("\n1. View Patients\n2. Delete Patient\n3. Back")
        choice = input("Choose: ").strip()
        if choice=="1":
            if not patients:
                print("No patients.")
            else:
                for n, info in patients.items():
                    print(f"{n}: {info['contact']}")
        elif choice=="2":
            name = input("Patient to delete: ").strip()
            if name in patients:
                del patients[name]
                global appointments
                appointments = [a for a in appointments if a["patient"] != name]
                print("Patient and appointments deleted.")
            else:
                print("Patient not found.")
        elif choice=="3":
            break
        else:
            print("Invalid choice. Please try again.")


def admin_manage_appointments():
    while True:
        print("\n1. View Pending\n2. Accept\n3. Reject\n4. View Scheduled\n5. Cancel Scheduled\n6. Back")
        choice = input("Choose: ").strip()
        pending = [a for a in appointments if a["status"] == "pending"]


        if choice=="1":
            if pending:
                for i,a in enumerate(pending,1):
                    t = datetime.datetime.strptime(a["time"], "%H:%M").strftime("%I:%M %p")
                    print(f"{i}. {a['patient']}: {a['date']} {t}")
            else:
                print("No pending requests.")
        elif choice=="2":
            if not pending:
                print("No pending requests.")
                continue
            for i,a in enumerate(pending,1):
                t = datetime.datetime.strptime(a["time"], "%H:%M").strftime("%I:%M %p")
                print(f"{i}. {a['patient']}: {a['date']} {t}")
            try:
                idx = int(input("Request number to accept: ").strip())-1
                if 0<=idx<len(pending):
                    a = pending[idx]
                    if sum(1 for ap in appointments if ap["date"]==a["date"] and ap["status"]=="scheduled")>=5:
                        print("Cannot accept. Daily limit reached.")
                        continue
                    a["status"]="scheduled"
                    print("Appointment scheduled.")
                else:
                    print("Invalid number.")
            except ValueError:
                print("Invalid input.")
        elif choice=="3":
            if not pending:
                print("No pending requests.")
                continue
            for i,a in enumerate(pending,1):
                t = datetime.datetime.strptime(a["time"], "%H:%M").strftime("%I:%M %p")
                print(f"{i}. {a['patient']}: {a['date']} {t}")
            try:
                idx = int(input("Request number to reject: ").strip())-1
                if 0<=idx<len(pending):
                    appointments.remove(pending[idx])
                    print("Request rejected.")
                else:
                    print("Invalid number.")
            except ValueError:
                print("Invalid input.")
        elif choice=="4":
            scheduled = [a for a in appointments if a["status"]=="scheduled"]
            if scheduled:
                for a in scheduled:
                    t = datetime.datetime.strptime(a["time"], "%H:%M").strftime("%I:%M %p")
                    print(f"{a['patient']}: {a['date']} {t}")
            else:
                print("No scheduled appointments.")
        elif choice=="5":
            name = input("Patient to cancel: ").strip()
            found=False
            for a in appointments:
                if a["patient"]==name and a["status"]=="scheduled":
                    appointments.remove(a)
                    print("Scheduled appointment canceled.")
                    found=True
                    break
            if not found:
                print("No scheduled appointment found.")
        elif choice=="6":
            break
        else:
            print("Invalid choice. Please try again.")


# ---------------- MENUS ---------------- #
def patient_menu(name):
    while True:
        print(f"\n=== PATIENT MENU ({name}) ===")
        print("1. View Schedules\n2. Book Appointment\n3. View Status\n4. Cancel Request\n5. Logout")
        choice = input("Choose: ").strip()
        if choice=="1": view_schedules()
        elif choice=="2": patient_book(name)
        elif choice=="3": patient_view_status(name)
        elif choice=="4": patient_cancel(name)
        elif choice=="5": break
        else: print("Invalid choice. Please try again.")


def admin_menu():
    while True:
        print("\n=== ADMIN MENU ===")
        print("1. Manage Patients\n2. Manage Appointments\n3. Logout")
        choice = input("Choose: ").strip()
        if choice=="1": admin_manage_patients()
        elif choice=="2": admin_manage_appointments()
        elif choice=="3": break
        else: print("Invalid choice. Please try again.")


# ---------------- MAIN ---------------- #
def main():
    while True:
        login()


if __name__=="__main__":
    main()

