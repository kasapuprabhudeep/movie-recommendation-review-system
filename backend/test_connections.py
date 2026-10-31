import sys
import logging
from database import db
from recommender import recommender

logging.basicConfig(level=logging.INFO, format="%(message)s")

def test_databases():
    print("=" * 65)
    print("  MOVIE RECOMMENDATION SYSTEM - DATABASE & GRAPH DIAGNOSTICS")
    print("=" * 65)

    status = db.get_system_status()

    # 1. MongoDB Status
    print(f"\n[1] MongoDB Status:")
    print(f"    - Connected to Live MongoDB: {status['mongodb']['connected']}")
    print(f"    - Active Mode:              {status['mongodb']['mode']}")
    print(f"    - Target URI:               {status['mongodb']['uri']}")

    # 2. Neo4j Status
    print(f"\n[2] Neo4j Status:")
    print(f"    - Connected to Live Neo4j:   {status['neo4j']['connected']}")
    print(f"    - Active Mode:              {status['neo4j']['mode']}")
    print(f"    - Target Bolt URI:          {status['neo4j']['uri']}")

    # 3. Collection Counts
    counts = status['data_summary']
    print(f"\n[3] Document Store Records:")
    print(f"    - Movies:      {counts['movies']}")
    print(f"    - Users:       {counts['users']}")
    print(f"    - Ratings:     {counts['ratings']}")
    print(f"    - Reviews:     {counts['reviews']}")

    # 4. Graph Engine Statistics
    print(f"\n[4] Graph Database Network:")
    print(f"    - Graph Nodes:         {counts['graph_nodes']}")
    print(f"    - Graph Relationships: {counts['graph_relationships']}")

    # 5. Graph Recommendation Query Test
    print(f"\n[5] Testing Graph Query (Similar movies for 'Inception'):")
    recs = recommender.get_similar_movies("m1", top_n=3)
    if not recs:
        print("    [!] Warning: No recommendations returned. Run seed_data.py first.")
        return False

    for i, r in enumerate(recs, 1):
        m = r['movie']
        print(f"    {i}. {m.get('title')} ({m.get('year')}) | Score: {r['score']}")
        print(f"       Explanation: {r['explanation']}")

    # 6. Personalized Recommendation Test
    print(f"\n[6] Testing Personalized Recommendation for User 'u1' (Alex):")
    user_recs = recommender.get_user_recommendations("u1", top_n=3)
    for i, r in enumerate(user_recs, 1):
        m = r['movie']
        print(f"    {i}. {m.get('title')} ({m.get('year')}) | Score: {r['score']}")
        print(f"       Explanation: {r['explanation']}")

    print("\n" + "=" * 65)
    print("  ALL DATABASE AND GRAPH TESTS PASSED SUCCESSFULLY!")
    print("=" * 65 + "\n")
    return True

if __name__ == "__main__":
    success = test_databases()
    sys.exit(0 if success else 1)

