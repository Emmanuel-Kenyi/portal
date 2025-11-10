# Student Project

This is a Django-based web application for managing student projects, with a mobile-first interface built using React Native.

## Features

- **User Authentication:** Students, lecturers, and admins can sign up and log in to the application.
- **Club Management:** Create, manage, and view details of student clubs.
- **Announcements and Polls:** Post announcements and create polls within clubs.
- **Point System:** Award points to students for their activities.
- **Grade Management:** Lecturers can add and edit student marks.
- **Reporting:** Generate reports on club activities and system usage.
- **API:** A RESTful API for interacting with the application data.

## Installation

### Prerequisites

- Python 3.11+
- Node.js and npm
- Pip (Python package installer)

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Emmanuel-Kenyi/portal
   cd portal
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Navigate to the mobile app directory:**
   ```bash
   cd student_project_mobile
   ```

2. **Install JavaScript dependencies:**
   ```bash
   npm install
   ```

3. **Run the mobile app:**
   ```bash
   npm start
   ```

## Project Structure

This project is composed of a Django backend and a React Native mobile frontend.

### Backend

The Django backend is organized into the following core applications:

- **`student_project`**: The main Django project directory, containing the settings and primary configuration.
- **`api`**: A Django Rest Framework app that provides a comprehensive set of API endpoints for mobile and web clients.
- **`clubs`**: A Django app responsible for all club-related functionalities, including creation, membership, announcements, and polls.
- **`users`**: A Django app that manages user authentication, profiles, roles (student, lecturer, admin), and permissions.

### Frontend

- **`student_project_mobile`**: A React Native application that serves as the mobile interface for the project, consuming the backend API.

### Shared Resources

- **`static`**: Contains static assets such as CSS, JavaScript, and images used across the web application.
- **`templates`**: Holds the Django HTML templates for rendering the web pages.



## API Endpoints

- **`api/token/`**: Obtain a JWT token.
- **`api/token/refresh/`**: Refresh a JWT token.
- **`api/clubs/`**: List and create clubs.
- **`api/clubs/<id>/`**: Retrieve, update, or delete a club.
- **`api/reports/system`**: Generate a system report.
- **`api/user/gpa/<student_id>`**: View a student's GPA.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License.
