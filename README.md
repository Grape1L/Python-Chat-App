# Real-Time Messaging App

A personal real-time messaging application built with **Python and FastAPI**. The project focuses primarily on backend development, including HTTP API design, authentication, persistent data storage and WebSocket-based real-time communication.

The application also includes a small web interface built with **HTML, JavaScript, and basic CSS**. The frontend is intentionally simple and functional; the main goal of the project was to build and understand the backend rather than create a polished frontend UI.

> **Project status:** Ongoing personal project. The codebase is actively being improved and refactored as new backend features and tests are added.

## Features

- User registration and authentication
- JWT-based authentication and authorization
- Password hashing with **bcrypt**
- Persistent application data stored in **SQLite**
- Real-time communication using **WebSockets**
- Separation of HTTP API and real-time communication logic
- Server-side HTML rendering with **Jinja2Templates**
- JSON-based API endpoints
- HttpOnly cookie storage for authenticated requests
- Basic end-to-end encrypted messaging / application data handling
- Basic browser interface for interacting with the application

## Tech Stack

### Backend

- **Python**
- **FastAPI**
- **Uvicorn**
- **SQLite**
- **WebSockets**
- **Pydantic**
- **JWT** authentication
- **bcrypt / Passlib** for password hashing
- **python-jose** for JWT handling

### Frontend

- **HTML**
- **JavaScript**
- **CSS**

The frontend is deliberately lightweight. It is basic and focused on layout and usability rather than advanced visual design, since this project is intended to demonstrate backend/software engineering skills, the UI is not intended to be a showcase of frontend development.

### Testing

- **pytest**

The backend is responsible for authentication, request handling, communication between connected clients, and persistence of application data. WebSockets are used for real-time communication so messages can be delivered without relying on repeated polling requests.

## Authentication

Authentication is implemented using **JWTs**.

The authentication flow is based around:

1. User registration and account creation.
2. Passwords being stored as hashes rather than plaintext passwords.
3. Successful login producing a JWT access token.
4. The JWT is being stored as a cookie.
5. Backend routes validating the token before allowing access to protected functionality.

Password hashing is handled with **bcrypt**, while JWT encoding/decoding is handled with **python-jose**.

## Real-Time Communication

The messaging layer uses **WebSockets** provided by FastAPI.

A connection manager keeps track of active WebSocket connections and handles connection lifecycle events such as connecting, disconnecting, and sending messages to connected clients.

This allows the application to support real-time communication instead of requiring the client to repeatedly ask the server for new messages.

## Database

The project uses **SQLite** for storage.

The database layer stores application data required by the messaging system, while the FastAPI backend provides the interface used by the rest of the application.

Sensitive data is handled with the project's authentication and encryption mechanisms rather than storing user passwords in plaintext.

SQLite was chosen because it keeps the project lightweight and easy to run locally while still providing a real relational database for practicing SQL-backed application development.

## Running Locally

### Requirements

- Python 3.10+
- pip

### Installation

Clone the repository and install the Python dependencies:

```bash
git clone <repository-url>
cd <repository-directory>
pip install -r requirements.txt
```

### Start the application

Run the FastAPI application with Uvicorn using the project's entry point:

```bash
python -m uvicorn backend.main:app --reload
```

> Replace `<module>:<app>` with the actual FastAPI application entry point used by the repository.

The project is designed to be run locally during development. Database and configuration details may change as the application continues to evolve.

## Frontend Note

The application includes a functional browser UI so the backend can be used and demonstrated without a separate API client. The HTML, JavaScript, and CSS were written as part of the project, but the frontend is intentionally simple.

The CSS in particular is **basic, custom CSS** intended to make the application usable and presentable rather than demonstrate advanced frontend engineering. The project's main emphasis is on the **Python backend, API design, authentication, database work and WebSockets**.

## Current Limitations

This is a personal project and is not presented as production-ready software. Some areas are still being improved, including:

- Expanding test coverage
- Refactoring and improving code organization
- Improving error handling and validation across the application
- Further hardening authentication and configuration for production deployment
- Improving the frontend presentation where useful
- Making the key not be created every time a user reloads the page, so that the earlier messages can be read too

These limitations are part of the project's ongoing development and provide areas for further development.
