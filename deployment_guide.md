# 🌍 How to Share Your Job Portal

Since your app uses **Playwright** (headless browser) and a **Local Database**, standard "1-click" hosting (like Streamlit Cloud) won't work. Here are your two best options:

---

## 🚀 Option 1: Instant Share (Temporary)
**Best for**: Showing friends right now.
**Requirement**: Your laptop must stay ON and connected to the internet.

1.  **Ensure Streamlit is running** on your mac (Port 8501).
2.  Open a **new terminal** window/tab.
3.  Run this command:
    ```bash
    npx localtunnel --port 8501
    ```
4.  It will give you a URL like `https://salty-dog-42.localtunnel.me`.
5.  **Send this URL to your friends!**
    *   *Note*: When they first open it, they might see a "Click to Continue" warning page.

---

## 🏗️ Option 2: Permanent Hosting (Docker)
**Best for**: Essential 24/7 availability.
**Provider**: [Render.com](https://render.com) (Has a good free/cheap tier for Docker).

### Steps:
1.  **Push your code to GitHub** (You already did this!).
2.  **Sign up for Render.com**.
3.  Click **New +** -> **Web Service**.
4.  Connect your GitHub Repo.
5.  **Runtime**: Select **Docker**.
6.  **Instance Type**: You need at least **1GB - 2GB RAM** for Chrome/Playwright. The "Free" tier might crash. Recommended: **Starter** ($7/mo).
7.  **Environment Variables**:
    *   Add any API keys if you have them (e.g., `ADZUNA_APP_ID`).
8.  **Deploy!**
    *   Render will read your `Dockerfile`, build the image (installing Chrome), and host it.

---

## 🐳 Docker Local Testing (Advanced)
If you want to verify the Docker build locally before deploying:

1.  **Build**:
    ```bash
    docker build -t job-portal . -f frontend/Dockerfile
    # Note: You have two Dockerfiles. You might need a merged one for single-container deployment.
    # Currently, your setup separates Backend and Frontend.
    # For Render, you typically deploy the BACKEND and FRONTEND as two separate services, or use a "Monolith" Dockerfile (advanced).
    ```

**Recommendation**: Stick to **Option 1 (Localtunnel)** for today!
