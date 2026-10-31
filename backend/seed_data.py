import os
import json
import logging
from database import db

logger = logging.getLogger("MovieRecSeeder")

SAMPLE_MOVIES = [
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
        "poster": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=600&auto=format&fit=crop&q=80",
        "plot": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O."
    },
    {
        "id": "m2",
        "title": "Interstellar",
        "year": 2014,
        "runtime": "169 min",
        "director": "Christopher Nolan",
        "genres": ["Sci-Fi", "Adventure", "Drama"],
        "actors": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain", "Matt Damon"],
        "rating": 8.7,
        "votes": 2000000,
        "poster": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&auto=format&fit=crop&q=80",
        "plot": "When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot, Joseph Cooper, is tasked to pilot a spacecraft along with a team of researchers to find a new planet for humans."
    },
    {
        "id": "m3",
        "title": "The Dark Knight",
        "year": 2008,
        "runtime": "152 min",
        "director": "Christopher Nolan",
        "genres": ["Action", "Crime", "Drama"],
        "actors": ["Christian Bale", "Heath Ledger", "Aaron Eckhart", "Gary Oldman"],
        "rating": 9.0,
        "votes": 2800000,
        "poster": "https://images.unsplash.com/photo-1509281373149-e957c6296406?w=600&auto=format&fit=crop&q=80",
        "plot": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice."
    },
    {
        "id": "m4",
        "title": "Oppenheimer",
        "year": 2023,
        "runtime": "180 min",
        "director": "Christopher Nolan",
        "genres": ["Biography", "Drama", "History"],
        "actors": ["Cillian Murphy", "Emily Blunt", "Matt Damon", "Robert Downey Jr."],
        "rating": 8.9,
        "votes": 750000,
        "poster": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=600&auto=format&fit=crop&q=80",
        "plot": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during World War II."
    },
    {
        "id": "m5",
        "title": "The Matrix",
        "year": 1999,
        "runtime": "136 min",
        "director": "Lana Wachowski",
        "genres": ["Sci-Fi", "Action"],
        "actors": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss", "Hugo Weaving"],
        "rating": 8.7,
        "votes": 2050000,
        "poster": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80",
        "plot": "When a beautiful stranger leads computer hacker Neo to a forbidding underworld, he discovers the shocking truth--the life he knows is the elaborate deception of an evil cyber-intelligence."
    },
    {
        "id": "m6",
        "title": "Pulp Fiction",
        "year": 1994,
        "runtime": "154 min",
        "director": "Quentin Tarantino",
        "genres": ["Crime", "Drama"],
        "actors": ["John Travolta", "Samuel L. Jackson", "Uma Thurman", "Bruce Willis"],
        "rating": 8.9,
        "votes": 2180000,
        "poster": "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=600&auto=format&fit=crop&q=80",
        "plot": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption."
    },
    {
        "id": "m7",
        "title": "Django Unchained",
        "year": 2012,
        "runtime": "165 min",
        "director": "Quentin Tarantino",
        "genres": ["Western", "Drama", "Action"],
        "actors": ["Jamie Foxx", "Christoph Waltz", "Leonardo DiCaprio", "Samuel L. Jackson"],
        "rating": 8.5,
        "votes": 1650000,
        "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop&q=80",
        "plot": "With the help of a German bounty-hunter, a freed slave sets out to rescue his wife from a brutal Mississippi plantation owner."
    },
    {
        "id": "m8",
        "title": "Inglourious Basterds",
        "year": 2009,
        "runtime": "153 min",
        "director": "Quentin Tarantino",
        "genres": ["War", "Drama", "Adventure"],
        "actors": ["Brad Pitt", "Christoph Waltz", "Michael Fassbender", "Eli Roth"],
        "rating": 8.4,
        "votes": 1540000,
        "poster": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=600&auto=format&fit=crop&q=80",
        "plot": "In Nazi-occupied France during World War II, a plan to assassinate Nazi leaders by a group of Jewish U.S. soldiers coincides with a theatre owner's vengeful plans for the same."
    },
    {
        "id": "m9",
        "title": "Dune: Part Two",
        "year": 2024,
        "runtime": "166 min",
        "director": "Denis Villeneuve",
        "genres": ["Sci-Fi", "Adventure", "Action"],
        "actors": ["Timothée Chalamet", "Zendaya", "Rebecca Ferguson", "Javier Bardem"],
        "rating": 8.6,
        "votes": 480000,
        "poster": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600&auto=format&fit=crop&q=80",
        "plot": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family."
    },
    {
        "id": "m10",
        "title": "Blade Runner 2049",
        "year": 2017,
        "runtime": "164 min",
        "director": "Denis Villeneuve",
        "genres": ["Sci-Fi", "Mystery", "Drama"],
        "actors": ["Ryan Gosling", "Harrison Ford", "Ana de Armas", "Sylvia Hoeks"],
        "rating": 8.0,
        "votes": 620000,
        "poster": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600&auto=format&fit=crop&q=80",
        "plot": "Young Blade Runner K's discovery of a long-buried secret leads him to track down former Blade Runner Rick Deckard, who's been missing for thirty years."
    },
    {
        "id": "m11",
        "title": "Arrival",
        "year": 2016,
        "runtime": "116 min",
        "director": "Denis Villeneuve",
        "genres": ["Sci-Fi", "Drama", "Mystery"],
        "actors": ["Amy Adams", "Jeremy Renner", "Forest Whitaker", "Michael Stuhlbarg"],
        "rating": 7.9,
        "votes": 740000,
        "poster": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=600&auto=format&fit=crop&q=80",
        "plot": "A linguist works with the military to communicate with alien lifeforms after twelve mysterious spacecraft appear around the world."
    },
    {
        "id": "m12",
        "title": "Parasite",
        "year": 2019,
        "runtime": "132 min",
        "director": "Bong Joon Ho",
        "genres": ["Thriller", "Drama", "Comedy"],
        "actors": ["Song Kang-ho", "Lee Sun-kyun", "Cho Yeo-jeong", "Choi Woo-shik"],
        "rating": 8.5,
        "votes": 910000,
        "poster": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop&q=80",
        "plot": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan."
    },
    {
        "id": "m13",
        "title": "Memories of Murder",
        "year": 2003,
        "runtime": "132 min",
        "director": "Bong Joon Ho",
        "genres": ["Crime", "Drama", "Mystery"],
        "actors": ["Song Kang-ho", "Kim Sang-kyung", "Roe-ha Kim", "Song Jae-ho"],
        "rating": 8.1,
        "votes": 210000,
        "poster": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=600&auto=format&fit=crop&q=80",
        "plot": "In a small Korean province in 1986, two detectives struggle with the case of multiple young women being found raped and murdered by an unknown culprit."
    },
    {
        "id": "m14",
        "title": "The Shawshank Redemption",
        "year": 1994,
        "runtime": "142 min",
        "director": "Frank Darabont",
        "genres": ["Drama"],
        "actors": ["Tim Robbins", "Morgan Freeman", "Bob Gunton", "William Sadler"],
        "rating": 9.3,
        "votes": 2900000,
        "poster": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600&auto=format&fit=crop&q=80",
        "plot": "Over the course of several years, two convicts form a friendship, seeking consolation and, eventually, redemption through basic compassion."
    },
    {
        "id": "m15",
        "title": "Spirited Away",
        "year": 2001,
        "runtime": "125 min",
        "director": "Hayao Miyazaki",
        "genres": ["Animation", "Adventure", "Fantasy"],
        "actors": ["Rumi Hiiragi", "Miyu Irino", "Mari Natsuki", "Takashi Naito"],
        "rating": 8.6,
        "votes": 840000,
        "poster": "https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=600&auto=format&fit=crop&q=80",
        "plot": "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits, and where humans are changed into beasts."
    }
]

SAMPLE_USERS = [
    {
        "id": "u1",
        "username": "alex_reviewer",
        "password": "alex123",
        "name": "Alex Johnson",
        "email": "alex@example.com",
        "bio": "Film enthusiast with a deep love for Nolan and Denis Villeneuve's cinematic universes."
    },
    {
        "id": "u2",
        "username": "sarah_cinephile",
        "password": "sarah123",
        "name": "Sarah Miller",
        "email": "sarah@example.com",
        "bio": "Screenwriter and movie lover obsessed with Tarantino dialogues and South Korean thrillers."
    },
    {
        "id": "u3",
        "username": "david_film",
        "password": "david123",
        "name": "David Chen",
        "email": "david@example.com",
        "bio": "Sci-Fi nerd and classic 90s cinema collector."
    },
    {
        "id": "u4",
        "username": "demo_user",
        "password": "demo123",
        "name": "Demo User",
        "email": "demo@example.com",
        "bio": "Default guest tester exploring the graph recommendation features."
    }
]

SAMPLE_RATINGS = [
    # Alex: loves Nolan Sci-Fi
    {"id": "r1", "user_id": "u1", "username": "alex_reviewer", "movie_id": "m1", "rating": 5.0},
    {"id": "r2", "user_id": "u1", "username": "alex_reviewer", "movie_id": "m2", "rating": 5.0},
    {"id": "r3", "user_id": "u1", "username": "alex_reviewer", "movie_id": "m3", "rating": 4.5},
    {"id": "r4", "user_id": "u1", "username": "alex_reviewer", "movie_id": "m4", "rating": 4.5},
    {"id": "r5", "user_id": "u1", "username": "alex_reviewer", "movie_id": "m9", "rating": 4.0},

    # Sarah: loves Tarantino and Bong Joon Ho
    {"id": "r6", "user_id": "u2", "username": "sarah_cinephile", "movie_id": "m6", "rating": 5.0},
    {"id": "r7", "user_id": "u2", "username": "sarah_cinephile", "movie_id": "m7", "rating": 4.5},
    {"id": "r8", "user_id": "u2", "username": "sarah_cinephile", "movie_id": "m8", "rating": 4.5},
    {"id": "r9", "user_id": "u2", "username": "sarah_cinephile", "movie_id": "m12", "rating": 5.0},
    {"id": "r10", "user_id": "u2", "username": "sarah_cinephile", "movie_id": "m13", "rating": 4.5},

    # David: Sci-Fi and classics
    {"id": "r11", "user_id": "u3", "username": "david_film", "movie_id": "m1", "rating": 4.5},
    {"id": "r12", "user_id": "u3", "username": "david_film", "movie_id": "m5", "rating": 5.0},
    {"id": "r13", "user_id": "u3", "username": "david_film", "movie_id": "m10", "rating": 4.5},
    {"id": "r14", "user_id": "u3", "username": "david_film", "movie_id": "m11", "rating": 4.0},
    {"id": "r15", "user_id": "u3", "username": "david_film", "movie_id": "m14", "rating": 5.0},

    # Demo user
    {"id": "r16", "user_id": "u4", "username": "demo_user", "movie_id": "m1", "rating": 5.0},
    {"id": "r17", "user_id": "u4", "username": "demo_user", "movie_id": "m5", "rating": 4.5}
]

SAMPLE_REVIEWS = [
    {
        "id": "rev1",
        "user_id": "u1",
        "username": "alex_reviewer",
        "movie_id": "m1",
        "title": "Mind-bending masterpiece that redefines sci-fi cinema",
        "content": "Christopher Nolan crafted an intricate dream labyrinth with breathtaking visuals and Hans Zimmer's iconic score. The ending spinning totem still keeps me thinking.",
        "rating": 5.0,
        "created_at": "2026-10-15T14:20:00"
    },
    {
        "id": "rev2",
        "user_id": "u1",
        "username": "alex_reviewer",
        "movie_id": "m2",
        "title": "An emotional journey across the cosmos",
        "content": "Interstellar blends high-concept gravitational physics with raw human emotion. Matthew McConaughey's performance in the video message scene is unforgettable.",
        "rating": 5.0,
        "created_at": "2026-10-18T10:15:00"
    },
    {
        "id": "rev3",
        "user_id": "u2",
        "username": "sarah_cinephile",
        "movie_id": "m6",
        "title": "Sharp dialogue and non-linear brilliance",
        "content": "Pulp Fiction changed 90s cinema forever. The banter between Vincent Vega and Jules Winnfield is legendary, and Samuel L. Jackson gives a career-defining performance.",
        "rating": 5.0,
        "created_at": "2026-10-20T18:45:00"
    },
    {
        "id": "rev4",
        "user_id": "u2",
        "username": "sarah_cinephile",
        "movie_id": "m12",
        "title": "A flawless social satire thriller",
        "content": "Bong Joon Ho masterfully balances sharp black comedy with chilling class tension. Every frame and set piece is meticulously designed with symbolic architecture.",
        "rating": 5.0,
        "created_at": "2026-10-22T09:30:00"
    },
    {
        "id": "rev5",
        "user_id": "u3",
        "username": "david_film",
        "movie_id": "m5",
        "title": "The pinnacle of cyberpunk action and philosophy",
        "content": "Bullet time, green digital rain, and profound existential questions. The Matrix is as groundbreaking today as it was in 1999.",
        "rating": 5.0,
        "created_at": "2026-10-24T12:00:00"
    }
]

SAMPLE_WATCHLISTS = [
    {"id": "w1", "user_id": "u1", "movie_id": "m9", "added_at": "2026-10-25T11:00:00"},
    {"id": "w2", "user_id": "u1", "movie_id": "m10", "added_at": "2026-10-26T15:30:00"},
    {"id": "w3", "user_id": "u2", "movie_id": "m4", "added_at": "2026-10-26T16:00:00"},
    {"id": "w4", "user_id": "u4", "movie_id": "m2", "added_at": "2026-10-27T08:00:00"},
    {"id": "w5", "user_id": "u4", "movie_id": "m9", "added_at": "2026-10-27T09:15:00"}
]

def seed_database(target_db=None):
    """Populates MongoDB and Neo4j graph stores with sample movies, users, ratings, and reviews."""
    target_db = target_db or db
    logger.info("Starting database seeding...")

    # Clear existing data in embedded stores
    target_db.embedded_mongo.data = {
        "movies": [],
        "users": [],
        "reviews": [],
        "ratings": [],
        "watchlists": []
    }
    target_db.embedded_graph.clear()

    # Clear live MongoDB if connected
    if target_db.mongo_connected and target_db.mongo_db is not None:
        try:
            target_db.mongo_db.movies.delete_many({})
            target_db.mongo_db.users.delete_many({})
            target_db.mongo_db.reviews.delete_many({})
            target_db.mongo_db.ratings.delete_many({})
            target_db.mongo_db.watchlists.delete_many({})
            logger.info("Cleared live MongoDB collections.")
        except Exception as e:
            logger.warning(f"Could not clear live MongoDB collections: {e}")

    # Clear live Neo4j if connected
    if target_db.neo4j_connected and target_db.neo4j_driver is not None:
        try:
            with target_db.neo4j_driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            logger.info("Cleared live Neo4j graph nodes & relationships.")
        except Exception as e:
            logger.warning(f"Could not clear live Neo4j: {e}")

    # 1. Seed Movies (and sync to Graph)
    for m in SAMPLE_MOVIES:
        target_db.movies.insert_one(m)
        target_db.sync_movie_to_graph(m)
    logger.info(f"Seeded {len(SAMPLE_MOVIES)} movies.")

    # 2. Seed Users
    for u in SAMPLE_USERS:
        target_db.users.insert_one(u)
    logger.info(f"Seeded {len(SAMPLE_USERS)} users.")

    # 3. Seed Ratings (and record in Graph)
    for r in SAMPLE_RATINGS:
        target_db.ratings.insert_one(r)
        target_db.record_user_rating_in_graph(r["user_id"], r["movie_id"], r["rating"])
    logger.info(f"Seeded {len(SAMPLE_RATINGS)} ratings.")

    # 4. Seed Reviews
    for rev in SAMPLE_REVIEWS:
        target_db.reviews.insert_one(rev)
    logger.info(f"Seeded {len(SAMPLE_REVIEWS)} reviews.")

    # 5. Seed Watchlists (and record in Graph)
    for w in SAMPLE_WATCHLISTS:
        target_db.watchlists.insert_one(w)
        target_db.record_watchlist_in_graph(w["user_id"], w["movie_id"], action="add")
    logger.info(f"Seeded {len(SAMPLE_WATCHLISTS)} watchlist entries.")

    status = target_db.get_system_status()
    logger.info(f"Seeding completed successfully: {json.dumps(status['data_summary'], indent=2)}")
    return status

if __name__ == "__main__":
    seed_database()

