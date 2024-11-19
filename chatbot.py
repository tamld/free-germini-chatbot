import tkinter as tk
from tkinter import scrolledtext, messagebox, Menu, StringVar, OptionMenu
import threading
from cryptography.fernet import Fernet
import base64
import os
from tkinterweb import HtmlFrame
import markdown
import google.generativeai as genai
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

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
        self.selected_model = StringVar()
        self.selected_model.set("gemini-exp-1114")
        self.create_menu()
        self.chat_history = HtmlFrame(self.root, horizontal_scrollbar="auto", messages_enabled=False)
        self.chat_history.pack(pady=10, fill=tk.BOTH, expand=True)
        self.create_message_frame()
        self.load_api_key()
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
        api_key_window.geometry("400x150")
        frame = tk.Frame(api_key_window)
        frame.pack(pady=10)
        tk.Label(frame, text="API Key:").pack(side=tk.LEFT)
        self.api_key_entry = tk.Entry(frame, show="*", width=40)
        self.api_key_entry.pack(side=tk.LEFT, padx=5)
        self.api_key_entry.bind("<Return>", lambda event: self.verify_api_key(api_key_window))
        tk.Button(frame, text="Verify", command=lambda: self.verify_api_key(api_key_window)).pack(side=tk.LEFT)

    def show_model_selection_window(self):
        model_window = tk.Toplevel(self.root)
        model_window.title("Select Model")
        model_window.geometry("400x150")
        frame = tk.Frame(model_window)
        frame.pack(pady=10)
        tk.Label(frame, text="Select Model:").pack(side=tk.LEFT)
        model_options = ["gemini-1.5-flash", "gemini-exp-1114"]
        tk.OptionMenu(frame, self.selected_model, *model_options).pack(side=tk.LEFT, padx=5)
        tk.Label(frame, text="Note: 'gemini-1.5-flash' is free, others may require payment.").pack(pady=5)
        tk.Button(frame, text="Confirm", command=model_window.destroy).pack(pady=5)

    def verify_api_key(self, window):
        self.api_key = self.api_key_entry.get().strip()
        if not self.api_key:
            messagebox.showerror("Error", "API Key cannot be empty!")
            return
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.selected_model.get())
            messagebox.showinfo("Success", "API Key is valid!")
            self.save_api_key()
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid API Key: {str(e)}")
            self.api_key = None

    def save_api_key(self):
        master_key = os.environ.get("MASTER_KEY")
        if not master_key:
            master_key = base64.urlsafe_b64encode(os.urandom(32))
            os.environ["MASTER_KEY"] = master_key.decode()
        cipher_suite = Fernet(master_key)
        encrypted_api_key = cipher_suite.encrypt(self.api_key.encode())
        with open("api_key.enc", "wb") as enc_file:
            enc_file.write(encrypted_api_key)

    def load_api_key(self):
        if os.path.exists("api_key.enc"):
            master_key = os.environ.get("MASTER_KEY")
            if not master_key:
                messagebox.showerror("Error", "MASTER_KEY not found. Unable to load API Key.")
                return
            cipher_suite = Fernet(master_key)
            with open("api_key.enc", "rb") as enc_file:
                encrypted_api_key = enc_file.read()
            try:
                self.api_key = cipher_suite.decrypt(encrypted_api_key).decode()
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.selected_model.get())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load API Key: {str(e)}")

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
        self.chat_history.yview_moveto(1.0)
        self.stop_event.clear()
        self.conversation_thread = threading.Thread(target=self.get_ai_response, args=(user_message,))
        self.conversation_thread.start()

    def get_ai_response(self, user_message):
        try:
            if self.current_conversation is None:
                self.current_conversation = self.model.start_chat()
            response = self.current_conversation.send_message(user_message)
            ai_response = response.text.strip()
            formatted_response = self.format_ai_response(ai_response)
            html_response = markdown.markdown(formatted_response, extensions=['fenced_code', 'codehilite'])
            self.chat_content += f"<p>AI: {html_response}</p>"
            self.chat_history.load_html(self.chat_content)
            self.chat_history.yview_moveto(1.0)
        except Exception as e:
            error_message = f"Error: {str(e)}"
            self.chat_content += f"<p>{error_message}</p>"
            self.chat_history.load_html(self.chat_content)
            self.chat_history.yview_moveto(1.0)

    def format_ai_response(self, response):
        lines = response.split("\n")
        formatted = []
        code_block = False
        current_lexer = None
        for line in lines:
            if line.startswith("```"):
                code_block = not code_block
                if code_block:
                    language = line[3:].strip()
                    try:
                        current_lexer = get_lexer_by_name(language)
                    except Exception:
                        current_lexer = get_lexer_by_name("text")
                    formatted.append("<pre><code>")
                else:
                    formatted.append("</code></pre>")
                continue
            if code_block:
                if current_lexer:
                    formatter = HtmlFormatter()
                    line = highlight(line, current_lexer, formatter)
                formatted.append(line)
            else:
                formatted.append(line)
        return "\n".join(formatted)

    def clear_chat_history(self):
        self.chat_content = ""
        self.chat_history.load_html("")
        self.chat_history.yview_moveto(1.0)
        self.current_conversation = None

    def new_chat(self):
        self.clear_chat_history()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()