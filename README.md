<<<<<<< HEAD
# ⚽ Football Arbitrage App – Built by [@mahavishnu47](https://github.com/mahavishnu47)

> A public AI-based football arbitrage display system using Streamlit and [OddsAPI](https://the-odds-api.com).  
> Scans odds every 15 minutes from 20+ bookmakers to identify risk-free betting opportunities.

---

## 🧠 What It Does

- Finds **2-way and 3-way arbitrage opportunities** across global football markets
- Uses **odds from 20+ bookmakers** (UK, US, EU, AU regions)
- Calculates:
  - Optimal stake for each outcome
  - Guaranteed return
  - Net profit and ROI

---

## 🖥️ Demo Preview

<img src="https://user-images.githubusercontent.com/mahavishnu47/arbitrage-demo.png" width="800"/>

---

## 📦 Features

- ✅ Real-time arbitrage scanning (15 min refresh)
- ✅ Odds from 20+ bookmakers
- ✅ Match info: teams, kickoff, ROI
- ✅ Responsive UI with Streamlit
- ✅ No login or betting — **recommendation-only**

---

## 🧮 Arbitrage Example

| Outcome        | Bookmaker     | Odds | Stake  |
|----------------|----------------|------|--------|
| Man Utd Win    | William Hill   | 2.30 | £470   |
| Draw           | Ladbrokes      | 3.40 | £320   |
| Liverpool Win  | Betfred        | 3.00 | £310   |

- **Total Stake**: £1,100  
- **Guaranteed Return**: £1,130  
- **Profit**: £30 (ROI = 2.7%)

---

## 🚀 Quickstart (Local)

### 1. Clone the repo

```bash
git clone https://github.com/mahavishnu47/football-arbitrage-app.git
cd football-arbitrage-app

## 2. Create a virtual environment and install dependencies
```bash
uv venv
uv pip install -r requirements.txt

## Run the app
```bash
streamlit run app.py

📜 Disclaimer
This app provides AI-based football arbitrage recommendations only.
No betting is performed by this system.
Gambling decisions and risks are your responsibility.

🧑‍💻 Developed by
Mahavishnu Essakimuthu
GitHub: @mahavishnu47

=======
# football-arbitrage-app
>>>>>>> bc45b6b6aa04fe84a49ae91c06fe3ea6370ff5ec
