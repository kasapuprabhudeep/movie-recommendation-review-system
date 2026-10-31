import unittest
import json
from app import app
from database import db
from seed_data import seed_database

class APITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        seed_database(db)

    def test_01_status(self):
        res = self.client.get('/api/status')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "online")
        self.assertIn("mongodb", data)
        self.assertIn("neo4j", data)
        self.assertGreaterEqual(data["data_summary"]["movies"], 15)

    def test_02_get_movies(self):
        res = self.client.get('/api/movies')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertGreaterEqual(data["total"], 15)
        self.assertTrue(len(data["movies"]) > 0)

    def test_03_search_movies(self):
        res = self.client.get('/api/movies?search=nolan')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        for m in data["movies"]:
            self.assertIn("Christopher Nolan", m["director"])

    def test_04_genre_filter(self):
        res = self.client.get('/api/movies?genre=Sci-Fi')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        for m in data["movies"]:
            self.assertIn("Sci-Fi", m["genres"])

    def test_05_movie_details(self):
        res = self.client.get('/api/movies/m1')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["movie"]["title"], "Inception")
        self.assertIn("similar", data)
        self.assertGreater(len(data["similar"]), 0)

    def test_06_genres_list(self):
        res = self.client.get('/api/genres')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("Sci-Fi", data["genres"])
        self.assertIn("Drama", data["genres"])

    def test_07_user_auth(self):
        # Login existing
        login_res = self.client.post('/api/users/login', json={
            "username": "demo_user",
            "password": "demo123"
        })
        self.assertEqual(login_res.status_code, 200)
        login_data = json.loads(login_res.data)
        self.assertEqual(login_data["user"]["username"], "demo_user")

        # Register new
        reg_res = self.client.post('/api/users/register', json={
            "username": "tester_qa",
            "password": "passwordQA1",
            "name": "QA Tester",
            "email": "qa@test.com"
        })
        self.assertEqual(reg_res.status_code, 201)

    def test_08_ratings(self):
        rate_res = self.client.post('/api/movies/m3/ratings', json={
            "user_id": "u4",
            "username": "demo_user",
            "rating": 5.0
        })
        self.assertEqual(rate_res.status_code, 200)
        data = json.loads(rate_res.data)
        self.assertEqual(data["user_rating"], 5.0)

    def test_09_reviews(self):
        rev_res = self.client.post('/api/movies/m3/reviews', json={
            "user_id": "u4",
            "username": "demo_user",
            "title": "Outstanding superhero movie",
            "content": "Heath Ledger gave an immortal performance as the Joker.",
            "rating": 5.0
        })
        self.assertEqual(rev_res.status_code, 201)
        data = json.loads(rev_res.data)
        self.assertIn("review", data)

    def test_10_watchlist(self):
        # Add to watchlist
        add_res = self.client.post('/api/watchlist', json={
            "user_id": "u4",
            "movie_id": "m11"
        })
        self.assertIn(add_res.status_code, (200, 201))

        # Get watchlist
        list_res = self.client.get('/api/watchlist/u4')
        self.assertEqual(list_res.status_code, 200)
        data = json.loads(list_res.data)
        movie_ids = [m["id"] for m in data["watchlist"]]
        self.assertIn("m11", movie_ids)

        # Remove from watchlist
        del_res = self.client.delete('/api/watchlist/u4/m11')
        self.assertEqual(del_res.status_code, 200)

    def test_11_recommendations(self):
        # Personalized
        rec_res = self.client.get('/api/recommendations?user_id=u1')
        self.assertEqual(rec_res.status_code, 200)
        data = json.loads(rec_res.data)
        self.assertTrue(len(data["recommendations"]) > 0)
        first_rec = data["recommendations"][0]
        self.assertIn("explanation", first_rec)

        # Graph similar
        sim_res = self.client.get('/api/movies/m1/similar')
        self.assertEqual(sim_res.status_code, 200)
        sim_data = json.loads(sim_res.data)
        self.assertTrue(len(sim_data["similar"]) > 0)

if __name__ == "__main__":
    unittest.main()

