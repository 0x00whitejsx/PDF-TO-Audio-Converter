import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfFileReader
from gtts import gTTS
import os
import pandas as pd
import time
from playsound import playsound
import threading

# Function to read PDF file and extract text
def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as pdf_file:
        reader = PdfFileReader(pdf_file)
        text = ""
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extract_text()
    return text

# Function to convert text to audio
def convert_text_to_audio(text, audio_file_path):
    tts = gTTS(text)
    tts.save(audio_file_path)

# Function to save conversion details to CSV database
def save_to_database(pdf_file, audio_file):
    database_file = "conversions.csv"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    if os.path.exists(database_file):
        df = pd.read_csv(database_file)
    else:
        df = pd.DataFrame(columns=["Timestamp", "PDF File", "Audio File"])
    
    df = df.append({"Timestamp": timestamp, "PDF File": pdf_file, "Audio File": audio_file}, ignore_index=True)
    df.to_csv(database_file, index=False)

# Function to handle file opening and conversion process
def open_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        loading_label.pack()
        root.update()
        try:
            text = extract_text_from_pdf(file_path)
            if not text.strip():
                messagebox.showerror("Error", "No text found in PDF.")
                loading_label.pack_forget()
                return
            audio_file = os.path.splitext(file_path)[0] + ".mp3"
            convert_text_to_audio(text, audio_file)
            save_to_database(file_path, audio_file)
            messagebox.showinfo("Success", f"Audio file saved as {audio_file}")
            play_button.config(state="normal")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            loading_label.pack_forget()

# Function to play audio file
def play_audio():
    file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3")])
    if file_path:
        threading.Thread(target=playsound, args=(file_path,), daemon=True).start()

# Function to view conversion history
def view_history():
    database_file = "conversions.csv"
    if os.path.exists(database_file):
        df = pd.read_csv(database_file)
        history_window = tk.Toplevel(root)
        history_window.title("Conversion History")
        
        text = tk.Text(history_window)
        text.pack(expand=True, fill="both")
        
        for index, row in df.iterrows():
            text.insert(tk.END, f"Timestamp: {row['Timestamp']}\nPDF File: {row['PDF File']}\nAudio File: {row['Audio File']}\n\n")
    else:
        messagebox.showinfo("Info", "No conversion history found.")

# Initialize Tkinter window
root = tk.Tk()
root.title("PDF to Audio Converter")
root.geometry("400x400")
root.configure(bg="#f0f0f0")

# Create and place widgets
tk.Button(root, text="Open PDF", command=open_pdf, bg="#4CAF50", fg="white").pack(pady=20)
tk.Button(root, text="View Conversion History", command=view_history, bg="#2196F3", fg="white").pack(pady=20)
play_button = tk.Button(root, text="Play Audio", command=play_audio, state="disabled", bg="#FF9800", fg="white")
play_button.pack(pady=20)

# Loading label
loading_label = tk.Label(root, text="Processing...", bg="#f0f0f0", fg="#FF0000")

root.mainloop()
