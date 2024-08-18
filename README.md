# GenAI-ChatApp
Python GUI application forr GenAI chat

# GenAI ChatApp

GenAI ChatApp is a Python-based graphical user interface (GUI) application that allows users to interact with an AI model to generate content based on their inputs. The application is built using PyQt6 and integrates with the Google Gemini API for AI-generated responses. The app supports multiple chat tabs, message history, file uploads, and more.

## Features

- **Multiple Chat Tabs:** Users can create multiple chat tabs to manage different conversations.
- **AI-Generated Content:** Interacts with the Google Gemini API to generate AI content based on user input.
- **Message History:** Save and load chat histories for future reference.
- **File Uploads:** Upload text files to the chat input for processing.
- **Copy Functionality:** Right-click on chat messages to copy them to the clipboard.
- **Light Theme:** A clean and modern white and blue layout.
- **Sound Notifications:** Plays a sound when messages are sent.

## Installation

### Prerequisites

- Python 3.8 or later
- `pip` (Python package installer)

### Dependencies

You can install the required dependencies using `pip`:

```bash
pip install PyQt6 simpleaudio requests

git clone https://github.com/Sherin-SEF-AI/GenAI-ChatApp.git
cd GenAI-ChatApp

Usage
Set Up API Key:

You need a valid API key from Google Gemini.

In the application, go to Settings > API Key and enter your API key.

Run the Application:

python chat_app.py

Interacting with the Application:


Type your message in the input box and press Send.

Right-click on any message bubble to copy the text.

Save the chat history using the File > Save Chat option.
