# Deployment Guide for InsightRural

This guide walks you through the deployment process for the **InsightRural** platform.
We will use **Render** for the Python Backend and **Vercel** for the Frontend.

## Prerequisites
1.  **GitHub Account**: You need to push your code to a GitHub repository.
2.  **Groq API Key**: You need this for the AI features.
3.  **Render Account**: Create one at [render.com](https://render.com).
4.  **Vercel Account**: Create one at [vercel.com](https://vercel.com).

---

## Step 1: Prepare the Repository
1.  Initialize a Git repository in your project folder (`IR Final 1.2`) if you haven't already.
2.  Create a `.gitignore` file in the root if missing, and add:
    ```
    __pycache__/
    *.pyc
    .env
    venv/
    node_modules/
    .DS_Store
    insightrural.db
    college/data/*.json  # OPTIONAL: Keep this if you want to ship data, Remove if you want to generate it. Recommendation: KEEP IT.
    ```
3.  **Push the entire project** to a new GitHub repository (e.g., `insightrural-app`).

---

## Step 2: Deploy Backend to Render
1.  Log in to **Render Dashboard**.
2.  Click **New +** -> **Blueprints**.
3.  Connect your GitHub repository.
4.  Render will automatically detect the `render.yaml` file in your repository root.
5.  **Review the Service**:
    *   Name: `insightrural-backend`
    *   Region: Singapore or Frankfurt (closest to India).
    *   Branch: `main` (or master).
6.  **Apply** the blueprint.
7.  **Environment Variables**:
    *   Go to the service settings -> **Environment**.
    *   Add `GROQ_API_KEY`: Paste your key here.
    *   Ensure `PYTHON_VERSION` is set to `3.10.0` (as defined in `render.yaml`).
8.  **Wait for Build**: It may take 5-10 minutes.
9.  **Copy the URL**: Once live, copy the backend URL (e.g., `https://insightrural-backend.onrender.com`).

---

## Step 3: Configure Frontend
1.  The frontend is set to automatically detect if it's running on `localhost`.
2.  If you want to hardcode the production URL:
    *   Open `insightrural-frontend/js/core/state.js`.
    *   Replace the URL in the `else` block with your actual Render URL.
    *   Push this change to GitHub.

---

## Step 4: Deploy Frontend to Vercel
1.  Log in to **Vercel Dashboard**.
2.  Click **Add New...** -> **Project**.
3.  Import your GitHub repository (`insightrural-app`).
4.  **Configure Project**:
    *   **Root Directory**: Click "Edit" and select `insightrural-frontend`. (This folder contains `index.html`).
    *   **Framework Preset**: Other (it's plain HTML/JS).
5.  Click **Deploy**.
6.  Vercel will give you a domain (e.g., `insightrural-app.vercel.app`).

---

## Step 5: Final Check
1.  Open your Vercel URL.
2.  Try the **KEA Predictor** (tests backend API).
3.  Try the **Voice Assistant** (tests backend Websockets/API).
4.  If something fails, check the **Console** (F12) in your browser and the **Logs** in Render.

---

### ⚠️ Important Notes
*   **Database**: The SQLite database (`insightrural.db`) on Render is **ephemeral**. This means if the server restarts (which happens often on the free tier), **new user data will be lost**. The static college data will remain (since it's in JSON files). For a production app, you would need a persistent database like PostgreSQL (Render offers this).
*   **Cold Starts**: The Render Free Tier "sleeps" after inactivity. The first request might take 50 seconds. Keep this in mind.
