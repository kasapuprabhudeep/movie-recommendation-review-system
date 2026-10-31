# 🚀 CineGraph Deployment & Sharing Guide

This guide gives you two easy ways to get a public link to share your Movie Recommendation System:
- **Option 1: Permanent 24/7 Cloud Deployment on Render.com** (Recommended for submissions, portfolios, and permanent sharing).
- **Option 2: Instant 30-Second Public Share Link** (Best for live demos right now from your machine).

---

## 🌟 Option 1: Permanent 24/7 Cloud Deployment (Render.com)

Render hosts your full-stack project for free with HTTPS, providing a permanent URL such as:
`https://movie-recommendation-system.onrender.com`

Because we unified the React frontend and Flask backend, **you only need to deploy ONE single service!**

### Step 1: Push your code to GitHub
1. Go to [github.com/new](https://github.com/new) and create a new repository named `MovieRecommendationSystem` (make it Public).
2. Inside your `MovieRecommendationSystem` folder, double-click:
   ```
   push_to_github.bat
   ```
   Paste your GitHub repository URL (e.g., `https://github.com/<your-username>/MovieRecommendationSystem.git`) when prompted.
   Your code is now securely on GitHub!

### Step 2: Deploy on Render
1. Visit **[dashboard.render.com](https://dashboard.render.com/)** and sign up or log in with GitHub.
2. Click **New +** (top right) ➔ **Web Service**.
3. Select your repository: `MovieRecommendationSystem` and click **Connect**.
4. Configure the settings (most are auto-filled by `render.yaml`):
   - **Name**: `movie-recommendation-system` (or any name you prefer)
   - **Region**: Choose the closest region (e.g., Singapore, Frankfurt, Oregon)
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT`
   - **Plan**: `Free`
5. Click **Create Web Service** at the bottom.

### Step 3: Get Your Shareable Link!
Render will run `./build.sh` (which builds the React frontend and installs backend packages).
Once the build says **"Your service is live"**, Render displays your public URL at the top:
👉 **`https://movie-recommendation-system.onrender.com`**

You can copy and send this link to anyone! It runs 24/7 even when your laptop is turned off.

---

## ⚡ Option 2: Instant 30-Second Public Share Link (Live Tunnel)

If you need a live public link **right now** to show someone immediately while running on your laptop:

1. Start your application locally:
   - Double-click `run_all.bat` (or `start_backend.bat`).
2. Double-click:
   ```
   share_instant_link.bat
   ```
3. A terminal window will open and display an instant public HTTPS link:
   ```
   https://xxxxxx.a.free.pinggy.link
   ```
4. Copy that URL and open it on your phone or send it to anyone!
   *(Note: This link remains active as long as the terminal window and your laptop backend stay running).*

---

## 🗄️ Database in Cloud (Self-Contained vs. Cloud Databases)

### Zero-Configuration Mode (Default)
The project comes with a built-in document and graph fallback engine with all 300+ sample and TMDB movies preserved in `backend/data/`.
When deployed to Render, it runs **completely self-contained** out of the box with zero external database setup required!

### (Optional) Connecting Live Cloud Databases
If your evaluator or vendor requires live cloud MongoDB and Neo4j clusters:
1. **MongoDB Atlas (Free M0 Cluster)**:
   - Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas).
   - In your Render Dashboard ➔ Environment ➔ Add Environment Variable:
     - `MONGO_URI` = `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/movierec?retryWrites=true&w=majority`
2. **Neo4j AuraDB (Free Cloud Graph)**:
   - Create a free AuraDB instance at [neo4j.com/cloud/aura/](https://neo4j.com/cloud/aura/).
   - In your Render Dashboard ➔ Environment ➔ Add Environment Variables:
     - `NEO4J_URI` = `neo4j+s://<dbid>.databases.neo4j.io`
     - `NEO4J_USER` = `neo4j`
     - `NEO4J_PASSWORD` = `<your-auradb-password>`

Once added, the system automatically switches from the embedded engine to the live cloud databases on restart!

