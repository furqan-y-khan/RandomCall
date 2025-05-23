# Cross-Gender Random Calling App

This is a simple web application that randomly connects users of different specified genders (male/female) for a one-on-one chat session. It uses Flask and Flask-SocketIO.

## Features

*   User registration with a username and gender.
*   Automatic pairing of male and female users.
*   Real-time notifications for matched calls and partner disconnections.

## Setup and Running

1.  **Clone the repository:**
    ```bash
    git clone https://your-repository-url/cross-gender-calling-app.git
    cd cross-gender-calling-app
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python app.py
    ```
    The application will typically be available at `http://127.0.0.1:5000`.

    For a more production-like setup using Gunicorn and Eventlet (as hinted in `requirements.txt`):
    ```bash
    gunicorn --worker-class eventlet -w 1 app:app
    ```
    This might require adjustments based on your specific environment and port needs. The `app:app` refers to the `app.py` file and the Flask `app` object within it.

## How it Works

Users join by providing a username and selecting their gender. The backend server maintains separate queues for male and female users. When a user from each queue is available, they are paired, and a unique chat room is created for them. Socket.IO is used for real-time communication between the clients and the server.
