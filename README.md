# Real-Time Messaging App

A personal real-time messaging application built with **Python and FastAPI**. The project focuses primarily on backend development, including HTTP API design, authentication, persistent data storage, WebSocket-based real-time communication, and automated testing.

The application also includes a small web interface built with **HTML, JavaScript, and basic CSS**. The frontend is intentionally simple and functional; the main goal of the project was to build and understand the backend rather than create a polished frontend UI.

> **Project status:** Ongoing personal project. The codebase is actively being improved and refactored as new backend features and tests are added.

## Screenshots



## Features

- User registration and authentication
- JWT-based authentication and authorization
- Password hashing with **bcrypt**
- Persistent application data stored in **SQLite**
- Real-time communication using **WebSockets**
- Separation of HTTP API and real-time communication logic
- Server-side HTML rendering with **Jinja2Templates**
- JSON-based API endpoints
- Client-side token storage for authenticated requests
- Automated backend tests using **pytest**
- End-to-end encrypted messaging / application data handling
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

## Architecture

The application is organized around a backend-first architecture:

```text
Browser / Client
       │
       ├── HTTP requests ───────────────┐
       │                                │
       └── WebSocket connection ────────┤
                                        ▼
                                  FastAPI Backend
                                        │
                       ┌────────────────┼────────────────┐
                       │                │                │
                       ▼                ▼                ▼
                  API / Routes     Auth / Security   WebSocket Manager
                       │                │                │
                       └────────────────┼────────────────┘
                                        ▼
                                   SQLite Database
```

The backend is responsible for authentication, request handling, communication between connected clients, and persistence of application data. WebSockets are used for real-time communication so messages can be delivered without relying on repeated polling requests.

## Authentication

Authentication is implemented using **JWTs**.

The authentication flow is based around:

1. User registration and account creation.
2. Passwords being stored as hashes rather than plaintext passwords.
3. Successful login producing a JWT access token.
4. The client storing the token locally and attaching it to authenticated requests.
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

## Testing

Backend functionality is tested with **pytest**.

The test suite is used to verify application components and backend behaviour, including connection-management logic and other core functionality. Writing tests alongside the application has also helped identify edge cases and regressions while the project is being refactored.

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
uvicorn <module>:<app> --reload
```

> Replace `<module>:<app>` with the actual FastAPI application entry point used by the repository.

The project is designed to be run locally during development. Database and configuration details may change as the application continues to evolve.

## What I Learned

This project was built as a practical way to develop backend engineering skills rather than as a tutorial implementation. The main areas of focus were:

- Designing and organizing a Python backend
- Building APIs with FastAPI
- Authentication and authorization with JWTs
- Secure password storage using password hashing
- Working with relational databases and SQL
- Building real-time features with WebSockets
- Managing multiple active connections
- Separating application responsibilities into different modules
- Writing automated tests with pytest
- Debugging backend logic and handling edge cases
- Connecting a browser client to a Python backend

A major part of the project has been learning how individual backend components interact as the application grows, rather than treating the server as a single monolithic script.

## Frontend Note

The application includes a functional browser UI so the backend can be used and demonstrated without a separate API client. The HTML, JavaScript, and CSS were written as part of the project, but the frontend is intentionally simple.

The CSS in particular is **basic, custom CSS** intended to make the application usable and presentable rather than demonstrate advanced frontend engineering. The project's main emphasis is on the **Python backend, API design, authentication, database work, WebSockets, and testing**.

## Current Limitations

This is a personal project and is not presented as production-ready software. Some areas are still being improved, including:

- Expanding test coverage
- Refactoring and improving code organization
- Improving error handling and validation across the application
- Further hardening authentication and configuration for production deployment
- Improving the frontend presentation where useful

These limitations are part of the project's ongoing development and provide areas for further iteration.
