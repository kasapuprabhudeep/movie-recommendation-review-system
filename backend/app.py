import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from database import db, NEO4J_URI
from recommender import recommender
from seed_data import seed_database
from load_tmdb import import_tmdb_dataset

load_dotenv()

def find_frontend_dist():
    """Locate the built React frontend dist directory across multiple deployment layouts."""
    candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")),
        os.path.abspath(os.path.join(os.getcwd(), "frontend", "dist")),
        os.path.abspath(os.path.join(os.getcwd(), "MovieRecommendationSystem", "frontend", "dist")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "dist")),
        os.path.abspath("dist")
    ]
    for c in candidates:
        if os.path.isdir(c) and os.path.isfile(os.path.join(c, "index.html")):
            return c
    for c in candidates:
        if os.path.isdir(c):
            return c
    return candidates[0]

FRONTEND_DIST = find_frontend_dist()
app = Flask(__name__, static_folder=None)
CORS(app, resources={r"/api/*": {"origins": "*"}})
PORT = int(os.getenv("PORT", 5000))

# ── Auto-seed on startup if DB is empty ─────────────────────────────────────
try:
    count = db.movies.count_documents({}) if db.mongo_connected else len(db.embedded_mongo.movies.find({}))
    if count == 0:
        print("No movies found. Seeding sample data...")
        seed_database(db)
        print("Sample data seeded successfully.")
except Exception as e:
    print(f"Warning: Auto-seed check failed: {e}")


# ── Helper ───────────────────────────────────────────────────────────────────

def clean_doc(doc):
    """Remove MongoDB _id ObjectId and return plain dict."""
    if doc is None:
        return None
    d = dict(doc)
    d.pop("_id", None)
    return d


def format_movie_response(movie):
    """Enrich movie dict with live rating stats."""
    if not movie:
        return None
    doc = clean_doc(movie)
    m_id = str(doc.get("id") or "")
    doc["id"] = m_id

    ratings = list(db.ratings.find({"movie_id": m_id}))
    if ratings:
        doc["user_rating_avg"] = round(sum(float(r.get("rating", 0)) for r in ratings) / len(ratings), 1)
        doc["user_rating_count"] = len(ratings)
    else:
        doc["user_rating_avg"] = doc.get("rating", 0)
        doc["user_rating_count"] = 0
    return doc


# ── System / Seed ────────────────────────────────────────────────────────────

@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify(db.get_system_status())


@app.route("/api/seed", methods=["POST"])
def trigger_seed():
    status = seed_database(db)
    return jsonify({"message": "Database successfully populated with sample data", "status": status}), 200


@app.route("/api/tmdb/import", methods=["POST"])
def trigger_tmdb_import():
    """Import TMDB movies. Supports offset for paginated batch importing."""
    data = request.get_json() or {}
    limit = int(data.get("limit", 100))
    offset = int(data.get("offset", 0))
    result = import_tmdb_dataset(limit=limit, offset=offset, target_db=db)
    return jsonify(result), (200 if result.get("success") else 400)


@app.route("/api/tmdb/status", methods=["GET"])
def tmdb_status():
    """Returns status of the TMDB data directory and CSV files."""
    import os
    from load_tmdb import TMDB_DIR
    movies_path = os.path.join(TMDB_DIR, "tmdb_5000_movies.csv")
    credits_path = os.path.join(TMDB_DIR, "tmdb_5000_credits.csv")
    movies_exist = os.path.exists(movies_path)
    credits_exist = os.path.exists(credits_path)
    total_csv_rows = 0
    if movies_exist:
        from load_tmdb import count_csv_rows
        total_csv_rows = count_csv_rows(movies_path)
    try:
        total_in_db = db.movies.count_documents({}) if db.mongo_connected else len(db.embedded_mongo.movies.find({}))
    except Exception:
        total_in_db = 0
    return jsonify({
        "tmdb_dir": TMDB_DIR,
        "movies_csv_found": movies_exist,
        "credits_csv_found": credits_exist,
        "total_csv_rows": total_csv_rows,
        "total_in_db": total_in_db
    })


@app.route("/api/neo4j/sync", methods=["POST"])
def sync_to_neo4j():
    """Push all movies from MongoDB into live Neo4j with full graph relationships."""
    if not db.ensure_neo4j():
        return jsonify({
            "success": False,
            "error": "Cannot connect to Neo4j at bolt://localhost:7687. Make sure your Neo4j Desktop DBMS is started and password in backend/.env matches."
        }), 503

    synced = 0
    all_movies = list(db.movies.find({}))
    for movie in all_movies:
        try:
            db.sync_movie_to_graph(movie)
            synced += 1
        except Exception as e:
            print(f"Error syncing {movie.get('title')}: {e}")

    for r in db.ratings.find({}):
        try:
            db.record_user_rating_in_graph(r["user_id"], r["movie_id"], r["rating"])
        except Exception:
            pass

    for w in db.watchlists.find({}):
        try:
            db.record_watchlist_in_graph(w["user_id"], w["movie_id"], action="add")
        except Exception:
            pass

    # Get live count in Neo4j
    nodes = 0
    rels = 0
    try:
        with db.neo4j_driver.session() as s:
            nodes = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
            rels = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
    except Exception:
        pass

    return jsonify({
        "success": True,
        "synced_movies": synced,
        "neo4j_nodes": nodes,
        "neo4j_relationships": rels,
        "message": f"Successfully synced {synced} movies to Neo4j Desktop! Live Neo4j now contains {nodes} nodes and {rels} relationships."
    })


@app.route("/api/neo4j/status", methods=["GET"])
def neo4j_status():
    connected = db.ensure_neo4j()
    result = {
        "connected": connected,
        "uri": NEO4J_URI,
        "mode": "Live Neo4j Database" if connected else "Built-in Graph Engine (Fallback Active)",
        "embedded_nodes": len(db.embedded_graph.nodes),
        "embedded_edges": len(db.embedded_graph.edges)
    }
    if connected and db.neo4j_driver:
        try:
            with db.neo4j_driver.session() as session:
                result["neo4j_nodes"] = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
                result["neo4j_relationships"] = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
        except Exception as e:
            result["error"] = str(e)
    return jsonify(result)


# ── Movies ───────────────────────────────────────────────────────────────────

@app.route("/api/movies", methods=["GET"])
def get_movies():
    search_query = request.args.get("search", "").strip().lower()
    genre_filter = request.args.get("genre", "").strip()
    sort_by = request.args.get("sort", "rating")
    limit = int(request.args.get("limit", 50))
    page = int(request.args.get("page", 1))

    filtered = []
    for m in db.movies.find({}):
        if genre_filter and genre_filter.lower() != "all":
            if genre_filter.lower() not in [g.lower() for g in m.get("genres", [])]:
                continue
        if search_query:
            haystack = " ".join([
                m.get("title", ""),
                m.get("director", ""),
                m.get("plot", ""),
                " ".join(m.get("actors", []))
            ]).lower()
            if search_query not in haystack:
                continue
        filtered.append(format_movie_response(m))

    if sort_by == "rating":
        filtered.sort(key=lambda x: float(x.get("rating", 0)), reverse=True)
    elif sort_by == "year":
        filtered.sort(key=lambda x: int(x.get("year", 0)), reverse=True)
    elif sort_by == "title":
        filtered.sort(key=lambda x: x.get("title", "").lower())

    total = len(filtered)
    start_idx = (page - 1) * limit
    return jsonify({"movies": filtered[start_idx: start_idx + limit], "total": total, "page": page, "limit": limit})


@app.route("/api/movies/<movie_id>", methods=["GET"])
def get_movie_details(movie_id):
    movie = db.movies.find_one({"id": movie_id}) or db.movies.find_one({"_id": movie_id})
    if not movie:
        return jsonify({"error": "Movie not found"}), 404

    reviews = [clean_doc(r) for r in db.reviews.find({"movie_id": movie_id})]
    reviews.sort(key=lambda r: r.get("created_at", ""), reverse=True)

    similar_movies = recommender.get_similar_movies(movie_id, top_n=4)
    # Clean similar movie docs
    clean_similar = []
    for s in similar_movies:
        s_copy = dict(s)
        if "movie" in s_copy:
            s_copy["movie"] = clean_doc(s_copy["movie"])
        clean_similar.append(s_copy)

    return jsonify({"movie": format_movie_response(movie), "reviews": reviews, "similar": clean_similar})


@app.route("/api/genres", methods=["GET"])
def get_genres():
    genres = set()
    for m in db.movies.find({}):
        for g in m.get("genres", []):
            genres.add(g)
    return jsonify({"genres": sorted(list(genres))})


# ── Recommendations ───────────────────────────────────────────────────────────

@app.route("/api/recommendations", methods=["GET"])
def get_recommendations():
    user_id = request.args.get("user_id")
    limit = int(request.args.get("limit", 8))
    recs = recommender.get_user_recommendations(user_id=user_id, top_n=limit)
    clean_recs = []
    for r in recs:
        r_copy = dict(r)
        if "movie" in r_copy:
            r_copy["movie"] = clean_doc(r_copy["movie"])
        clean_recs.append(r_copy)
    return jsonify({"recommendations": clean_recs, "user_id": user_id,
                    "type": "personalized_graph" if user_id else "community_trending"})


@app.route("/api/movies/<movie_id>/similar", methods=["GET"])
def get_similar_movies_route(movie_id):
    limit = int(request.args.get("limit", 6))
    similar = recommender.get_similar_movies(movie_id, top_n=limit)
    clean_similar = []
    for s in similar:
        s_copy = dict(s)
        if "movie" in s_copy:
            s_copy["movie"] = clean_doc(s_copy["movie"])
        clean_similar.append(s_copy)
    return jsonify({"movie_id": movie_id, "similar": clean_similar})


# ── Auth ─────────────────────────────────────────────────────────────────────

@app.route("/api/users/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    bio = data.get("bio", "Film lover").strip()

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    if db.users.find_one({"username": username}):
        return jsonify({"error": "Username already exists"}), 409

    new_id = "u_" + str(uuid.uuid4())[:8]
    user_doc = {"id": new_id, "_id": new_id, "username": username, "password": password,
                "name": name or username, "email": email, "bio": bio,
                "created_at": datetime.now().isoformat()}
    db.users.insert_one(user_doc)
    return jsonify({"message": "User registered successfully",
                    "user": {"id": new_id, "username": username, "name": name or username,
                             "email": email, "bio": bio}}), 201


@app.route("/api/users/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    user = db.users.find_one({"username": username})
    if not user or user.get("password") != password:
        return jsonify({"error": "Invalid username or password"}), 401
    uid = user.get("id") or str(user.get("_id"))
    return jsonify({"message": "Login successful",
                    "user": {"id": uid, "username": user.get("username"),
                             "name": user.get("name", username), "email": user.get("email", ""),
                             "bio": user.get("bio", "")},
                    "token": f"token_{uid}_{uuid.uuid4().hex[:12]}"})


@app.route("/api/users/<user_id>", methods=["GET"])
def get_user_profile(user_id):
    user = db.users.find_one({"id": user_id}) or db.users.find_one({"_id": user_id})
    if not user:
        return jsonify({"error": "User not found"}), 404
    uid = user.get("id") or str(user.get("_id"))
    ratings_count = len(list(db.ratings.find({"user_id": user_id})))
    reviews_count = len(list(db.reviews.find({"user_id": user_id})))
    watchlist_count = len(list(db.watchlists.find({"user_id": user_id})))
    return jsonify({"user": {"id": uid, "username": user.get("username"),
                             "name": user.get("name"), "email": user.get("email"),
                             "bio": user.get("bio")},
                    "stats": {"ratings_count": ratings_count, "reviews_count": reviews_count,
                              "watchlist_count": watchlist_count}})


# ── Ratings ───────────────────────────────────────────────────────────────────

@app.route("/api/movies/<movie_id>/ratings", methods=["POST"])
def rate_movie(movie_id):
    data = request.get_json() or {}
    user_id = data.get("user_id")
    username = data.get("username", "Anonymous")
    rating_val = data.get("rating")
    if not user_id or rating_val is None:
        return jsonify({"error": "user_id and rating are required"}), 400
    try:
        rating_val = float(rating_val)
        if not (1.0 <= rating_val <= 5.0):
            return jsonify({"error": "Rating must be between 1.0 and 5.0"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid rating number"}), 400

    existing = db.ratings.find_one({"user_id": str(user_id), "movie_id": str(movie_id)})
    if existing:
        db.ratings.update_one({"user_id": str(user_id), "movie_id": str(movie_id)},
                              {"$set": {"rating": rating_val, "updated_at": datetime.now().isoformat()}})
    else:
        db.ratings.insert_one({"id": "r_" + str(uuid.uuid4())[:8], "user_id": str(user_id),
                                "username": username, "movie_id": str(movie_id),
                                "rating": rating_val, "created_at": datetime.now().isoformat()})
    db.record_user_rating_in_graph(user_id, movie_id, rating_val)

    all_r = list(db.ratings.find({"movie_id": str(movie_id)}))
    new_avg = round(sum(float(r["rating"]) for r in all_r) / len(all_r), 1) if all_r else rating_val
    return jsonify({"message": "Rating saved successfully", "movie_id": movie_id,
                    "user_rating": rating_val, "new_average": new_avg, "total_votes": len(all_r)})


@app.route("/api/movies/<movie_id>/user-rating/<user_id>", methods=["GET"])
def get_user_movie_rating(movie_id, user_id):
    existing = db.ratings.find_one({"user_id": str(user_id), "movie_id": str(movie_id)})
    return jsonify({"rated": bool(existing), "rating": existing.get("rating") if existing else None})


# ── Reviews ───────────────────────────────────────────────────────────────────

@app.route("/api/movies/<movie_id>/reviews", methods=["GET"])
def get_movie_reviews(movie_id):
    reviews = [clean_doc(r) for r in db.reviews.find({"movie_id": str(movie_id)})]
    reviews.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return jsonify({"reviews": reviews})


@app.route("/api/movies/<movie_id>/reviews", methods=["POST"])
def add_movie_review(movie_id):
    data = request.get_json() or {}
    user_id = data.get("user_id")
    username = data.get("username", "Anonymous")
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    rating_val = float(data.get("rating", 5.0))
    if not user_id or not content:
        return jsonify({"error": "user_id and review content are required"}), 400

    rev_id = "rev_" + str(uuid.uuid4())[:8]
    review_doc = {"id": rev_id, "_id": rev_id, "user_id": str(user_id), "username": username,
                  "movie_id": str(movie_id), "title": title or "My Review",
                  "content": content, "rating": rating_val, "created_at": datetime.now().isoformat()}
    db.reviews.insert_one(review_doc)
    db.record_user_rating_in_graph(user_id, movie_id, rating_val)
    review_doc.pop("_id", None)
    return jsonify({"message": "Review submitted successfully", "review": review_doc}), 201


@app.route("/api/reviews/<review_id>", methods=["DELETE"])
def delete_review(review_id):
    ok = db.reviews.delete_one({"id": review_id}) or db.reviews.delete_one({"_id": review_id})
    return jsonify({"success": bool(ok)})


# ── Watchlist ─────────────────────────────────────────────────────────────────

@app.route("/api/watchlist/<user_id>", methods=["GET"])
def get_user_watchlist(user_id):
    movies = []
    for item in db.watchlists.find({"user_id": str(user_id)}):
        m_id = str(item.get("movie_id"))
        m = db.movies.find_one({"id": m_id}) or db.movies.find_one({"_id": m_id})
        if m:
            m_copy = format_movie_response(m)
            m_copy["watchlist_id"] = item.get("id") or str(item.get("_id"))
            m_copy["added_at"] = item.get("added_at")
            movies.append(m_copy)
    return jsonify({"user_id": user_id, "watchlist": movies, "count": len(movies)})


@app.route("/api/watchlist", methods=["POST"])
def add_to_watchlist():
    data = request.get_json() or {}
    user_id = str(data.get("user_id", ""))
    movie_id = str(data.get("movie_id", ""))
    if not user_id or not movie_id:
        return jsonify({"error": "user_id and movie_id are required"}), 400
    if db.watchlists.find_one({"user_id": user_id, "movie_id": movie_id}):
        return jsonify({"message": "Movie already in watchlist", "already_present": True}), 200
    w_id = "w_" + str(uuid.uuid4())[:8]
    item = {"id": w_id, "_id": w_id, "user_id": user_id, "movie_id": movie_id,
            "added_at": datetime.now().isoformat()}
    db.watchlists.insert_one(item)
    db.record_watchlist_in_graph(user_id, movie_id, action="add")
    item.pop("_id", None)
    return jsonify({"message": "Added to watchlist", "watchlist_item": item}), 201


@app.route("/api/watchlist/<user_id>/<movie_id>", methods=["DELETE"])
def remove_from_watchlist(user_id, movie_id):
    db.watchlists.delete_one({"user_id": str(user_id), "movie_id": str(movie_id)})
    db.record_watchlist_in_graph(user_id, movie_id, action="remove")
    return jsonify({"message": "Removed from watchlist", "movie_id": movie_id})


# ── Serve React Frontend (Single-Service Cloud Deployment) ───────────────────
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    dist_dir = find_frontend_dist()
    target_file = os.path.join(dist_dir, path) if path else ""

    # 1. If path is a real asset file (e.g. assets/index-*.js, assets/*.css, favicon.ico)
    if path and os.path.isfile(target_file):
        return send_from_directory(dist_dir, path)

    # 2. If index.html exists, serve React App for all browser routes
    index_path = os.path.join(dist_dir, "index.html")
    if os.path.isfile(index_path):
        return send_from_directory(dist_dir, "index.html")

    # 3. Informative diagnostic page if frontend assets have not yet finished compiling
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CineGraph — Backend Live</title>
  <style>
    body { background: #0b1120; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }
    .box { background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 40px; max-width: 620px; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }
    h1 { color: #38bdf8; margin: 0 0 12px; font-size: 26px; }
    p { color: #94a3b8; font-size: 15px; line-height: 1.6; margin: 8px 0; }
    .status { display: inline-block; padding: 6px 14px; border-radius: 20px; background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); font-weight: 600; font-size: 13px; margin-bottom: 20px; }
    .links { margin-top: 24px; display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
    a.btn { background: #2563eb; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 8px; font-size: 14px; font-weight: 600; transition: background 0.2s; }
    a.btn:hover { background: #1d4ed8; }
    a.btn-secondary { background: #334155; }
    a.btn-secondary:hover { background: #475569; }
  </style>
</head>
<body>
  <div class="box">
    <div class="status">● Flask Backend Server Live & Healthy</div>
    <h1>CineGraph Engine is Online</h1>
    <p>The backend database & graph recommendation service is fully functional.</p>
    <div class="links">
      <a class="btn" href="/api/movies">View 555 Movies JSON (/api/movies)</a>
      <a class="btn btn-secondary" href="/api/status">System Status (/api/status)</a>
      <a class="btn btn-secondary" href="/api/recommendations">Recommendations API</a>
    </div>
  </div>
</body>
</html>""", 200


if __name__ == "__main__":
    print(f"Starting Movie Recommendation System Backend on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=False)
