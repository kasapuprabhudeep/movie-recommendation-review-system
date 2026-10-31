import os
import csv
import json
import ast
import logging
from database import db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TMDBLoader")

TMDB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "tmdb")

GENRE_POSTERS = {
    "Action":     "https://images.unsplash.com/photo-1509281373149-e957c6296406?w=600&auto=format&fit=crop&q=80",
    "Sci-Fi":     "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=600&auto=format&fit=crop&q=80",
    "Science Fiction": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&auto=format&fit=crop&q=80",
    "Drama":      "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600&auto=format&fit=crop&q=80",
    "Crime":      "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=600&auto=format&fit=crop&q=80",
    "Adventure":  "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&auto=format&fit=crop&q=80",
    "Animation":  "https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=600&auto=format&fit=crop&q=80",
    "Comedy":     "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop&q=80",
    "Thriller":   "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=600&auto=format&fit=crop&q=80",
    "Romance":    "https://images.unsplash.com/photo-1518999406264-2c9aa2ad3a4a?w=600&auto=format&fit=crop&q=80",
    "Horror":     "https://images.unsplash.com/photo-1509248961158-e54f6934749c?w=600&auto=format&fit=crop&q=80",
    "Fantasy":    "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=600&auto=format&fit=crop&q=80",
    "History":    "https://images.unsplash.com/photo-1524985069026-dd778a71c7b4?w=600&auto=format&fit=crop&q=80",
    "War":        "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=600&auto=format&fit=crop&q=80",
    "Biography":  "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=600&auto=format&fit=crop&q=80",
    "Mystery":    "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600&auto=format&fit=crop&q=80",
    "Western":    "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop&q=80",
}

# In-memory credits cache: loaded once and shared across imports for 100x speed
_GLOBAL_CREDITS_CACHE = None

def safe_parse_json(text):
    if not text:
        return []
    try:
        return json.loads(text)
    except Exception:
        try:
            return ast.literal_eval(text)
        except Exception:
            return []

def load_credits(credits_path):
    global _GLOBAL_CREDITS_CACHE
    if _GLOBAL_CREDITS_CACHE is not None:
        return _GLOBAL_CREDITS_CACHE

    credits_map = {}
    if not os.path.exists(credits_path):
        _GLOBAL_CREDITS_CACHE = credits_map
        return credits_map

    logger.info(f"Loading and caching credits from {credits_path}...")
    try:
        with open(credits_path, mode="r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                mid = row.get("movie_id") or row.get("id")
                if not mid:
                    continue
                cast_raw = safe_parse_json(row.get("cast", "[]"))
                crew_raw = safe_parse_json(row.get("crew", "[]"))
                actors = [c["name"] for c in cast_raw[:5] if isinstance(c, dict) and "name" in c]
                director = next(
                    (m.get("name", "") for m in crew_raw if isinstance(m, dict) and m.get("job") == "Director"),
                    ""
                )
                credits_map[str(mid)] = {"director": director, "actors": actors}
    except Exception as e:
        logger.warning(f"Error loading credits: {e}")

    logger.info(f"Cached credits for {len(credits_map)} movies.")
    _GLOBAL_CREDITS_CACHE = credits_map
    return credits_map

def count_csv_rows(movies_path):
    """Count total valid (non-header) rows in the CSV."""
    try:
        with open(movies_path, mode="r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in csv.DictReader(f))
    except Exception:
        return 0

def import_tmdb_dataset(limit=100, offset=0, target_db=None):
    """
    High-performance batch importer for TMDB movies.
    Uses in-memory credits cache and deferred disk writes for sub-second speeds.
    """
    target_db = target_db or db
    target_db.ensure_neo4j()

    movies_path = os.path.join(TMDB_DIR, "tmdb_5000_movies.csv")
    credits_path = os.path.join(TMDB_DIR, "tmdb_5000_credits.csv")

    if not os.path.exists(movies_path):
        for alt in ["movies.csv", "tmdb.csv", "tmdb_movies.csv"]:
            candidate = os.path.join(TMDB_DIR, alt)
            if os.path.exists(candidate):
                movies_path = candidate
                break

    if not os.path.exists(movies_path):
        return {
            "success": False,
            "error": f"No TMDB CSV found in {TMDB_DIR}. Please place tmdb_5000_movies.csv there.",
            "tmdb_dir": TMDB_DIR
        }

    total_rows_in_csv = count_csv_rows(movies_path)
    credits_map = load_credits(credits_path) if os.path.exists(credits_path) else {}

    imported_count = 0
    skipped_count = 0
    rows_read = 0

    # Enable batch mode to eliminate disk writes per movie
    target_db.embedded_graph.batch_mode = True
    target_db.embedded_mongo.batch_mode = True

    try:
        with open(movies_path, mode="r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i < offset:
                    continue

                if imported_count >= limit:
                    break

                rows_read += 1
                try:
                    m_id = str(row.get("id") or i + 1)
                    title = (row.get("title") or row.get("original_title", "")).strip()
                    if not title:
                        skipped_count += 1
                        continue

                    vote_count = int(float(row.get("vote_count", 0) or 0))
                    if vote_count < 10:
                        skipped_count += 1
                        continue

                    overview = row.get("overview", "")
                    release_date = row.get("release_date", "")
                    year = int(release_date.split("-")[0]) if release_date and release_date.split("-")[0].isdigit() else 2020
                    runtime_raw = row.get("runtime", "0") or "0"
                    try:
                        runtime = f"{int(float(runtime_raw))} min"
                    except Exception:
                        runtime = "120 min"

                    vote_avg = round(float(row.get("vote_average", 6.0) or 6.0), 1)

                    genres_raw = safe_parse_json(row.get("genres", "[]"))
                    genres = [g["name"] for g in genres_raw if isinstance(g, dict) and "name" in g]
                    if not genres:
                        genres = ["Drama"]

                    movie_credit = credits_map.get(m_id, {})
                    director = movie_credit.get("director") or "Unknown Director"
                    actors = movie_credit.get("actors", ["Lead Cast"])

                    poster_path = row.get("poster_path", "")
                    if poster_path and poster_path.strip():
                        poster = f"https://image.tmdb.org/t/p/w500{poster_path.strip()}"
                    else:
                        genre_key = genres[0] if genres else "Drama"
                        poster = GENRE_POSTERS.get(genre_key, GENRE_POSTERS.get("Drama", ""))

                    movie_doc = {
                        "id": f"tmdb_{m_id}",
                        "title": title,
                        "year": year,
                        "runtime": runtime,
                        "director": director,
                        "genres": genres,
                        "actors": actors,
                        "rating": vote_avg,
                        "votes": vote_count,
                        "poster": poster,
                        "plot": overview or "An acclaimed cinematic experience."
                    }

                    # Upsert in MongoDB
                    existing = target_db.movies.find_one({"id": movie_doc["id"]})
                    if existing:
                        target_db.movies.update_one({"id": movie_doc["id"]}, {"$set": movie_doc})
                    else:
                        target_db.movies.insert_one(movie_doc)

                    # Sync into Graph (Neo4j if connected + embedded graph)
                    target_db.sync_movie_to_graph(movie_doc)
                    imported_count += 1

                except Exception as e:
                    logger.warning(f"Row {i} skipped: {e}")
                    skipped_count += 1
                    continue
    finally:
        # Re-enable auto-save and write once
        target_db.embedded_graph.batch_mode = False
        target_db.embedded_mongo.batch_mode = False
        target_db.embedded_graph.save()
        target_db.embedded_mongo.save()

    next_offset = offset + rows_read
    has_more = next_offset < total_rows_in_csv

    try:
        total_in_db = target_db.movies.count_documents({}) if target_db.mongo_connected else len(target_db.embedded_mongo.movies.find({}))
    except Exception:
        total_in_db = imported_count

    return {
        "success": True,
        "imported_count": imported_count,
        "skipped_count": skipped_count,
        "offset_used": offset,
        "next_offset": next_offset,
        "has_more": has_more,
        "total_csv_rows": total_rows_in_csv,
        "total_in_db": total_in_db,
        "message": f"Imported {imported_count} movies (rows {offset}–{next_offset}). {'More available.' if has_more else 'All rows processed.'}"
    }

if __name__ == "__main__":
    result = import_tmdb_dataset(limit=100, offset=0)
    print(json.dumps(result, indent=2))
