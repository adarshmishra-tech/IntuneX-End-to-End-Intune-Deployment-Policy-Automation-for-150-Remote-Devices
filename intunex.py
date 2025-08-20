import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, Toplevel
import random
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import threading
import numpy as np

class IntuneDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Intune Deployment Dashboard")
        self.root.geometry("1280x720")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Configure custom styles
        self.style = tk.ttk.Style()
        self.style.configure("Treeview", background="#2a2a3b", foreground="#ffffff", fieldbackground="#2a2a3b", font=("Segoe UI", 11))
        self.style.configure("Treeview.Heading", background="#0078d4", foreground="#ffffff", font=("Segoe UI", 11, "bold"))
        self.style.map("Treeview", background=[("selected", "#005a9e")])

        # Gradient Background
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.create_gradient()
        self.root.bind("<Configure>", self.resize_gradient)

        # Header Frame
        header_frame = ctk.CTkFrame(self.canvas, fg_color="#1e1e2f", corner_radius=10)
        header_frame.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.1)
        ctk.CTkLabel(
            header_frame,
            text="Intune Deployment & Policy Automation Dashboard",
            font=("Segoe UI", 28, "bold"),
            text_color="#ffffff"
        ).pack(side="left", padx=20)
        self.time_label = ctk.CTkLabel(
            header_frame,
            text=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            font=("Segoe UI", 12),
            text_color="#cccccc"
        )
        self.time_label.pack(side="right", padx=20)
        self.update_time()

        # Main Content
        main_frame = ctk.CTkFrame(self.canvas, fg_color="#1e1e2f", corner_radius=10)
        main_frame.place(relx=0.02, rely=0.14, relwidth=0.96, relheight=0.75)

        # Left: Stats and Analytics
        left_frame = ctk.CTkFrame(main_frame, width=350, fg_color="#252537", corner_radius=10)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkLabel(
            left_frame,
            text="Deployment Analytics",
            font=("Segoe UI", 20, "bold"),
            text_color="#ffffff"
        ).pack(pady=10)

        # Stats with Hover Effect
        stats_data = [
            ("Total Devices", "152"),
            ("Compliance Rate", "94%"),
            ("Autopilot Enrolled", "150"),
            ("Policies Applied", "48")
        ]
        for label, value in stats_data:
            frame = ctk.CTkFrame(left_frame, fg_color="#2a2a3b", corner_radius=8)
            frame.pack(fill="x", pady=8, padx=10)
            frame.bind("<Enter>", lambda e, f=frame: f.configure(fg_color="#0078d4"))
            frame.bind("<Leave>", lambda e, f=frame: f.configure(fg_color="#2a2a3b"))
            ctk.CTkLabel(frame, text=label, font=("Segoe UI", 12)).pack(side="left", padx=10)
            ctk.CTkLabel(frame, text=value, font=("Segoe UI", 12, "bold"), text_color="#ffffff").pack(side="right", padx=10)

        # Animated Compliance Chart
        chart_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        chart_frame.pack(fill="x", pady=20)
        self.fig, self.ax = plt.subplots(figsize=(4, 3), facecolor="#252537")
        self.canvas_chart = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas_chart.get_tk_widget().configure(bg="#252537")
        self.canvas_chart.get_tk_widget().pack()
        self.animate_chart()

        # Right: Device Management
        right_frame = ctk.CTkFrame(main_frame, fg_color="#252537", corner_radius=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(
            right_frame,
            text="Device Management",
            font=("Segoe UI", 20, "bold"),
            text_color="#ffffff"
        ).pack(pady=10)

        # Device Table with Clickable Rows
        columns = ("Device ID", "User", "Compliance", "Last Check-in", "Status")
        self.tree = tk.ttk.Treeview(right_frame, columns=columns, show="headings", style="Treeview")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind("<Double-1>", self.show_device_details)

        # Sample device data
        self.devices = [
            (f"DEV{100+i}", f"User {i+1}", random.choice(["Compliant", "Non-compliant"]),
             f"2025-08-{random.randint(10, 20)} {random.randint(10, 23)}:{random.randint(10, 59)}",
             "Active")
            for i in range(15)
        ]
        for data in self.devices:
            self.tree.insert("", "end", values=data)

        # Action Buttons
        button_frame = ctk.CTkFrame(self.canvas, fg_color="#1e1e2f", corner_radius=10)
        button_frame.place(relx=0.02, rely=0.91, relwidth=0.96, relheight=0.07)
        actions = [
            ("Run Autopilot Sync", self.run_autopilot),
            ("Apply Policies", self.apply_policies),
            ("Check Compliance", self.check_compliance),
            ("Generate Report", self.generate_report)
        ]
        for text, command in actions:
            btn = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                width=220,
                height=45,
                font=("Segoe UI", 12, "bold"),
                fg_color="#0078d4",
                hover_color="#005a9e",
                corner_radius=10
            )
            btn.pack(side="left", padx=10)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(fg_color="#0091ff"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(fg_color="#0078d4"))

        # Progress Bar and Status
        self.progress = ctk.CTkProgressBar(self.canvas, width=600, mode="determinate", progress_color="#0078d4")
        self.progress.place(relx=0.5, rely=0.85, anchor="center")
        self.progress.set(0)
        self.progress.place_forget()
        self.status_label = ctk.CTkLabel(
            self.canvas,
            text="Ready",
            font=("Segoe UI", 14),
            text_color="#cccccc"
        )
        self.status_label.place(relx=0.5, rely=0.85, anchor="center")

    def create_gradient(self):
        self.canvas.delete("gradient")
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        colors = ["#1e1e2f", "#2a2a3b", "#1e1e2f"]
        for i in range(height):
            r = int(np.interp(i, [0, height], [int(colors[0][1:3], 16), int(colors[1][1:3], 16)]))
            g = int(np.interp(i, [0, height], [int(colors[0][3:5], 16), int(colors[1][3:5], 16)]))
            b = int(np.interp(i, [0, height], [int(colors[0][5:7], 16), int(colors[1][5:7], 16)]))
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, width, i, fill=color, tags="gradient")

    def resize_gradient(self, event):
        self.create_gradient()

    def update_time(self):
        self.time_label.configure(text=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.root.after(1000, self.update_time)

    def animate_chart(self):
        def update_chart(frame):
            self.ax.clear()
            labels = ["Compliant", "Non-compliant"]
            sizes = [94 + random.uniform(-0.5, 0.5), 6 + random.uniform(-0.5, 0.5)]
            colors = ["#0078d4", "#d83b01"]
            explode = (0.05, 0)
            self.ax.pie(sizes, labels=labels, colors=colors, autopct="%1.0f%%", startangle=90, explode=explode)
            self.ax.axis("equal")
            self.ax.set_facecolor("#252537")
            self.canvas_chart.draw()

        self.ani = animation.FuncAnimation(self.fig, update_chart, interval=4000, repeat=True)

    def show_device_details(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        device_data = item["values"]

        popup = Toplevel(self.root)
        popup.title("Device Details")
        popup.geometry("400x300")
        popup.configure(bg="#1e1e2f")
        ctk.CTkLabel(
            popup,
            text="Device Details",
            font=("Segoe UI", 16, "bold"),
            text_color="#ffffff"
        ).pack(pady=10)
        details = [
            ("Device ID", device_data[0]),
            ("User", device_data[1]),
            ("Compliance", device_data[2]),
            ("Last Check-in", device_data[3]),
            ("Status", device_data[4]),
            ("OS", random.choice(["Windows 10", "Windows 11"])),
            ("Intune Policy", "Applied")
        ]
        for label, value in details:
            frame = ctk.CTkFrame(popup, fg_color="#252537")
            frame.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(frame, text=label, font=("Segoe UI", 12)).pack(side="left", padx=10)
            ctk.CTkLabel(frame, text=value, font=("Segoe UI", 12, "bold"), text_color="#0078d4").pack(side="right", padx=10)
        ctk.CTkButton(
            popup,
            text="Close",
            command=popup.destroy,
            fg_color="#0078d4",
            hover_color="#005a9e",
            corner_radius=10
        ).pack(pady=20)

    def simulate_progress(self, task_name, callback):
        self.status_label.place_forget()
        self.progress.place(relx=0.5, rely=0.85, anchor="center")
        self.status_label.configure(text=f"Processing {task_name}...")
        self.status_label.place(relx=0.5, rely=0.80, anchor="center")
        self.progress.set(0)

        def update_progress():
            for i in range(1, 101):
                self.progress.set(i / 100)
                self.root.update()
                self.root.after(25)
            self.progress.place_forget()
            self.status_label.configure(text=f"{task_name} completed successfully!")
            self.status_label.place(relx=0.5, rely=0.85, anchor="center")
            callback()

        threading.Thread(target=update_progress, daemon=True).start()

    def run_autopilot(self):
        self.simulate_progress("Autopilot Sync", lambda: messagebox.showinfo(
            "Success", "Zero-touch deployment completed for 152 devices using Autopilot and PowerShell scripts."
        ))

    def apply_policies(self):
        self.simulate_progress("Policy Application", lambda: messagebox.showinfo(
            "Success", "App protection and conditional access policies applied to 152 devices via Intune."
        ))

    def check_compliance(self):
        self.simulate_progress("Compliance Check", lambda: messagebox.showinfo(
            "Success", "Compliance check completed: 94% of 152 devices are compliant with Azure AD policies."
        ))

    def generate_report(self):
        self.simulate_progress("Report Generation", lambda: messagebox.showinfo(
            "Success", "M365 Security Center report generated for 152 devices, detailing compliance and security status."
        ))

if __name__ == "__main__":
    root = ctk.CTk()
    app = IntuneDashboard(root)
    root.mainloop()
