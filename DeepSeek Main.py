import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Database Setup
db_file = "clinic.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        complaint TEXT,
        diagnosis TEXT,
        treatment TEXT,
        next_visit TEXT
    )
''')
conn.commit()
conn.close()

# Main Application
class ClinicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clinic Management")
        self.root.geometry("500x400")
        
        # Search Bar
        self.search_var = tk.StringVar()
        tk.Entry(root, textvariable=self.search_var).pack(pady=5)
        tk.Button(root, text="Search", command=self.search_patient).pack()
        self.search_var.trace("w", lambda *args: self.search_patient())
        
        # Table
        self.tree = ttk.Treeview(root, columns=("Name", "Date"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Date", text="Date")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.load_patient_data)
        
        # Buttons
        tk.Button(root, text="Add", command=self.open_form).pack(pady=5)
        
        self.load_patients()
    
    def load_patients(self):
        self.tree.delete(*self.tree.get_children())
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name, date FROM patients")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()
    
    def search_patient(self):
        query = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name, date FROM patients WHERE LOWER(name) LIKE ?", (f"{query}%",))
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()
    
    def open_form(self, patient_data=None):
        form = tk.Toplevel(self.root)
        form.title("Patient Form")
        form.geometry("300x300")
        
        tk.Label(form, text="Name:").pack()
        name_entry = tk.Entry(form)
        name_entry.pack()
        tk.Label(form, text="Date:").pack()
        date_entry = tk.Entry(form)
        date_entry.pack()
        tk.Label(form, text="Complaint:").pack()
        complaint_entry = tk.Entry(form)
        complaint_entry.pack()
        tk.Label(form, text="Diagnosis:").pack()
        diagnosis_entry = tk.Entry(form)
        diagnosis_entry.pack()
        tk.Label(form, text="Treatment:").pack()
        treatment_entry = tk.Entry(form)
        treatment_entry.pack()
        tk.Label(form, text="Next Visit:").pack()
        next_visit_entry = tk.Entry(form)
        next_visit_entry.pack()
        
        if patient_data:
            name_entry.insert(0, patient_data[0])
            date_entry.insert(0, patient_data[1])
            complaint_entry.insert(0, patient_data[2] or "")
            diagnosis_entry.insert(0, patient_data[3] or "")
            treatment_entry.insert(0, patient_data[4] or "")
            next_visit_entry.insert(0, patient_data[5] or "")
        
        def save_data():
            name = name_entry.get()
            date = date_entry.get()
            complaint = complaint_entry.get()
            diagnosis = diagnosis_entry.get()
            treatment = treatment_entry.get()
            next_visit = next_visit_entry.get()
            if not name or not date:
                messagebox.showerror("Error", "Name and Date are required!")
                return
            
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("REPLACE INTO patients (name, date, complaint, diagnosis, treatment, next_visit) VALUES (?, ?, ?, ?, ?, ?)",
                           (name, date, complaint, diagnosis, treatment, next_visit))
            conn.commit()
            conn.close()
            
            self.load_patients()
            form.destroy()
        
        tk.Button(form, text="Save", command=save_data).pack(pady=10)
    
    def load_patient_data(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        name, date = self.tree.item(selected_item, "values")
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE name = ? AND date = ?", (name, date))
        data = cursor.fetchone()
        conn.close()
        if data:
            self.open_form(data[1:])

root = tk.Tk()
app = ClinicApp(root)
root.mainloop()
