import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu, StringVar, OptionMenu, simpledialog
import threading
from cryptography.fernet import Fernet, InvalidToken
import base64
import os
from tkinterweb import HtmlFrame
import markdown2
import google.generativeai as genai

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Gemini AI - Chat App")
        self.root.geometry("800x700")
        self.api_key = None
        self.conversation_thread = None
        self.stop_event = threading.Event()
        self.chat_content = ""
        self.current_conversation = None
        self.model = None
        self.selected_model = "gemini-exp-1121"
        self.create_menu()
        self.chat_history = HtmlFrame(self.root, horizontal_scrollbar="auto", messages_enabled=False)
        self.chat_history.pack(pady=10, fill=tk.BOTH, expand=True)
        self.create_message_frame()
        self.loading_label = tk.Label(self.root, text="", fg="grey", font="italic")
        self.loading_label.pack(pady=5)
        self.load_api_key()  # Load API key at startup, if available
        if not self.api_key:
            self.show_api_key_window()

    def create_menu(self):
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Chat", command=self.new_chat)
        file_menu.add_command(label="Delete Chat", command=self.clear_chat_history)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        settings_menu = Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="API Key", command=self.show_api_key_window)
        settings_menu.add_command(label="Select Model", command=self.show_model_selection_window)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

    def create_message_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10, fill=tk.X, side=tk.BOTTOM)
        self.message_entry = tk.Text(frame, height=3, width=40)
        self.message_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.message_entry.bind("<Return>", self.send_message_enter)
        self.message_entry.bind("<Shift-Return>", self.insert_new_line)
        button_frame = tk.Frame(frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        go_to_end_button = tk.Button(button_frame, text="Go to End", command=lambda: self.chat_history.yview_moveto(1.0), height=2, width=12)
        go_to_end_button.pack(side=tk.BOTTOM, pady=5, padx=5)

    def show_api_key_window(self):
        api_key_window = tk.Toplevel(self.root)
        api_key_window.title("API Key Settings")
        api_key_window.geometry("400x200")
        frame = tk.Frame(api_key_window)
        frame.pack(pady=10)
        tk.Label(frame, text="API Key:").pack(side=tk.LEFT)
        self.api_key_entry = tk.Entry(frame, show="*", width=40)
        self.api_key_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(api_key_window, text="Master Password:").pack(pady=5)
        self.password_entry = tk.Entry(api_key_window, show="*", width=40)
        self.password_entry.pack(pady=5)
        tk.Button(api_key_window, text="Verify", command=lambda: self.verify_api_key(api_key_window)).pack(pady=5)

    def show_model_selection_window(self):
        model_window = tk.Toplevel(self.root)
        model_window.title("Select Model")
        model_window.geometry("400x150")
        frame = tk.Frame(model_window)
        frame.pack(pady=10)
        tk.Label(frame, text="Select Model:").pack(side=tk.LEFT)
        model_options = ["gemini-1.5-flash", "gemini-exp-1114", "gemini-exp-1121"]
        tk.OptionMenu(frame, StringVar(value=self.selected_model), *model_options, command=self.update_model).pack(side=tk.LEFT, padx=5)
        tk.Label(model_window, text="All models used are from the free version of Gemini.").pack(pady=5)
        tk.Button(model_window, text="Confirm", command=model_window.destroy).pack(pady=5)

    def update_model(self, selected):
        self.selected_model = selected

    def verify_api_key(self, window):
        self.api_key = self.api_key_entry.get().strip()
        master_password = self.password_entry.get().strip()
        if not self.api_key or not master_password:
            messagebox.showerror("Error", "API Key and Master Password cannot be empty!")
            return
        try:
            # Verify API key with Google before saving it
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.selected_model)
            messagebox.showinfo("Success", "API Key is valid!")
            self.save_api_key(master_password)
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid API Key: {str(e)}")
            self.api_key = None

    def save_api_key(self, master_password):
        # Ensure the master key is exactly 32 bytes
        master_key = base64.urlsafe_b64encode(master_password.encode().ljust(32)[:32])
        cipher_suite = Fernet(master_key)
        encrypted_api_key = cipher_suite.encrypt(self.api_key.encode())
        with open("api_key.enc", "wb") as enc_file:
            enc_file.write(encrypted_api_key)

    def load_api_key(self):
        if os.path.exists("api_key.enc"):
            master_password = simpledialog.askstring("Master Password", "Enter Master Password:", show="*")
            if not master_password:
                messagebox.showerror("Error", "Master Password is required to load API Key.")
                return
            try:
                # Ensure the master key is exactly 32 bytes
                master_key = base64.urlsafe_b64encode(master_password.encode().ljust(32)[:32])
                cipher_suite = Fernet(master_key)
                with open("api_key.enc", "rb") as enc_file:
                    encrypted_api_key = enc_file.read()
                # Decrypt the API key to verify it with Google
                self.api_key = cipher_suite.decrypt(encrypted_api_key).decode()
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.selected_model)
                messagebox.showinfo("Success", "API Key loaded successfully!")
            except InvalidToken:
                messagebox.showerror("Error", "Invalid Master Password. Please try again.")
                self.api_key = None
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load API Key: {str(e)}")
                self.api_key = None

    def send_message_enter(self, event):
        self.send_message()
        return "break"

    def insert_new_line(self, event):
        self.message_entry.insert(tk.INSERT, "\n")
        return "break"

    def send_message(self):
        if not self.api_key or not self.model:
            messagebox.showerror("Error", "Please verify your API Key first!")
            return
        user_message = self.message_entry.get("1.0", tk.END).strip()
        if not user_message:
            messagebox.showerror("Error", "Message cannot be empty!")
            return
        self.message_entry.delete("1.0", tk.END)
        self.chat_content += f"<p>You: {user_message}</p>"
        self.chat_history.load_html(self.chat_content)
        self.scroll_to_end()
        self.loading_label.config(text="AI is thinking...")
        self.stop_event.clear()
        self.conversation_thread = threading.Thread(target=self.get_ai_response, args=(user_message,))
        self.conversation_thread.start()

    def get_ai_response(self, user_message):
        try:
            if self.current_conversation is None:
                self.current_conversation = self.model.start_chat()
            response = self.current_conversation.send_message(user_message)
            ai_response = response.text.strip()
            html_response = markdown2.markdown(ai_response, extras=["fenced-code-blocks", "code-friendly"])
            self.chat_content += f"<p>AI: {html_response}</p>"
            self.chat_history.load_html(self.chat_content)
            self.loading_label.config(text="")
            self.scroll_to_end()
        except Exception as e:
            error_message = f"Error: {str(e)}"
            self.chat_content += f"<p>{error_message}</p>"
            self.chat_history.load_html(self.chat_content)
            self.loading_label.config(text="")
            self.scroll_to_end()

    def scroll_to_end(self):
        self.chat_history.yview_moveto(1.0)

    def clear_chat_history(self):
        self.chat_content = ""
        self.chat_history.load_html("")
        self.current_conversation = None

    def new_chat(self):
        self.clear_chat_history()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
