import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Database setup
def initialize_db():
    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
                      id INTEGER PRIMARY KEY,
                      name TEXT,
                      date TEXT,
                      complaint TEXT,
                      diagnosis TEXT,
                      treatment TEXT,
                      next_visit TEXT)''')
    conn.commit()
    conn.close()

def fetch_patients():
    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, date FROM patients")
    data = cursor.fetchall()
    conn.close()
    return data

# Pop-up form to add/edit patients
def open_form(name="", date="", complaint="", diagnosis="", treatment="", next_visit=""):
    def save_data():
        new_name = entry_name.get()
        new_date = entry_date.get()
        new_complaint = entry_complaint.get()
        new_diagnosis = entry_diagnosis.get()
        new_treatment = entry_treatment.get()
        new_next = entry_next.get()
        
        if not new_name or not new_date:
            messagebox.showerror("Error", "Name and Date are required!")
            return

        conn = sqlite3.connect("clinic.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM patients WHERE name = ?", (new_name,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE patients SET date=?, complaint=?, diagnosis=?, treatment=?, next_visit=?
                WHERE name=?
            """, (new_date, new_complaint, new_diagnosis, new_treatment, new_next, new_name))
        else:
            cursor.execute("""
                INSERT INTO patients (name, date, complaint, diagnosis, treatment, next_visit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (new_name, new_date, new_complaint, new_diagnosis, new_treatment, new_next))

        conn.commit()
        conn.close()
        refresh_table()
        form.destroy()
    
    form = tk.Toplevel(root)
    form.title("Patient Form")
    form.geometry("300x300")
    
    tk.Label(form, text="Name:").pack()
    entry_name = tk.Entry(form)
    entry_name.pack()
    entry_name.insert(0, name)
    
    tk.Label(form, text="Date:").pack()
    entry_date = tk.Entry(form)
    entry_date.pack()
    entry_date.insert(0, date)
    
    tk.Label(form, text="Complaint:").pack()
    entry_complaint = tk.Entry(form)
    entry_complaint.pack()
    entry_complaint.insert(0, complaint)
    
    tk.Label(form, text="Diagnosis:").pack()
    entry_diagnosis = tk.Entry(form)
    entry_diagnosis.pack()
    entry_diagnosis.insert(0, diagnosis)
    
    tk.Label(form, text="Treatment:").pack()
    entry_treatment = tk.Entry(form)
    entry_treatment.pack()
    entry_treatment.insert(0, treatment)
    
    tk.Label(form, text="Next Visit:").pack()
    entry_next = tk.Entry(form)
    entry_next.pack()
    entry_next.insert(0, next_visit)
    
    tk.Button(form, text="Save", command=save_data).pack()

def on_patient_click(event):
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        name = item['values'][0]
        conn = sqlite3.connect("clinic.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE name = ?", (name,))
        data = cursor.fetchone()
        conn.close()
        if data:
            open_form(*data[1:])

def refresh_table():
    tree.delete(*tree.get_children())
    for row in fetch_patients():
        tree.insert("", "end", values=row)

def search_patient(event):
    query = search_var.get().lower()
    tree.delete(*tree.get_children())
    for row in fetch_patients():
        if query in row[0].lower():
            tree.insert("", "end", values=row)

# GUI Setup
root = tk.Tk()
root.title("Clinic Management")
root.geometry("500x400")

frame = tk.Frame(root)
frame.pack()

tree = ttk.Treeview(frame, columns=("Name", "Date"), show="headings")
tree.heading("Name", text="Name")
tree.heading("Date", text="Date")
tree.bind("<Double-1>", on_patient_click)
tree.pack()

search_var = tk.StringVar()
search_entry = tk.Entry(root, textvariable=search_var)
search_entry.pack()
search_entry.bind("<KeyRelease>", search_patient)

tk.Button(root, text="Add", command=lambda: open_form()).pack()

tree.pack()

initialize_db()
refresh_table()
root.mainloop()
