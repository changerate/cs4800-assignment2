## CPP Parking Chaos
*cs4800 assignment 2*

*Cal Poly Pomona, Spring 2026*

This project is a small full‑stack web app where students try to "park" as many vehicles as they can on a shared grid. Everyone sees the same grid in real time, so when someone else parks on top of you it feels like they "towed" your vehicle away.

The app is intentionally light‑hearted and a bit chaotic, but it is built as a proper production‑style stack with backend, frontend, database, AWS deployment, and CI/CD.

---

### High‑level idea

- **Concept**: A multiplayer parking grid for CPP students.
- **Goal**: Log in, pick a fun vehicle emoji (🚗, 🛸, 🚀, etc.), and click on cells in the grid to park your vehicle.
- **Social twist**: Because everyone shares the same grid, other students can overwrite your parking spot; from your perspective, they just "towed" you.

---

### Mapping to formal homework requirements

#### 1. Application

- **Backend server (Python, Flask)**:
  - Implemented with **Flask** in `backend/app/__init__.py` using the application factory pattern.
  - Uses blueprints under `backend/app/api/v1` for versioned APIs.

- **Frontend (HTML/CSS/JavaScript)**:
  - `index.html` contains the login form, vehicle selector, grid container, and log sidebar.
  - `styles.css` defines the responsive layout and grid styling.
  - Inline JavaScript in `index.html` handles:
    - User authentication (login/register and logout).
    - Choosing vehicles.
    - Rendering the grid and reacting to clicks.
    - Polling the backend every few seconds to keep the grid and activity log up to date.

- **Create / Read functionality**
  - **Create/Update**:
    - The user is able to create a simple account that registers a new user with `/login` when a username does not yet exist.
    - Updating the user’s selected vehicle via `/me/vehicle`.
    - Toggling grid cells via `/api/v1/grid/toggle`, which writes the current user’s vehicle (or clears it).
  - **Read**:
    - Reading the current user via `/me`.
    - Reading the current grid state and activity logs via `/api/v1/grid`.

- **Persistent data in a database**
  - The grid state and users are stored in a cloud database via SQLAlchemy models, so:
    - The grid state survives server restarts.
    - User accounts and vehicle choices persist across sessions.

#### 2. Engineering

- **Code pushed to GitHub**
  - The entire project (backend, frontend, configuration, and CI/CD workflow) lives in this GitHub repository.

- **Clean project structure**
  - Clear separation between concerns:
    - `backend/app/` for Flask app code (factory, blueprints, models, extensions, config).
    - `backend/app/templates/` for HTML templates.
    - `backend/app/static/` for static assets like CSS.
    - `.github/workflows/` for CI/CD configuration.
  - Uses the application factory pattern and blueprints, which is standard practice for medium‑sized Flask apps.

#### 3. Deployment

- **Deployed to AWS EC2**
  - The workflow assumes an EC2 host (`EC2_HOST`) and user (`EC2_USER`) with SSH access.
  - The Flask app is run as a `systemd` service named `flaskapp` on the instance.

- **Publicly accessible via EC2 URL http://18.119.220.37**
  - The EC2 instance exposes the Flask app over HTTP (for grading: the instructor can visit the EC2 URL to interact with the parking grid).

- **GitHub Actions auto‑deploy on push to main**
  - `.github/workflows/deploy.yml` triggers on `push` to `main`.
  - Deployment is repeatable and automated; no manual SSH steps are required beyond the initial server setup.
