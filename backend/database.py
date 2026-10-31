import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MovieRecDB")

# Environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/movierec")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "movierec")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
MONGO_JSON_FILE = os.path.join(DATA_DIR, "mongo_data.json")
GRAPH_JSON_FILE = os.path.join(DATA_DIR, "graph_data.json")

# ============================================================================
# EMBEDDED DOCUMENT STORE (MongoDB Compatible Fallback)
# ============================================================================

class EmbeddedCollection:
    """Provides a MongoDB-like collection interface over JSON file persistence."""
    def __init__(self, name, parent_store):
        self.name = name
        self.parent = parent_store

    def _get_items(self):
        return self.parent.data.get(self.name, [])

    def find(self, query=None, projection=None, sort=None, limit=0, skip=0):
        query = query or {}
        results = []
        for item in self._get_items():
            match = True
            for k, v in query.items():
                if isinstance(v, dict):
                    item_val = item.get(k)
                    if "$in" in v and item_val not in v["$in"]:
                        match = False
                        break
                    if "$regex" in v:
                        import re
                        options = v.get("$options", "")
                        flags = re.IGNORECASE if "i" in options else 0
                        if not re.search(v["$regex"], str(item_val or ""), flags):
                            match = False
                            break
                    if "$gte" in v and (item_val is None or item_val < v["$gte"]):
                        match = False
                        break
                    if "$lte" in v and (item_val is None or item_val > v["$lte"]):
                        match = False
                        break
                else:
                    if item.get(k) != v:
                        match = False
                        break
            if match:
                doc = dict(item)
                if projection and isinstance(projection, dict):
                    include_keys = [k for k, val in projection.items() if val == 1]
                    if include_keys:
                        doc = {k: doc[k] for k in include_keys if k in doc}
                results.append(doc)

        if sort and isinstance(sort, list):
            for field, direction in reversed(sort):
                reverse = (direction == -1)
                results.sort(key=lambda x: (x.get(field) is None, x.get(field)), reverse=reverse)

        if skip > 0:
            results = results[skip:]
        if limit > 0:
            results = results[:limit]

        return results

    def find_one(self, query=None):
        res = self.find(query=query, limit=1)
        return res[0] if res else None

    def insert_one(self, document):
        doc = dict(document)
        if "_id" not in doc:
            doc["_id"] = str(len(self._get_items()) + 1) + "_" + hex(abs(hash(str(datetime.now()))))[2:8]
        if "id" not in doc:
            doc["id"] = doc["_id"]
        
        items = self._get_items()
        items.append(doc)
        self.parent.data[self.name] = items
        self.parent.save()
        
        class InsertResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return InsertResult(doc["_id"])

    def update_one(self, query, update, upsert=False):
        items = self._get_items()
        matched = False
        for i, item in enumerate(items):
            match = all(item.get(k) == v for k, v in query.items())
            if match:
                matched = True
                if "$set" in update:
                    items[i].update(update["$set"])
                if "$addToSet" in update:
                    for field, val in update["$addToSet"].items():
                        arr = items[i].get(field, [])
                        if not isinstance(arr, list):
                            arr = [arr]
                        if val not in arr:
                            arr.append(val)
                        items[i][field] = arr
                if "$pull" in update:
                    for field, val in update["$pull"].items():
                        arr = items[i].get(field, [])
                        if isinstance(arr, list) and val in arr:
                            arr.remove(val)
                            items[i][field] = arr
                break

        if not matched and upsert:
            new_doc = dict(query)
            if "$set" in update:
                new_doc.update(update["$set"])
            self.insert_one(new_doc)
            return True

        self.parent.data[self.name] = items
        self.parent.save()
        return matched

    def delete_one(self, query):
        items = self._get_items()
        for i, item in enumerate(items):
            match = all(item.get(k) == v for k, v in query.items())
            if match:
                del items[i]
                self.parent.data[self.name] = items
                self.parent.save()
                return True
        return False

    def count_documents(self, query=None):
        return len(self.find(query or {}))


class EmbeddedMongoStore:
    def __init__(self, filepath=MONGO_JSON_FILE):
        self.filepath = filepath
        self.data = {"movies": [], "users": [], "reviews": [], "ratings": [], "watchlists": []}
        self.batch_mode = False
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load mongo JSON file, starting fresh: {e}")

    def save(self):
        if self.batch_mode:
            return
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving mongo JSON file: {e}")

    def __getattr__(self, name):
        if name not in self.data:
            self.data[name] = []
        return EmbeddedCollection(name, self)


# ============================================================================
# EMBEDDED GRAPH ENGINE (Neo4j Compatible Fallback - High Performance)
# ============================================================================

class EmbeddedGraphEngine:
    """High-performance graph engine with in-memory indexes and deferred disk writes."""
    def __init__(self, filepath=GRAPH_JSON_FILE):
        self.filepath = filepath
        self.nodes = {}
        self.edges = []
        self._edge_keys = set()
        self.batch_mode = False
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    self.nodes = content.get("nodes", {})
                    self.edges = content.get("edges", [])
                    self._edge_keys = {
                        (e["source"], e["target"], e["type"]) for e in self.edges
                    }
            except Exception as e:
                logger.warning(f"Could not load graph JSON file: {e}")

    def save(self):
        if self.batch_mode:
            return
        try:
            tmp_path = self.filepath + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump({"nodes": self.nodes, "edges": self.edges}, f, indent=2, default=str)
            os.replace(tmp_path, self.filepath)
        except Exception as e:
            logger.error(f"Error saving graph JSON file: {e}")

    def add_node(self, node_id, label, properties=None):
        properties = properties or {}
        self.nodes[str(node_id)] = {
            "id": str(node_id),
            "label": label,
            "properties": properties
        }
        if not self.batch_mode:
            self.save()

    def add_relationship(self, source_id, target_id, rel_type, properties=None):
        s_id = str(source_id)
        t_id = str(target_id)
        key = (s_id, t_id, rel_type)
        if key in self._edge_keys:
            return  # O(1) duplicate check
        self._edge_keys.add(key)
        self.edges.append({
            "source": s_id,
            "target": t_id,
            "type": rel_type,
            "properties": properties or {}
        })
        if not self.batch_mode:
            self.save()

    def delete_relationship(self, source_id, target_id, rel_type):
        s_id = str(source_id)
        t_id = str(target_id)
        key = (s_id, t_id, rel_type)
        if key in self._edge_keys:
            self._edge_keys.remove(key)
            self.edges = [
                e for e in self.edges 
                if not (e["source"] == s_id and e["target"] == t_id and e["type"] == rel_type)
            ]
            if not self.batch_mode:
                self.save()

    def get_node(self, node_id):
        return self.nodes.get(str(node_id))

    def get_neighbors(self, node_id, rel_type=None, direction="out"):
        node_id = str(node_id)
        results = []
        for edge in self.edges:
            if rel_type and edge["type"] != rel_type:
                continue
            if direction in ("out", "both") and edge["source"] == node_id:
                results.append((self.nodes.get(edge["target"]), edge))
            elif direction in ("in", "both") and edge["target"] == node_id:
                results.append((self.nodes.get(edge["source"]), edge))
        return [r for r in results if r[0] is not None]

    def clear(self):
        self.nodes = {}
        self.edges = []
        self._edge_keys = set()
        self.save()


# ============================================================================
# DATABASE MANAGER (Unified MongoDB + Neo4j Client with Dynamic Auto-Reconnect)
# ============================================================================

class DatabaseManager:
    _instance = None

    def __init__(self):
        self.mongo_client = None
        self.mongo_db = None
        self.mongo_connected = False
        self.embedded_mongo = EmbeddedMongoStore()

        self.neo4j_driver = None
        self.neo4j_connected = False
        self.embedded_graph = EmbeddedGraphEngine()

        self.init_mongodb()
        self.init_neo4j()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DatabaseManager()
        return cls._instance

    def init_mongodb(self):
        try:
            import pymongo
            client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
            client.admin.command('ping')
            self.mongo_client = client
            self.mongo_db = client[MONGO_DB_NAME]
            self.mongo_connected = True
            logger.info(f"Connected to Live MongoDB at {MONGO_URI}")
            return True
        except Exception as e:
            self.mongo_connected = False
            self.mongo_db = self.embedded_mongo
            logger.info(f"Live MongoDB not running ({e}). Using Built-in Document Engine.")
            return False

    def init_neo4j(self):
        """Attempts connection to live Neo4j. Safe to call multiple times."""
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            driver.verify_connectivity()
            self.neo4j_driver = driver
            self.neo4j_connected = True
            logger.info(f"Connected to Live Neo4j at {NEO4J_URI}")
            return True
        except Exception as e:
            self.neo4j_connected = False
            self.neo4j_driver = None
            logger.info(f"Live Neo4j not running ({e}). Using Built-in Graph Engine.")
            return False

    def ensure_neo4j(self):
        """Dynamic check: if not currently connected, try connecting."""
        if not self.neo4j_connected:
            self.init_neo4j()
        return self.neo4j_connected

    @property
    def movies(self):
        return self.mongo_db["movies"] if self.mongo_connected else self.embedded_mongo.movies

    @property
    def users(self):
        return self.mongo_db["users"] if self.mongo_connected else self.embedded_mongo.users

    @property
    def reviews(self):
        return self.mongo_db["reviews"] if self.mongo_connected else self.embedded_mongo.reviews

    @property
    def ratings(self):
        return self.mongo_db["ratings"] if self.mongo_connected else self.embedded_mongo.ratings

    @property
    def watchlists(self):
        return self.mongo_db["watchlists"] if self.mongo_connected else self.embedded_mongo.watchlists

    def sync_movie_to_graph(self, movie):
        """Syncs movie nodes and relationships to Neo4j (via single Cypher) and Embedded Graph."""
        movie_id = str(movie.get("id") or movie.get("_id"))
        title = movie.get("title", "")
        director = movie.get("director", "")
        genres = movie.get("genres", [])
        actors = movie.get("actors", [])
        rating = float(movie.get("rating", 0.0) or 0.0)
        year = int(movie.get("year", 2020) or 2020)

        # 1. Live Neo4j single-query execution
        if self.ensure_neo4j() and self.neo4j_driver:
            try:
                with self.neo4j_driver.session() as session:
                    session.run(
                        """
                        MERGE (m:Movie {id: $id})
                        SET m.title = $title, m.director = $director, m.rating = $rating, m.year = $year
                        FOREACH (dName IN CASE WHEN $director <> '' AND $director <> 'Unknown Director' THEN [$director] ELSE [] END |
                            MERGE (d:Director {name: dName})
                            MERGE (d)-[:DIRECTED]->(m)
                        )
                        FOREACH (gName IN $genres |
                            MERGE (g:Genre {name: gName})
                            MERGE (m)-[:IN_GENRE]->(g)
                        )
                        FOREACH (aName IN $actors |
                            MERGE (a:Actor {name: aName})
                            MERGE (a)-[:ACTED_IN]->(m)
                        )
                        """,
                        id=movie_id, title=title, director=director, rating=rating,
                        year=year, genres=genres, actors=actors[:5]
                    )
            except Exception as e:
                logger.error(f"Error syncing movie to Neo4j: {e}")

        # 2. Maintain embedded graph fallback
        self.embedded_graph.add_node(f"movie_{movie_id}", "Movie", {
            "id": movie_id, "title": title, "director": director, "rating": rating, "year": year
        })
        if director and director != "Unknown Director":
            d_id = f"director_{director.replace(' ', '_').lower()}"
            self.embedded_graph.add_node(d_id, "Director", {"name": director})
            self.embedded_graph.add_relationship(d_id, f"movie_{movie_id}", "DIRECTED")
        for genre in genres:
            g_id = f"genre_{genre.replace(' ', '_').lower()}"
            self.embedded_graph.add_node(g_id, "Genre", {"name": genre})
            self.embedded_graph.add_relationship(f"movie_{movie_id}", g_id, "IN_GENRE")
        for actor in actors[:5]:
            a_id = f"actor_{actor.replace(' ', '_').lower()}"
            self.embedded_graph.add_node(a_id, "Actor", {"name": actor})
            self.embedded_graph.add_relationship(a_id, f"movie_{movie_id}", "ACTED_IN")

    def record_user_rating_in_graph(self, user_id, movie_id, rating_val):
        user_id = str(user_id)
        movie_id = str(movie_id)
        rating_val = float(rating_val)

        if self.ensure_neo4j() and self.neo4j_driver:
            try:
                with self.neo4j_driver.session() as session:
                    session.run(
                        """
                        MERGE (u:User {id: $user_id})
                        MERGE (m:Movie {id: $movie_id})
                        MERGE (u)-[r:RATED]->(m)
                        SET r.rating = $rating
                        """,
                        user_id=user_id, movie_id=movie_id, rating=rating_val
                    )
            except Exception as e:
                logger.error(f"Error recording rating in Neo4j: {e}")

        u_node_id = f"user_{user_id}"
        m_node_id = f"movie_{movie_id}"
        self.embedded_graph.add_node(u_node_id, "User", {"id": user_id})
        self.embedded_graph.add_relationship(u_node_id, m_node_id, "RATED", {"rating": rating_val})

    def record_watchlist_in_graph(self, user_id, movie_id, action="add"):
        user_id = str(user_id)
        movie_id = str(movie_id)

        if self.ensure_neo4j() and self.neo4j_driver:
            try:
                with self.neo4j_driver.session() as session:
                    if action == "add":
                        session.run(
                            """
                            MERGE (u:User {id: $user_id})
                            MERGE (m:Movie {id: $movie_id})
                            MERGE (u)-[:WATCHLISTED]->(m)
                            """,
                            user_id=user_id, movie_id=movie_id
                        )
                    else:
                        session.run(
                            """
                            MATCH (u:User {id: $user_id})-[r:WATCHLISTED]->(m:Movie {id: $movie_id})
                            DELETE r
                            """,
                            user_id=user_id, movie_id=movie_id
                        )
            except Exception as e:
                logger.error(f"Error recording watchlist in Neo4j: {e}")

        u_node_id = f"user_{user_id}"
        m_node_id = f"movie_{movie_id}"
        if action == "add":
            self.embedded_graph.add_node(u_node_id, "User", {"id": user_id})
            self.embedded_graph.add_relationship(u_node_id, m_node_id, "WATCHLISTED")
        else:
            self.embedded_graph.delete_relationship(u_node_id, m_node_id, "WATCHLISTED")

    def get_system_status(self):
        # Auto-check if Neo4j is ready now
        self.ensure_neo4j()

        # Count collections
        if self.mongo_connected:
            try:
                movie_count = self.mongo_db.movies.count_documents({})
                user_count = self.mongo_db.users.count_documents({})
                review_count = self.mongo_db.reviews.count_documents({})
                rating_count = self.mongo_db.ratings.count_documents({})
            except Exception:
                movie_count = len(self.embedded_mongo.movies.find({}))
                user_count = len(self.embedded_mongo.users.find({}))
                review_count = len(self.embedded_mongo.reviews.find({}))
                rating_count = len(self.embedded_mongo.ratings.find({}))
        else:
            movie_count = len(self.embedded_mongo.movies.find({}))
            user_count = len(self.embedded_mongo.users.find({}))
            review_count = len(self.embedded_mongo.reviews.find({}))
            rating_count = len(self.embedded_mongo.ratings.find({}))

        graph_nodes = len(self.embedded_graph.nodes)
        graph_edges = len(self.embedded_graph.edges)

        neo4j_nodes = 0
        neo4j_edges = 0
        if self.neo4j_connected and self.neo4j_driver:
            try:
                with self.neo4j_driver.session() as s:
                    neo4j_nodes = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
                    neo4j_edges = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
            except Exception:
                pass

        return {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "mongodb": {
                "connected": self.mongo_connected,
                "mode": "Live MongoDB Database" if self.mongo_connected else "Built-in Document Engine (Ready)",
                "uri": MONGO_URI
            },
            "neo4j": {
                "connected": self.neo4j_connected,
                "mode": "Live Neo4j Graph Database" if self.neo4j_connected else "Built-in Graph Engine (Ready)",
                "uri": NEO4J_URI,
                "live_nodes": neo4j_nodes,
                "live_relationships": neo4j_edges
            },
            "data_summary": {
                "movies": movie_count,
                "users": user_count,
                "reviews": review_count,
                "ratings": rating_count,
                "graph_nodes": neo4j_nodes if self.neo4j_connected else graph_nodes,
                "graph_relationships": neo4j_edges if self.neo4j_connected else graph_edges
            }
        }

db = DatabaseManager.get_instance()
