from tkinter import *
from tkinter import filedialog, simpledialog, messagebox
import os
from PIL import Image, ImageTk
from stegano import lsb
import hashlib
import base64
from cryptography.fernet import Fernet

# ==============================
# 🔧 MAIN WINDOW CONFIG
# ==============================

root = Tk()
root.title("Secure Steganography System with VAPT")
root.geometry("1050x650+100+80")
root.resizable(False, False)
root.configure(bg="#2f4155")

filename = None
secret = None

# ==============================
# 🔐 SECURITY FUNCTIONS
# ==============================

def generate_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)

def compute_sha256_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

# ==============================
# 📂 IMAGE HANDLING
# ==============================

def showimage():
    global filename
    filename = filedialog.askopenfilename(
        initialdir=os.getcwd(),
        title='Select Image File',
        filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg")]
    )

    if filename:
        img = Image.open(filename)
        img = img.resize((350, 300))
        img = ImageTk.PhotoImage(img)
        lbl.configure(image=img)
        lbl.image = img

# ==============================
# 🔐 HIDE DATA (ENCRYPT + LSB)
# ==============================

def hide_data():
    global secret

    if not filename:
        messagebox.showerror("Error", "Load an image first!")
        return

    message = text1.get(1.0, END).strip()

    if not message:
        messagebox.showerror("Error", "Enter a message!")
        return

    password = simpledialog.askstring("Password", "Enter Password:", show="*")

    if not password:
        messagebox.showerror("Error", "Password required!")
        return

    try:
        key = generate_key(password)
        cipher = Fernet(key)
        encrypted_message = cipher.encrypt(message.encode()).decode()

        secret = lsb.hide(filename, encrypted_message)
        messagebox.showinfo("Success", "Message Encrypted & Hidden Successfully!")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ==============================
# 🔓 SHOW DATA (DECRYPT)
# ==============================

def show_data():
    if not filename:
        messagebox.showerror("Error", "Load an image first!")
        return

    encrypted_message = lsb.reveal(filename)

    if not encrypted_message:
        text1.delete(1.0, END)
        text1.insert(END, "No hidden data found.")
        return

    password = simpledialog.askstring("Password", "Enter Password:", show="*")

    try:
        key = generate_key(password)
        cipher = Fernet(key)
        decrypted_message = cipher.decrypt(encrypted_message.encode()).decode()

        text1.delete(1.0, END)
        text1.insert(END, decrypted_message)

    except:
        text1.delete(1.0, END)
        text1.insert(END, "Wrong Password! Possible attack detected.")

# ==============================
# 💾 SAVE IMAGE + HASH
# ==============================

def save_image():
    global secret

    if not secret:
        messagebox.showerror("Error", "No hidden image to save!")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".png")

    if save_path:
        secret.save(save_path)
        hash_val = compute_sha256_hash(save_path)

        with open("hidden_hash.txt", "w") as f:
            f.write(hash_val)

        messagebox.showinfo("Saved", "Image saved with SHA-256 hash generated!")

# ==============================
# 🔍 STEGANOGRAPHY DETECTION
# ==============================
'''
def detect_stego():
    if not filename:
        messagebox.showerror("Error", "Load an image first!")
        return

    hidden_data = lsb.reveal(filename)

    text1.delete(1.0, END)

    if hidden_data:
        text1.insert(END, "⚠ Steganography Detected in Image!")
    else:
        text1.insert(END, "✔ No hidden data detected.")
'''
def detect_stego():
    if not filename:
        messagebox.showerror("Error", "Load an image first!")
        return

    text1.delete(1.0, END)

    try:
        hidden_data = lsb.reveal(filename)

        if hidden_data:
            text1.insert(END, "⚠ Steganography Detected in Image!")
        else:
            text1.insert(END, "✔ No hidden data detected.")

    except Exception:
        text1.insert(END, "✔ No hidden data detected.")

# ==============================
# 💣 BRUTE FORCE SIMULATION
# ==============================

def simulate_attack():
    if not filename:
        messagebox.showerror("Error", "Load image first!")
        return

    encrypted_message = lsb.reveal(filename)

    if not encrypted_message:
        text1.insert(END, "\nNo hidden message to attack.")
        return

    common_passwords = ["1234", "admin", "password", "test"]

    for pwd in common_passwords:
        try:
            key = generate_key(pwd)
            cipher = Fernet(key)
            cipher.decrypt(encrypted_message.encode())

            text1.insert(END, f"\n⚠ Weak Password Detected: {pwd}")
            return
        except:
            continue

    text1.insert(END, "\n✔ Brute Force Simulation Failed. System Secure.")

# ==============================
# 📊 VIEW HASH
# ==============================

def view_hidden_hash():
    if os.path.exists("hidden_hash.txt"):
        with open("hidden_hash.txt", "r") as f:
            hash_val = f.read()

        text1.delete(1.0, END)
        text1.insert(END, f"SHA-256 Hash:\n{hash_val}")
    else:
        text1.insert(END, "\nNo hash file found.")

# ==============================
# 🎨 GUI LAYOUT (3 SECTIONS)
# ==============================

# ==============================
# 🎨 MODERN CYBER UI DESIGN
# ==============================

root.configure(bg="#0f172a")

title = Label(root,
              text="🔐 SECURE STEGANOGRAPHY DASHBOARD",
              bg="#0f172a",
              fg="#38bdf8",
              font=("Segoe UI", 22, "bold"))
title.pack(pady=20)

# ===== MAIN TOP CONTAINER =====
main_frame = Frame(root, bg="#0f172a")
main_frame.pack(pady=10)

# ================= IMAGE PANEL =================
image_frame = Frame(main_frame,
                    bg="#1e293b",
                    width=420,
                    height=330,
                    highlightbackground="#38bdf8",
                    highlightthickness=2)
image_frame.grid(row=0, column=0, padx=30)
image_frame.pack_propagate(False)

Label(image_frame,
      text="IMAGE PREVIEW",
      bg="#1e293b",
      fg="#94a3b8",
      font=("Segoe UI", 12, "bold")).pack(pady=5)

lbl = Label(image_frame, bg="#1e293b")
lbl.pack(expand=True)

# ================= TEXT PANEL =================
text_frame = Frame(main_frame,
                   bg="#1e293b",
                   width=420,
                   height=330,
                   highlightbackground="#38bdf8",
                   highlightthickness=2)
text_frame.grid(row=0, column=1, padx=30)
text_frame.pack_propagate(False)

Label(text_frame,
      text="MESSAGE / OUTPUT",
      bg="#1e293b",
      fg="#94a3b8",
      font=("Segoe UI", 12, "bold")).pack(pady=5)

text1 = Text(text_frame,
             font=("Consolas", 11),
             bg="#0f172a",
             fg="#38bdf8",
             insertbackground="white",
             relief=FLAT)
text1.pack(fill=BOTH, expand=True, padx=10, pady=5)

# ================= BUTTON PANEL =================
button_frame = Frame(root, bg="#0f172a")
button_frame.pack(pady=25)
button_frame.grid_columnconfigure((0,1,2,3), weight=1)


def style_button(btn):
    btn.configure(
        bg="#2563eb",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief=FLAT,
        width=15,
        height=2,
        activebackground="#1d4ed8",
        activeforeground="white",
        cursor="hand2"
    )

def on_enter(e):
    e.widget['bg'] = "#1d4ed8"

def on_leave(e):
    e.widget['bg'] = "#2563eb"

buttons = [
    ("Open Image", showimage),
    ("Save Image", save_image),
    ("Hide Data", hide_data),
    ("Show Data", show_data),
    ("Detect Stego", detect_stego),
    ("Simulate Attack", simulate_attack),
    ("View Hash", view_hidden_hash)
]

row = 0
col = 0

for text, command in buttons:
    btn = Button(button_frame, text=text, command=command)
    style_button(btn)
    btn.grid(row=row, column=col, padx=10, pady=10)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    col += 1

# ================= STATUS BAR =================
status_bar = Label(root,
                   text="System Ready | Secure Mode Enabled",
                   bg="#1e293b",
                   fg="#38bdf8",
                   font=("Segoe UI", 10),
                   anchor=W)
status_bar.pack(fill=X, side=BOTTOM)

root.mainloop()
