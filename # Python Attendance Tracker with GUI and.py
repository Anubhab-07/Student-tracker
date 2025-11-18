# Python Attendance Tracker with GUI and CSV storage
import tkinter as tk
from tkinter import messagebox
import csv
import os
from datetime import date

# Initialize main window
root = tk.Tk()
root.title("Student Attendance Tracker")

# Data structures to store students and their attendance status variables
students = []               # list to hold student names
attendance_vars = {}        # maps student name -> StringVar for 'P'/'A'
ROW_START = 2               # first row index where student rows start

# Function to add a new student
def add_student():
    name = name_entry.get().strip()
    if not name:
        messagebox.showwarning("Input Error", "Student name cannot be empty.")
        return
    if name in students:
        messagebox.showwarning("Duplicate Entry", f"{name} is already in the student list.")
        return

    students.append(name)
    # Create a StringVar for this student's attendance status (default to 'P'resent)
    attendance_vars[name] = tk.StringVar(value="P")

    # Place label and radio buttons for Present/Absent in the next available row
    row = ROW_START + len(students) - 1
    tk.Label(root, text=name).grid(row=row, column=0, padx=5, pady=2, sticky="w")
    tk.Radiobutton(root, text="Present", variable=attendance_vars[name], value="P").grid(row=row, column=1)
    tk.Radiobutton(root, text="Absent", variable=attendance_vars[name], value="A").grid(row=row, column=2)

    name_entry.delete(0, tk.END)


# Function to save attendance data to a CSV file
def save_attendance():
    if not students:
        messagebox.showwarning("No Students", "Add students before saving attendance.")
        return

    today = date.today().isoformat()
    filename = "attendance.csv"

    # Read existing entries to avoid duplicates for the same date
    existing_entries = set()
    if os.path.isfile(filename):
        try:
            with open(filename, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_entries.add((row.get("Name"), row.get("Date")))
        except Exception as e:
            messagebox.showerror("File Error", f"Error reading existing file: {e}")
            return

    # Open file for append, write header if file doesn't exist
    try:
        file_exists = os.path.isfile(filename)
        with open(filename, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["Name", "Date", "Status"])
            written_count = 0
            for name in students:
                status = attendance_vars[name].get().upper()
                if (name, today) in existing_entries:
                    # skip duplicate record for same student & date
                    continue
                writer.writerow([name, today, status])
                written_count += 1
        messagebox.showinfo("Success", f"Attendance for {today} saved to {filename} ({written_count} new rows).")
    except Exception as e:
        messagebox.showerror("File Error", f"Error writing to file: {e}")


# Function to calculate and show attendance percentages
def show_percentages():
    filename = "attendance.csv"
    if not os.path.isfile(filename):
        messagebox.showwarning("No Data", "No attendance records found.")
        return

    totals = {}
    present = {}

    try:
        with open(filename, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row.get("Name")
                status = row.get("Status", "").strip().upper()
                if not name:
                    continue
                totals[name] = totals.get(name, 0) + 1
                if status == "P":
                    present[name] = present.get(name, 0) + 1

        # calculate percentage and prepare result text
        if not totals:
            messagebox.showinfo("Attendance Percentage", "No valid attendance data found.")
            return

        result_lines = []
        for name in sorted(totals):
            total = totals[name]
            pres = present.get(name, 0)
            percent = (pres / total) * 100 if total > 0 else 0
            result_lines.append(f"{name}: {percent:.1f}% ({pres}/{total})")

        result_msg = "\n".join(result_lines)
        messagebox.showinfo("Attendance Percentage", result_msg)
    except Exception as e:
        messagebox.showerror("File Error", f"Error reading file: {e}")


# UI layout: input field and buttons
tk.Label(root, text="Student Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Add Student", command=add_student).grid(row=0, column=2, padx=5, pady=5)

tk.Button(root, text="Save Attendance", command=save_attendance, bg="lightgreen").grid(row=1, column=0, padx=5, pady=5)
tk.Button(root, text="Show Percentages", command=show_percentages, bg="lightblue").grid(row=1, column=1, padx=5, pady=5)

# Start the GUI event loop
root.mainloop()
