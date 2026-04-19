import customtkinter as ctk
import numpy as np
from tkinter import messagebox

ctk.set_appearance_mode("dark")

class LeontiefApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🌍 Economic Ripple Simulator")
        self.geometry("950x750")
        self.configure(fg_color="#4c7322")  # dark navy background

        # ===== TITLE =====
        title = ctk.CTkLabel(self,
                            text="🌍 Economic Ripple Effect Analyzer",
                            font=("Arial", 24, "bold"),
                            text_color="#b2a52e")
        title.pack(pady=15)

        # ===== INPUT CARD =====
        self.input_card = ctk.CTkFrame(self, fg_color="#F6E9E9", corner_radius=15)
        self.input_card.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(self.input_card, text="Enter Number of Sectors",
                     text_color="#0A0B0B").pack(pady=5)

        self.size_entry = ctk.CTkEntry(self.input_card, width=200)
        self.size_entry.pack(pady=5)

        ctk.CTkButton(self.input_card,
                      text="Generate Fields",
                      fg_color="#3b82f6",
                      hover_color="#2563eb",
                      command=self.generate_fields).pack(pady=10)

        # ===== MATRIX CARD =====
        self.frame = ctk.CTkFrame(self, fg_color="#dce0e6", corner_radius=15)
        self.frame.pack(pady=10, padx=20)

        # ===== BUTTONS =====
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame,
                      text="📊 Calculate Report",
                      fg_color="#22c55e",
                      hover_color="#16a34a",
                      command=self.calculate).grid(row=0, column=0, padx=10)

        ctk.CTkButton(btn_frame,
                      text="🧪 Load Sample",
                      fg_color="#f59e0b",
                      hover_color="#d97706",
                      command=self.load_sample).grid(row=0, column=1, padx=10)

        # ===== OUTPUT CARD =====
        self.output_card = ctk.CTkFrame(self, fg_color="#020617", corner_radius=15)
        self.output_card.pack(pady=0, padx=0, fill="both", expand=True)

        self.output_box = ctk.CTkTextbox(self.output_card,
                                         width=850,
                                         height=300,
                                         fg_color="#ECEEF6",
                                         text_color="#666d08",
                                         font=("Consolas", 13))
        self.output_box.pack(padx=10, pady=10)

        self.entries_A = []
        self.entries_D = []
        self.names = []

    def generate_fields(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        n = int(self.size_entry.get())

        self.entries_A = []
        self.entries_D = []
        self.names = []

        for i in range(n):
            name = ctk.CTkEntry(self.frame,
                                placeholder_text=f"Sector {i+1}",
                                fg_color="#334155")
            name.grid(row=i, column=0, padx=5, pady=5)
            self.names.append(name)

        for i in range(n):
            row = []
            for j in range(n):
                e = ctk.CTkEntry(self.frame, width=60, fg_color="#475569")
                e.grid(row=i, column=j+1, padx=5, pady=5)
                row.append(e)
            self.entries_A.append(row)

        for i in range(n):
            e = ctk.CTkEntry(self.frame, width=60,
                             placeholder_text="Demand",
                             fg_color="#065f46")
            e.grid(row=i, column=n+2, padx=5, pady=5)
            self.entries_D.append(e)

    def calculate(self):
        try:
            n = len(self.entries_A)

            A = []
            for i in range(n):
                row = [float(self.entries_A[i][j].get()) for j in range(n)]
                A.append(row)

            D = [float(self.entries_D[i].get()) for i in range(n)]
            names = [self.names[i].get() or f"S{i+1}" for i in range(n)]

            A = np.array(A)
            D = np.array(D)

            X = np.linalg.inv(np.eye(n) - A) @ D

            report = "🌍 ECONOMIC REPORT\n"
            report += "="*45 + "\n\n"

            report += "📦 DEMAND:\n"
            for i in range(n):
                report += f"{names[i]}: {D[i]}\n"

            report += "\n📈 OUTPUT:\n"
            for i in range(n):
                report += f"{names[i]}: {round(X[i],2)}\n"

            report += "\n🔥 RIPPLE EFFECT:\n"
            for i in range(n):
                report += f"{names[i]}: +{round(X[i]-D[i],2)}\n"

            self.output_box.delete("1.0", "end")
            self.output_box.insert("end", report)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_sample(self):
        self.size_entry.delete(0, 'end')
        self.size_entry.insert(0, "4")
        self.generate_fields()

        names = ["Agriculture", "Mining", "Food", "Industry"]

        A = [[0.2,0.1,0,0.1],
             [0.1,0.2,0.1,0.2],
             [0.3,0.1,0.2,0.1],
             [0.2,0.2,0.1,0.2]]

        D = [120,100,180,200]

        for i in range(4):
            self.names[i].insert(0, names[i])
            for j in range(4):
                self.entries_A[i][j].insert(0, A[i][j])
            self.entries_D[i].insert(0, D[i])


app = LeontiefApp()
app.mainloop()