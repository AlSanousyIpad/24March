import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from fpdf import FPDF  # For PDF export
import os  # For folder creation

# Database setup
def create_db():
    conn = sqlite3.connect('patients.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS patients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  date TEXT NOT NULL,
                  complaint TEXT,
                  diagnosis TEXT,
                  treatment TEXT,
                  next TEXT)''')
    conn.commit()
    conn.close()

# Main Application
class PatientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Patient Management System")

        # Create database and table if not exists
        create_db()

        # Main Window Widgets
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_table)

        self.search_entry = ttk.Entry(root, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=0, padx=10, pady=10)

        self.search_button = ttk.Button(root, text="Search", command=self.update_table)
        self.search_button.grid(row=0, column=1, padx=10, pady=10)

        self.add_button = ttk.Button(root, text="Add Patient", command=self.open_add_form)
        self.add_button.grid(row=0, column=2, padx=10, pady=10)

        self.delete_button = ttk.Button(root, text="Delete", command=self.delete_patient)
        self.delete_button.grid(row=0, column=3, padx=10, pady=10)

        self.create_folder_button = ttk.Button(root, text="Create Folder", command=self.create_folder)
        self.create_folder_button.grid(row=0, column=4, padx=10, pady=10)

        self.tree = ttk.Treeview(root, columns=("Name", "Date"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Date", text="Date")
        self.tree.grid(row=1, column=0, columnspan=5, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.on_patient_select)

        self.update_table()

    def update_table(self, *args):
        search_term = self.search_var.get()
        conn = sqlite3.connect('patients.db')
        c = conn.cursor()
        c.execute("SELECT name, date FROM patients WHERE name LIKE ?", (f'%{search_term}%',))
        rows = c.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=row)

    def open_add_form(self, patient_id=None):
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add Patient")

        self.patient_id = patient_id  # Store the patient ID for updates

        tk.Label(self.add_window, text="Name").grid(row=0, column=0, padx=10, pady=5)
        self.name_entry = ttk.Entry(self.add_window)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.add_window, text="Date").grid(row=1, column=0, padx=10, pady=5)
        self.date_entry = ttk.Entry(self.add_window)
        self.date_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.add_window, text="Complaint").grid(row=2, column=0, padx=10, pady=5)
        self.complaint_entry = ttk.Entry(self.add_window)
        self.complaint_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self.add_window, text="Diagnosis").grid(row=3, column=0, padx=10, pady=5)
        self.diagnosis_entry = ttk.Entry(self.add_window)
        self.diagnosis_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(self.add_window, text="Treatment").grid(row=4, column=0, padx=10, pady=5)
        self.treatment_entry = ttk.Entry(self.add_window)
        self.treatment_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(self.add_window, text="Next").grid(row=5, column=0, padx=10, pady=5)
        self.next_entry = ttk.Entry(self.add_window)
        self.next_entry.grid(row=5, column=1, padx=10, pady=5)

        ttk.Button(self.add_window, text="Save", command=self.save_patient).grid(row=6, column=0, columnspan=2, pady=10)

        # Add Export PDF button
        ttk.Button(self.add_window, text="Export PDF", command=self.export_pdf).grid(row=7, column=0, columnspan=2, pady=10)

        # If patient_id is provided, pre-fill the form
        if patient_id:
            conn = sqlite3.connect('patients.db')
            c = conn.cursor()
            c.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
            patient_data = c.fetchone()
            conn.close()

            self.name_entry.insert(0, patient_data[1])
            self.date_entry.insert(0, patient_data[2])
            self.complaint_entry.insert(0, patient_data[3])
            self.diagnosis_entry.insert(0, patient_data[4])
            self.treatment_entry.insert(0, patient_data[5])
            self.next_entry.insert(0, patient_data[6])

    def save_patient(self):
        name = self.name_entry.get()
        date = self.date_entry.get()
        complaint = self.complaint_entry.get()
        diagnosis = self.diagnosis_entry.get()
        treatment = self.treatment_entry.get()
        next_ = self.next_entry.get()

        if name and date:
            conn = sqlite3.connect('patients.db')
            c = conn.cursor()
            if self.patient_id:  # Update existing record
                c.execute("UPDATE patients SET name=?, date=?, complaint=?, diagnosis=?, treatment=?, next=? WHERE id=?",
                          (name, date, complaint, diagnosis, treatment, next_, self.patient_id))
            else:  # Insert new record
                c.execute("INSERT INTO patients (name, date, complaint, diagnosis, treatment, next) VALUES (?, ?, ?, ?, ?, ?)",
                          (name, date, complaint, diagnosis, treatment, next_))
            conn.commit()
            conn.close()
            self.update_table()
            self.add_window.destroy()
        else:
            messagebox.showwarning("Input Error", "Name and Date are required!")

    def on_patient_select(self, event):
        selected_item = self.tree.selection()[0]
        name = self.tree.item(selected_item, "values")[0]

        conn = sqlite3.connect('patients.db')
        c = conn.cursor()
        c.execute("SELECT id FROM patients WHERE name=?", (name,))
        patient_id = c.fetchone()[0]
        conn.close()

        self.open_add_form(patient_id)  # Open form with patient ID for updating

    def delete_patient(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a patient to delete.")
            return

        name = self.tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}?")
        if confirm:
            conn = sqlite3.connect('patients.db')
            c = conn.cursor()
            c.execute("DELETE FROM patients WHERE name=?", (name,))
            conn.commit()
            conn.close()
            self.update_table()

    def export_pdf(self):
        # Get data from the form
        name = self.name_entry.get()
        date = self.date_entry.get()
        complaint = self.complaint_entry.get()
        diagnosis = self.diagnosis_entry.get()
        treatment = self.treatment_entry.get()
        next_ = self.next_entry.get()

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add headings and data
        pdf.cell(200, 10, txt="Patient Details", ln=True, align="C")
        pdf.cell(200, 10, txt="----------------", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
        pdf.cell(200, 10, txt=f"Date: {date}", ln=True)
        pdf.cell(200, 10, txt=f"Complaint: {complaint}", ln=True)
        pdf.cell(200, 10, txt=f"Diagnosis: {diagnosis}", ln=True)
        pdf.cell(200, 10, txt=f"Treatment: {treatment}", ln=True)
        pdf.cell(200, 10, txt=f"Next: {next_}", ln=True)

        # Save the PDF
        pdf_file = f"patient_{name.replace(' ', '_')}.pdf"
        pdf.output(pdf_file)

        # Notify the user
        messagebox.showinfo("Export Successful", f"Patient details exported to {pdf_file}")

    def create_folder(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a patient to create a folder.")
            return

        # Get patient name and date
        name = self.tree.item(selected_item, "values")[0]
        date = self.tree.item(selected_item, "values")[1]

        # Format folder name (e.g., Ahmad_23032025)
        folder_name = f"{name.replace(' ', '_')}_{date.replace('/', '')}"
        folder_path = os.path.join("/Users/drahmed/Coding/24March", folder_name)

        # Create the folder
        try:
            os.makedirs(folder_path, exist_ok=True)
            messagebox.showinfo("Folder Created", f"Folder created at:\n{folder_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create folder: {e}")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = PatientApp(root)
    root.mainloop()