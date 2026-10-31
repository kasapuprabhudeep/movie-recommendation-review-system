import logging
from database import db

logger = logging.getLogger("MovieRecommender")

class MovieRecommender:
    """
    Hybrid Movie Recommendation Engine powered by Graph Traversal
    (Neo4j Cypher queries or embedded graph engine), collaborative filtering,
    and content attribute matching (genres, directors, actors, ratings).
    """

    def __init__(self, database_manager):
        self.db = database_manager

    def get_similar_movies(self, movie_id, top_n=6):
        """
        Recommends movies similar to a target movie using graph relationships:
        shared director, shared actors, shared genres.
        Returns movies with computed score and human-readable explanation.
        """
        movie_id = str(movie_id)
        
        # 1. Try real Neo4j query if connected
        if self.db.neo4j_connected and self.db.neo4j_driver:
            try:
                cypher_query = """
                MATCH (target:Movie {id: $movie_id})
                OPTIONAL MATCH (target)-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(m:Movie)
                OPTIONAL MATCH (target)<-[:ACTED_IN]-(a:Actor)-[:ACTED_IN]->(m)
                OPTIONAL MATCH (target)<-[:DIRECTED]-(d:Director)-[:DIRECTED]->(m)
                WHERE m.id <> target.id AND m IS NOT NULL
                WITH m,
                     COUNT(DISTINCT g) AS shared_genres,
                     COLLECT(DISTINCT g.name) AS genre_names,
                     COUNT(DISTINCT a) AS shared_actors,
                     COLLECT(DISTINCT a.name) AS actor_names,
                     COUNT(DISTINCT d) AS shared_director,
                     COLLECT(DISTINCT d.name) AS director_names
                WHERE (shared_genres > 0 OR shared_actors > 0 OR shared_director > 0)
                WITH m, genre_names, actor_names, director_names,
                     (shared_director * 3.5 + shared_actors * 2.5 + shared_genres * 1.5) AS score
                RETURN m.id AS id,
                       m.title AS title,
                       m.rating AS rating,
                       score,
                       genre_names,
                       actor_names,
                       director_names
                ORDER BY score DESC, m.rating DESC
                LIMIT $top_n
                """
                with self.db.neo4j_driver.session() as session:
                    records = session.run(cypher_query, movie_id=movie_id, top_n=top_n)
                    recs = []
                    for r in records:
                        rec_id = r["id"]
                        movie_doc = self.db.movies.find_one({"id": rec_id}) or {}
                        recs.append({
                            "movie": movie_doc,
                            "score": round(float(r["score"]), 1),
                            "explanation": self._build_similarity_explanation(
                                r["genre_names"], r["actor_names"], r["director_names"]
                            ),
                            "graph_path": {
                                "shared_genres": r["genre_names"],
                                "shared_actors": r["actor_names"],
                                "shared_directors": r["director_names"]
                            }
                        })
                    if recs:
                        return recs
            except Exception as e:
                logger.error(f"Neo4j similarity query failed: {e}. Using embedded graph engine.")

        # 2. Embedded Graph Engine Traversal (Always available)
        return self._get_similar_movies_embedded_graph(movie_id, top_n)

    def _get_similar_movies_embedded_graph(self, movie_id, top_n=6):
        target_node_id = f"movie_{movie_id}"
        graph = self.db.embedded_graph
        target_node = graph.get_node(target_node_id)
        
        target_movie_doc = self.db.movies.find_one({"id": movie_id}) or {}
        if not target_movie_doc and target_node:
            target_movie_doc = target_node.get("properties", {})

        target_genres = set(target_movie_doc.get("genres", []))
        target_actors = set(target_movie_doc.get("actors", []))
        target_director = target_movie_doc.get("director", "")

        candidates = {}
        all_movies = self.db.movies.find({})

        for m in all_movies:
            m_id = str(m.get("id") or m.get("_id"))
            if m_id == movie_id:
                continue

            shared_genres = list(target_genres.intersection(set(m.get("genres", []))))
            shared_actors = list(target_actors.intersection(set(m.get("actors", []))))
            shared_director = [m.get("director")] if target_director and m.get("director") == target_director else []

            score = (len(shared_director) * 3.5) + (len(shared_actors) * 2.5) + (len(shared_genres) * 1.5)
            if score > 0:
                candidates[m_id] = {
                    "movie": m,
                    "score": round(score, 1),
                    "explanation": self._build_similarity_explanation(shared_genres, shared_actors, shared_director),
                    "graph_path": {
                        "shared_genres": shared_genres,
                        "shared_actors": shared_actors,
                        "shared_directors": shared_director
                    }
                }

        # Sort by score desc, then movie rating desc
        ranked = sorted(
            candidates.values(),
            key=lambda x: (x["score"], float(x["movie"].get("rating", 0))),
            reverse=True
        )
        return ranked[:top_n]

    def _build_similarity_explanation(self, genres, actors, directors):
        parts = []
        if directors:
            parts.append(f"Same Director ({', '.join(directors)})")
        if actors:
            parts.append(f"Shared Cast ({', '.join(actors[:2])})")
        if genres:
            parts.append(f"Shared Genre ({', '.join(genres[:2])})")
        if not parts:
            return "Based on popular graph connections"
        return " & ".join(parts)

    def get_user_recommendations(self, user_id=None, top_n=8):
        """
        Personalized Recommendations:
        Combines User-Movie Ratings Graph, Watchlist, Collaborative Filtering,
        and Content Taste Profiling.
        """
        if not user_id:
            # Fallback for anonymous users: highest rated & trending
            all_movies = self.db.movies.find({}, sort=[("rating", -1)], limit=top_n)
            return [{
                "movie": m,
                "score": float(m.get("rating", 4.0)),
                "explanation": "Top rated by the community"
            } for m in all_movies]

        user_id = str(user_id)
        
        # 1. Gather movies this user interacted with (rated or watchlisted)
        user_ratings = self.db.ratings.find({"user_id": user_id})
        user_watchlist = self.db.watchlists.find({"user_id": user_id})

        rated_movie_ids = {str(r["movie_id"]): float(r.get("rating", 0)) for r in user_ratings}
        watchlist_movie_ids = {str(w["movie_id"]) for w in user_watchlist}
        seen_movie_ids = set(rated_movie_ids.keys()).union(watchlist_movie_ids)

        # High-rated movies (rating >= 3.5)
        liked_movie_ids = [mid for mid, r_val in rated_movie_ids.items() if r_val >= 3.5]
        # Include watchlist as positive signal
        for w_mid in watchlist_movie_ids:
            if w_mid not in liked_movie_ids:
                liked_movie_ids.append(w_mid)

        if not liked_movie_ids:
            # User hasn't liked/rated/watchlisted anything yet
            all_movies = self.db.movies.find({}, sort=[("rating", -1)], limit=top_n)
            return [{
                "movie": m,
                "score": float(m.get("rating", 4.0)),
                "explanation": "Trending & critically acclaimed to kick off your watchlist"
            } for m in all_movies]

        # 2. Extract User's Favorite Directors, Genres, and Actors
        preferred_genres = {}
        preferred_directors = {}
        preferred_actors = {}
        liked_movie_titles = {}

        for l_id in liked_movie_ids:
            m_doc = self.db.movies.find_one({"id": l_id})
            if not m_doc:
                continue
            liked_movie_titles[l_id] = m_doc.get("title", "")
            for g in m_doc.get("genres", []):
                preferred_genres[g] = preferred_genres.get(g, 0) + 1
            director = m_doc.get("director")
            if director:
                preferred_directors[director] = preferred_directors.get(director, 0) + 2
            for a in m_doc.get("actors", []):
                preferred_actors[a] = preferred_actors.get(a, 0) + 1

        # 3. Collaborative Filtering via other users' ratings
        collaborative_scores = {}
        collaborative_reasons = {}

        all_ratings = self.db.ratings.find({})
        other_user_ratings = {}
        for r in all_ratings:
            o_uid = str(r["user_id"])
            if o_uid != user_id:
                if o_uid not in other_user_ratings:
                    other_user_ratings[o_uid] = {}
                other_user_ratings[o_uid][str(r["movie_id"])] = float(r.get("rating", 0))

        # Find users with overlapping liked movies
        for o_uid, o_rated in other_user_ratings.items():
            common_likes = [m for m in liked_movie_ids if o_rated.get(m, 0) >= 3.5]
            if common_likes:
                # Other user shares similar taste
                for o_mid, o_rval in o_rated.items():
                    if o_mid not in seen_movie_ids and o_rval >= 3.5:
                        collaborative_scores[o_mid] = collaborative_scores.get(o_mid, 0) + (o_rval * 0.8)
                        anchor_title = liked_movie_titles.get(common_likes[0], "your favorites")
                        collaborative_reasons[o_mid] = f"Viewers who enjoyed '{anchor_title}' also gave this high marks"

        # 4. Content Graph Scoring for unseen movies
        all_movies = self.db.movies.find({})
        scored_candidates = []

        for m in all_movies:
            m_id = str(m.get("id") or m.get("_id"))
            if m_id in seen_movie_ids:
                continue

            # Calculate content match
            genre_score = sum(preferred_genres.get(g, 0) * 1.5 for g in m.get("genres", []))
            director_score = preferred_directors.get(m.get("director"), 0) * 2.5
            actor_score = sum(preferred_actors.get(a, 0) * 1.2 for a in m.get("actors", []))
            base_rating = float(m.get("rating", 0)) * 0.5
            collab_score = collaborative_scores.get(m_id, 0.0)

            total_score = genre_score + director_score + actor_score + base_rating + collab_score

            # Build intuitive explanation
            reasons = []
            if collab_score > 0 and m_id in collaborative_reasons:
                reasons.append(collaborative_reasons[m_id])
            if director_score > 0:
                reasons.append(f"Directed by {m.get('director')} whom you frequently enjoy")
            matching_genres = [g for g in m.get("genres", []) if g in preferred_genres]
            if matching_genres and not reasons:
                reasons.append(f"Matches your favorite genres: {', '.join(matching_genres[:2])}")
            if not reasons:
                reasons.append("High overall rating matching your discovery profile")

            scored_candidates.append({
                "movie": m,
                "score": round(total_score, 1),
                "explanation": reasons[0]
            })

        # Sort descending by score
        scored_candidates.sort(key=lambda x: (x["score"], float(x["movie"].get("rating", 0))), reverse=True)
        return scored_candidates[:top_n]

recommender = MovieRecommender(db)

