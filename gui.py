import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import database
from face_recognition_module import FaceRecognizer
from emotion_detection import EmotionDetector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import time
from datetime import datetime

class MainGUI:
    def __init__(self, current_user):
        self.current_user = current_user
        self.face_recognizer = FaceRecognizer()
        self.emotion_detector = EmotionDetector()
        self.app = tk.Tk()
        self.setup_main_window()
        
    def setup_main_window(self):
        """Setup the main application window"""
        self.app.title("NCA Facial Recognition Software")
        self.app.state("zoomed")
        self.app.minsize(width=800, height=580)
        self.app["background"] = "#CED0CE"
        
        tk.Label(self.app, text=f"Welcome, {self.current_user[1]} (Rank: {self.current_user[6]})", 
                font=("Arial", 16)).place(x=20, y=20)
        
        buttons = [
            ("Start Detection", self.start_detection_tab),
            ("Add Criminal", self.add_criminal_tab),
            ("Remove Criminal", self.remove_criminal_tab),
            ("Criminal Logs", self.criminal_logs_tab),
            ("Emotion Graphs", self.emotion_graphs_tab)
        ]
        
        for i, (text, command) in enumerate(buttons, start=1):
            y_pos = 0.1 + i * 0.15
            tk.Button(self.app, text=text, height=2, width=40, command=command
                     ).place(relx=0.5, rely=y_pos, anchor=tk.CENTER)
    
    def start_detection_tab(self):
        """Start facial recognition and emotion detection"""
        user_id_window = tk.Toplevel(self.app)
        user_id_window.title("Enter Criminal ID")
        user_id_window.geometry("300x150")
        
        tk.Label(user_id_window, text="Criminal ID:").place(x=50, y=20)
        user_id_entry = tk.Entry(user_id_window)
        user_id_entry.place(x=150, y=20)
        
        def submit_user_id():
            criminal_id = user_id_entry.get()
            if not criminal_id:
                messagebox.showerror("Error", "Criminal ID is required!")
                return
            user_id_window.destroy()
            self.run_facial_recognition(criminal_id)
        
        tk.Button(user_id_window, text="Start Detection", command=submit_user_id).place(x=100, y=60)
    
    def run_facial_recognition(self, criminal_id):
        """Run the facial recognition and emotion detection process"""
        sdt = tk.Toplevel(self.app)
        sdt.title("Start Detection")
        sdt.geometry("800x580")
        
        tk.Label(sdt, text="Webcam Facial Recognition", font=("Arial", 16)).place(x=250, y=10)
        video_label = tk.Label(sdt)
        video_label.place(x=80, y=50)
        emotion_text = tk.Label(sdt, text="Emotion: ", font=("Arial", 16))
        emotion_text.place(x=80, y=540)
        
        cap = cv2.VideoCapture(0)
        start_time = time.time()
        
        def update_webcam():
            ret, frame = cap.read()
            if ret:
                emotion, face_coords = self.emotion_detector.detect_emotion(frame)
                if emotion and face_coords:
                    x, y, w, h = face_coords
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    emotion_text.config(text=f"Emotion: {emotion}")
                    database.log_emotion(criminal_id, emotion)
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img = img.resize((640, 480))
                imgtk = ImageTk.PhotoImage(image=img)
                video_label.imgtk = imgtk
                video_label.config(image=imgtk)
            
            elapsed_time = time.time() - start_time
            if elapsed_time < 60:
                video_label.after(30, update_webcam)
            else:
                close_webcam()
        
        def close_webcam():
            cap.release()
            sdt.destroy()
            messagebox.showinfo("Complete", "1 minute of emotion data collected!")
        
        update_webcam()
        exit_button = tk.Button(sdt, text="Close", command=close_webcam)
        exit_button.place(x=350, y=550)
    
    def add_criminal_tab(self):
        """Add a new criminal to the database"""
        add_criminal_window = tk.Toplevel(self.app)
        add_criminal_window.title("Add Criminal")
        add_criminal_window.geometry("400x400")
        
        fields = [
            ("Name:", 20),
            ("Age:", 60),
            ("Crime:", 100),
            ("Criminal ID:", 140)
        ]
        
        entries = {}
        for label_text, y_pos in fields:
            tk.Label(add_criminal_window, text=label_text).place(x=50, y=y_pos)
            entry = tk.Entry(add_criminal_window)
            entry.place(x=150, y=y_pos)
            entries[label_text] = entry
        
        def submit_criminal():
            name = entries["Name:"].get()
            age = entries["Age:"].get()
            crime = entries["Crime:"].get()
            criminal_id = entries["Criminal ID:"].get()
            
            if not all([name, age, crime, criminal_id]):
                messagebox.showerror("Error", "All fields must be filled!")
                return
                
            if database.add_criminal(name, age, crime, criminal_id):
                messagebox.showinfo("Success", "Criminal Added Successfully!")
                add_criminal_window.destroy()
            else:
                messagebox.showerror("Error", "Criminal ID already exists!")
        
        tk.Button(add_criminal_window, text="Submit", command=submit_criminal).place(x=150, y=180)
    
    def remove_criminal_tab(self):
        """Remove a criminal from the database"""
        remove_criminal_window = tk.Toplevel(self.app)
        remove_criminal_window.title("Remove Criminal")
        remove_criminal_window.geometry("400x200")
        
        tk.Label(remove_criminal_window, text="Criminal ID:").place(x=50, y=20)
        criminal_id_entry = tk.Entry(remove_criminal_window)
        criminal_id_entry.place(x=150, y=20)
        
        def remove_criminal():
            criminal_id = criminal_id_entry.get()
            if not criminal_id:
                messagebox.showerror("Error", "Criminal ID is required!")
                return
                
            if database.remove_criminal(criminal_id):
                messagebox.showinfo("Success", "Criminal Removed Successfully!")
                remove_criminal_window.destroy()
            else:
                messagebox.showerror("Error", "Criminal ID not found!")
        
        tk.Button(remove_criminal_window, text="Remove", command=remove_criminal).place(x=150, y=60)
    
    def criminal_logs_tab(self):
        """Display criminal logs in a table"""
        logs_window = tk.Toplevel(self.app)
        logs_window.title("Criminal Logs")
        logs_window.geometry("600x400")
        
        tk.Label(logs_window, text="Search Criminal ID:").place(x=20, y=20)
        search_entry = tk.Entry(logs_window)
        search_entry.place(x=150, y=20)
        
        def search_criminal():
            criminal_id = search_entry.get()
            update_criminal_list(criminal_id)
        
        def update_criminal_list(search_id=None):
            for row in tree.get_children():
                tree.delete(row)
            criminals = database.get_all_criminals() if not search_id else [c for c in database.get_all_criminals() if c[4] == search_id]
            for criminal in criminals:
                tree.insert("", "end", values=(criminal[4], criminal[1], criminal[2], criminal[3]))
        
        def on_criminal_select(event):
            selected_item = tree.selection()[0]
            criminal_id = tree.item(selected_item, 'values')[0]
            criminal = database.get_criminal_by_id(criminal_id)
            if criminal:
                detail_window = tk.Toplevel(logs_window)
                detail_window.title("Criminal Details")
                detail_window.geometry("300x200")
                
                details = [
                    f"Name: {criminal[1]}",
                    f"Age: {criminal[2]}",
                    f"Crime: {criminal[3]}",
                    f"ID: {criminal[4]}"
                ]
                
                for i, detail in enumerate(details):
                    tk.Label(detail_window, text=detail).place(x=20, y=20 + i*30)
        
        tk.Button(logs_window, text="Search", command=search_criminal).place(x=300, y=20)
        
        columns = ("Criminal ID", "Name", "Age", "Crime")
        tree = ttk.Treeview(logs_window, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
        tree.place(x=20, y=60, width=550, height=300)
        tree.bind("<Double-1>", on_criminal_select)
        
        update_criminal_list()
    
    def emotion_graphs_tab(self):
        """Display emotion graphs for selected criminals"""
        graphs_window = tk.Toplevel(self.app)
        graphs_window.title("Emotion Analysis")
        graphs_window.geometry("800x600")
        
        tk.Label(graphs_window, text="Select Criminal:").place(x=20, y=20)
        
        # Criminal selection frame
        selection_frame = tk.Frame(graphs_window)
        selection_frame.place(x=20, y=50, width=750, height=200)
        
        # Treeview for criminal list
        columns = ("Criminal ID", "Name", "Age", "Crime")
        self.criminal_tree = ttk.Treeview(selection_frame, columns=columns, show='headings')
        for col in columns:
            self.criminal_tree.heading(col, text=col)
        self.criminal_tree.pack(fill=tk.BOTH, expand=True)
        
        # Graph display frame
        graph_frame = tk.Frame(graphs_window)
        graph_frame.place(x=20, y=260, width=750, height=300)
        
        # Conclusion label
        conclusion_label = tk.Label(graphs_window, text="Conclusion: ", font=("Arial", 12))
        conclusion_label.place(x=20, y=570)
        
        def load_criminals():
            """Load all criminals into the treeview"""
            for row in self.criminal_tree.get_children():
                self.criminal_tree.delete(row)
            criminals = database.get_all_criminals()
            for criminal in criminals:
                self.criminal_tree.insert("", "end", values=(criminal[4], criminal[1], criminal[2], criminal[3]))
        
        def on_criminal_select(event):
            """Handle criminal selection and display their emotion graph"""
            selected_item = self.criminal_tree.selection()
            if not selected_item:
                return
                
            criminal_id = self.criminal_tree.item(selected_item[0], 'values')[0]
            criminal = database.get_criminal_by_id(criminal_id)
            if not criminal:
                return
                
            # Get emotion logs
            logs = database.get_emotion_logs(criminal_id)

            # Clear previous graph and conclusion
            for widget in graph_frame.winfo_children():
                widget.destroy()
            conclusion_label.config(text="Conclusion: ")

            if not logs:
                tk.Label(graph_frame, text="No emotion data available for this criminal").pack()
                return

            # Prepare data for plotting
            timestamps = [log[0] for log in logs]
            emotions = [log[1] for log in logs]

            try:
                # Convert timestamps to relative time in seconds
                first_time = datetime.strptime(timestamps[0], '%Y-%m-%d %H:%M:%S')
                time_deltas = [(datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') - first_time).total_seconds() 
                              for ts in timestamps]
                
                # Create the plot with larger figure size
                fig, ax = plt.subplots(figsize=(12, 6))
                
                # Emotion color mapping and numerical values for plotting
                emotion_values = {
                    'Angry': 4,
                    'Disgust': 3,
                    'Fear': 2,
                    'Happy': 1,
                    'Sad': 4,
                    'Surprise': 2,
                    'Neutral': 0
                }
                
                # Convert emotions to numerical values
                y_values = [emotion_values[e] for e in emotions]
                
                # Create a line plot that shows emotional transitions
                ax.plot(time_deltas, y_values, 
                       color='blue', 
                       linewidth=2, 
                       marker='o',
                       markersize=8,
                       markerfacecolor='red',
                       markeredgewidth=2)
                
                # Add emotion labels at each point
                for i, (x, y, emotion) in enumerate(zip(time_deltas, y_values, emotions)):
                    ax.text(x, y+0.1, emotion, ha='center', va='bottom', fontsize=10)
                
                # Customize the plot
                ax.set_xlabel("Time (seconds)", fontsize=12)
                ax.set_ylabel("Emotion Intensity", fontsize=12)
                ax.set_title(f"Emotional Variation for {criminal[1]}", fontsize=14, pad=20)
                
                # Set y-axis to show emotion names
                ax.set_yticks(list(emotion_values.values()))
                ax.set_yticklabels(list(emotion_values.keys()))
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # Calculate conclusion
                negative_emotions = ['Angry', 'Disgust', 'Fear', 'Sad']
                negative_count = sum(1 for e in emotions if e in negative_emotions)
                total = len(emotions)
                conclusion = "Confirmed suspect" if (negative_count/total) > 0.5 else "Innocent civilian"
                conclusion_label.config(text=f"Conclusion: {conclusion} (Negative: {negative_count}/{total})")
                
                # Embed the plot
                canvas = FigureCanvasTkAgg(fig, master=graph_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
            except Exception as e:
                tk.Label(graph_frame, text=f"Error generating graph: {str(e)}").pack()
        
        # Bind selection event
        self.criminal_tree.bind("<<TreeviewSelect>>", on_criminal_select)
        
        # Load initial data
        load_criminals()
    
    def run(self):
        """Run the main application"""
        self.app.mainloop()