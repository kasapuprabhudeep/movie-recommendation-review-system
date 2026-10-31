# 🎬 CineGraph — Movie Recommendation & Review System

A full-stack, responsive Movie Recommendation and Review application built with **React**, **Python Flask**, **MongoDB**, and **Neo4j**. Features graph-based recommendations with explainable AI, collaborative filtering, user ratings, reviews, watchlists, and authentication.

---

## 🌟 Key Features

1. **Clean & Responsive UI (React)**
   - **Movie Catalog**: Instant search by title, director, cast, or plot keywords, with interactive genre filters and sorting options.
   - **Movie Details**: Full film metadata, runtime, director, actors, user rating summary, and community reviews.
   - **Interactive Ratings & Reviews**: Users can rate movies (1 to 5 stars) and publish detailed reviews with moderation controls.
   - **Personalized Watchlist**: Save movies to a personal watchlist with real-time graph updates.
   - **Persona Switcher**: Simulate recommendations across different user personas (e.g., Sci-Fi lover vs. Tarantino fan) to witness dynamic graph traversals live.
   - **Authentication**: User registration and login, with preconfigured one-click demo credentials for immediate testing.

2. **Dual-Database Architecture**
   - **MongoDB (Document Store)**: Stores movie details, user profiles, text reviews, numeric ratings, and user watchlists.
   - **Neo4j (Graph Database)**: Stores nodes (`:Movie`, `:Genre`, `:Actor`, `:Director`, `:User`) and relationships (`:IN_GENRE`, `:ACTED_IN`, `:DIRECTED`, `:RATED`, `:WATCHLISTED`).
   - **Built-in Smart Fallback**: The backend includes real `pymongo` and `neo4j` drivers that automatically connect to live MongoDB/Neo4j servers when available. If external database processes are not running, it automatically operates a built-in document and graph engine so the entire system works **100% out of the box without requiring Docker or manual database installations**.

3. **Graph-Powered Explainable Recommendations**
   - **Content-Graph Traversal**: Traverses direct graph links between movies sharing the same director, cast members, and genres with weighted graph proximity scores.
   - **Collaborative Filtering**: Traverses user-to-movie graph paths `(User A)-[:RATED]->(Movie 1)<-[:RATED]-(User B)-[:RATED]->(Movie 2)` to discover movies liked by viewers with similar tastes.
   - **Human-Readable Explanations**: Displays clear explanations for every recommendation (e.g., *"Same Director (Christopher Nolan) & Shared Cast (Cillian Murphy)"* or *"Viewers who enjoyed 'Inception' also gave this high marks"*).

---

## 🛠️ Technologies Used

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite 5, JavaScript (ES6+), Modern Vanilla CSS |
| **Backend** | Python 3.13, Flask 3.1, Flask-CORS, Python-Dotenv, Werkzeug |
| **Database Drivers** | `pymongo` 4.19, `neo4j` Python driver 6.4 |
| **Databases** | MongoDB (Document Store), Neo4j (Graph Database) |
| **Containerization** | Docker & Docker Compose (`docker-compose.yml` included) |
| **Testing** | Python `unittest`, automated connection diagnostics |

---

## 🗄️ Database Design

### 1. MongoDB Document Collections

- **`movies`**:
  ```json
  {
    "id": "m1",
    "title": "Inception",
    "year": 2010,
    "runtime": "148 min",
    "director": "Christopher Nolan",
    "genres": ["Sci-Fi", "Action", "Adventure"],
    "actors": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page", "Cillian Murphy"],
    "rating": 8.8,
    "votes": 2400000,
    "poster": "https://images.unsplash.com/...",
    "plot": "A thief who steals corporate secrets through dream-sharing..."
  }
  ```
- **`users`**: `{ id, username, password, name, email, bio, created_at }`
- **`ratings`**: `{ id, user_id, username, movie_id, rating, created_at }`
- **`reviews`**: `{ id, user_id, username, movie_id, title, content, rating, created_at }`
- **`watchlists`**: `{ id, user_id, movie_id, added_at }`

### 2. Neo4j Graph Model

- **Nodes**:
  - `(:Movie {id, title, director, rating})`
  - `(:Genre {name})`
  - `(:Actor {name})`
  - `(:Director {name})`
  - `(:User {id})`
- **Relationships**:
  - `(:Movie)-[:IN_GENRE]->(:Genre)`
  - `(:Actor)-[:ACTED_IN]->(:Movie)`
  - `(:Director)-[:DIRECTED]->(:Movie)`
  - `(:User)-[:RATED {rating}]->(:Movie)`
  - `(:User)-[:WATCHLISTED]->(:Movie)`

---

## 📁 Project Structure

```
MovieRecommendationSystem/
├── backend/
│   ├── app.py                 # Flask REST API server & routing
│   ├── database.py            # MongoDB & Neo4j clients + fallback engine
│   ├── recommender.py         # Graph traversal & recommendation algorithms
│   ├── seed_data.py           # Database seeder with sample movies, users, ratings
│   ├── test_connections.py    # Database connection & graph diagnostics script
│   ├── test_api.py            # 11 automated API unit tests
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Configuration & port settings
│   └── data/                  # Local persistent store (JSON)
├── frontend/
│   ├── package.json           # React dependencies & scripts
│   ├── vite.config.js         # Vite configuration with /api proxy
│   ├── index.html             # HTML entry point
│   └── src/
│       ├── main.jsx           # React DOM root
│       ├── App.jsx            # State & page navigation
│       ├── index.css          # Clean dark-slate design system
│       ├── services/
│       │   └── api.js         # Unified API client
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── MovieCard.jsx
│       │   ├── RecommendationCard.jsx
│       │   ├── RatingModal.jsx
│       │   ├── ReviewModal.jsx
│       │   └── StatusBanner.jsx
│       └── pages/
│           ├── Home.jsx
│           ├── MovieDetails.jsx
│           ├── Recommendations.jsx
│           ├── Watchlist.jsx
│           ├── Login.jsx
│           └── Register.jsx
├── docker-compose.yml         # Pre-configured MongoDB & Neo4j containers
├── render.yaml                # Render Blueprint for 1-click cloud deployment
├── Procfile                   # Process file for cloud hosting (Render, Railway)
├── build.sh                   # Cloud build script (React build + Python install)
├── run_all.bat                # 1-Click launcher for both backend & frontend
├── start_backend.bat          # 1-Click launcher for Flask backend
├── start_frontend.bat         # 1-Click launcher for React frontend
├── share_instant_link.bat     # 1-Click instant public HTTPS link generator
├── push_to_github.bat         # 1-Click GitHub publisher
├── test_system.bat            # 1-Click test runner for all tests
├── DEPLOYMENT_GUIDE.md        # Comprehensive deployment and sharing instructions
└── README.md                  # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+** (Python 3.13 tested)
- **Node.js 18+** and **npm**

### Step 1: Install Dependencies

1. **Backend Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. **Frontend Dependencies**:
   ```bash
   cd ../frontend
   npm install
   ```

### Step 2: Seed the Database

Populate sample movies, genres, actors, directors, ratings, and reviews:
```bash
cd backend
python seed_data.py
```

### Step 3: Run the Application

You can start both frontend and backend using the provided batch script or separate terminals:

#### Option A: Quick Launcher (Windows)
Double-click `run_all.bat` or run:
```bash
.\run_all.bat
```

#### Option B: Manual Startup

- **Terminal 1 (Backend)**:
  ```bash
  cd backend
  python app.py
  ```
  *Server starts at `http://localhost:5000`*

- **Terminal 2 (Frontend)**:
  ```bash
  cd frontend
  npm run dev
  ```
  *React application opens at `http://localhost:3000`*

---

## 🐳 Optional: Running with Real Docker Databases

The system works automatically without Docker. However, if you wish to run dedicated live MongoDB and Neo4j database containers:

1. Start the Docker containers:
   ```bash
   docker compose up -d
   ```
   - **MongoDB** will listen on `localhost:27017`
   - **Neo4j** will listen on `localhost:7687` (Web browser UI at `http://localhost:7474`, auth: `neo4j` / `password123`)

2. Re-run `python seed_data.py` to populate the live containers. The backend will detect the live connections automatically!

---

## 🧪 Testing & Verification

Run the comprehensive automated test suite:

### 1. Database Connection & Graph Diagnostics
```bash
cd backend
python test_connections.py
```
*Verifies database status, collection counts, graph nodes, relationships, and similarity queries.*

### 2. Full API Endpoint Test Suite (11 Tests)
```bash
cd backend
python -m unittest test_api.py
```
*Tests status, movie listing, search, genre filters, details, authentication, rating upsert, review posting, watchlist manipulation, and recommendations.*

### 3. One-Click Test Runner
```bash
.\test_system.bat
```

---

## 👥 Demo Accounts

The application includes pre-configured sample users for instant testing (also available as one-click login buttons on the login page):

| Username | Password | Profile / Taste |
|---|---|---|
| `demo_user` | `demo123` | Default tester account |
| `alex_reviewer` | `alex123` | Nolan and Sci-Fi enthusiast |
| `sarah_cinephile` | `sarah123` | Tarantino & Korean thriller fan |
| `david_film` | `david123` | Cyberpunk & 90s cinema collector |

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/status` | System health, DB connection status & counts |
| `POST` | `/api/seed` | Reset & re-seed sample database |
| `GET` | `/api/movies` | List movies (supports `search`, `genre`, `sort`) |
| `GET` | `/api/movies/<id>` | Full movie details, reviews & similar movies |
| `GET` | `/api/genres` | List of all unique genres |
| `GET` | `/api/recommendations` | Hybrid & graph-traversed recommendations |
| `GET` | `/api/movies/<id>/similar`| Similar movies by graph traversal |
| `POST` | `/api/users/register` | Register new user |
| `POST` | `/api/users/login` | Authenticate user |
| `POST` | `/api/movies/<id>/ratings` | Rate a movie (1 to 5 stars) |
| `GET` | `/api/movies/<id>/reviews` | Get reviews for a movie |
| `POST` | `/api/movies/<id>/reviews` | Submit a review |
| `DELETE`| `/api/reviews/<id>` | Delete a review |
| `GET` | `/api/watchlist/<user_id>` | Get user's watchlist |
| `POST` | `/api/watchlist` | Add movie to watchlist |
| `DELETE`| `/api/watchlist/<uid>/<mid>`| Remove movie from watchlist |

