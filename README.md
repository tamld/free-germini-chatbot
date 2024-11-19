# Google Gemini AI - Chat App

This is a Python application that utilizes Google Gemini AI's capabilities to provide an interactive chatbot experience. The app has a graphical user interface (GUI) built with `Tkinter`, and it uses Google Gemini models to generate responses based on user input.

## Features

- **Chat Interface**: A simple and user-friendly chat interface that allows users to interact with the chatbot.
- **Model Selection**: Users can select between two models provided by Google Gemini AI: `gemini-1.5-flash` (free) and `gemini-exp-1114` (latest).
- **End Scroll Button**: A "Go to End" button allows the user to quickly scroll to the latest messages in the chat.
- **API Key Management**: Securely manage Google Gemini AI API keys using local encryption.
- **Supports Code Formatting**: The chatbot supports rendering responses with syntax-highlighted code blocks.

## Prerequisites

To run the chatbot, you'll need:
- [Germini API token](https://aistudio.google.com/)
- Python 3.8 or newer installed on your system.
- Google Gemini AI API Key. Make sure you have a valid API key to use with the application.

## Installation Guide

### 1. Install Python

If you do not have Python installed, you can download and install the latest version of Python 3 from [Python.org](https://www.python.org/downloads/). Make sure to add Python to your system PATH during the installation.

### 2. Clone or Create Python File

Create a directory for your project and create a Python file, for example, `chatbot.py`. You can use the code from the provided script to set up the chatbot.

### 3. Set Up Virtual Environment (Optional but Recommended)

Create a virtual environment to keep the dependencies organized:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 4. Install Required Dependencies

Create a ```requirements.txt``` file with the following content:

```bash
tkinterweb
cryptography
markdown
google-generativeai
pygments
```

Install the dependencies by running:

```bash
pip install -r requirements.txt
```

### 5. Set Environment Variables
The application requires a master key for encryption purposes, which is set through an environment variable. Set this variable by running the following command:

```bash
export MASTER_KEY=<YOUR-SECRET-KEYS>
```
or on Windows

```bash
set MASTER_KEY=<YOUR-SECRET-KEYS>
```

### 6. Running the Application

After setting up the environment, run the chatbot using the following command:

```bash
python chatbot.py
or 
python3 chatbot.py
```

### 7. Packaging as an Executable File

To package the Python application into an executable file (.exe), you can use PyInstaller. Follow these steps:

Install PyInstaller:
```bash
pip install pyinstaller
```

Create the Executable:
Run the following command to create an executable version of your script:

```bash
pyinstaller --onefile chatbot.py
```
  - The --onefile option ensures that all dependencies are packed into a single .exe file.

  - After running this command, a dist directory will be created containing the chatbot.exe file.
  
Running the Executable:
Navigate to the dist directory and run the generated chatbot.exe file
*Note: On the first run, some antivirus software may flag the executable. You may need to mark it as safe. *