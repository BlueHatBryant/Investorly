# 📊 Investorly — Real-Time Stock Dashboard

Investorly is a powerful, interactive dashboard built with Streamlit that allows you to monitor stock performance, news sentiment, and get alerts via Discord if any of your favorite stocks move ±5% in a day.

---

## 🚀 Features

- 🔍 Track top 100 US stocks or any custom ticker
- ⭐ Add/remove favorite stocks to monitor regularly
- 📈 Intraday (5-min) and 1-month historical charts
- 💸 Earnings, dividend, and analyst ratings
- 🧠 News sentiment analysis
- 📢 Discord notifications for major price swings
- 🧰 Settings panel for webhook configuration

---

## 📦 Docker Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/bluehatbryant/investorly.git
cd investorly
```
2. Build the Docker image
```bash
Copy
Edit
docker build -t investorly .
```
3. Run the container
```bash 
Copy
Edit
docker run -d \
  -p 8501:8501 \
  --name investorly \
  --restart unless-stopped \
  investorly
```
Open your browser and go to: http://localhost:8501

🧪 Check if Investorly is Running
After deploying (locally or remotely):

```bash
Copy
Edit
curl http://localhost:8501/_stcore/health
```
Expected result:

```json
Copy
Edit
{"status":"ok"}
```
If using DockerHub:

```bash
Copy
Edit
docker pull bluehatbryant/investorly:latest
docker run -d -p 8501:8501 bluehatbryant/investorly
```
⚙️ Settings Panel
Go to the Settings tab in the sidebar to:

Add your Discord Webhook URL

Send a test notification

The app will send alerts if any favorite stock changes by 5% or more in a day.

📁 File Structure
bash
Copy
Edit
investorly/
├── app.py               # Streamlit application
├── Dockerfile           # For containerization
├── requirements.txt     # Python dependencies
├── favorites.json       # User-selected favorites
├── settings.json        # Discord webhook configuration

📜 License
MIT — free to use and modify.