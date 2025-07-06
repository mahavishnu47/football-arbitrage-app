# app.py
import os
from datetime import datetime
from typing import Dict, List

import requests
import streamlit as st

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore

# ─────────────── CONFIG ─────────────── #
SPORT = "soccer"
REGIONS = "uk,us,eu,au"
BOOKMAKERS = (
    "williamhill,ladbrokes,bet365,skybet,betfair,bwin,unibet,betvictor,"
    "coral,888sport,betfred,betway,marathonbet,pinnacle,matchbook,"
    "boylesports,10bet,betbright,parimatch,betradar"
)
BASE_STAKE_DEFAULT = 1_000
IST = ZoneInfo("Asia/Kolkata")
CACHE_TTL = 900  # 15 minutes
API_URL = "https://api.the-odds-api.com/v4/sports/{sport}/odds"
NAME_MAP = {"Home": "home", "Draw": "draw", "Away": "away", "1": "home", "X": "draw", "2": "away"}

# ─────────────── HELPERS ─────────────── #
def best_prices(bookmakers: List[Dict]) -> tuple[Dict[str, float], Dict[str, str]]:
    best = {"home": 0.0, "draw": 0.0, "away": 0.0}
    books = {"home": "", "draw": "", "away": ""}
    for bk in bookmakers:
        if not bk["markets"]:
            continue
        for out in bk["markets"][0]["outcomes"]:
            k = NAME_MAP.get(out["name"])
            if k and out["price"] > best[k]:
                best[k], books[k] = out["price"], bk["title"]
    return best, books

def calc_arbitrage(odds: Dict[str, float], total: float) -> Dict | None:
    if any(o <= 0 for o in odds.values()):
        return None
    inv_sum = sum(1 / o for o in odds.values())
    if inv_sum >= 1:
        return None
    stakes = {k: (total / o) / inv_sum for k, o in odds.items()}
    payout = stakes["home"] * odds["home"]
    profit = payout - total
    return {
        "stakes": {k: round(v) for k, v in stakes.items()},
        "total": round(sum(stakes.values())),
        "payout": round(payout),
        "profit": round(profit),
        "roi": round((profit / total) * 100, 2),
    }

@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def fetch_arbs(api_key: str, base_stake: float) -> tuple[List[Dict], str | None]:
    params = {
        "apiKey": api_key,
        "regions": REGIONS,
        "markets": "h2h",
        "oddsFormat": "decimal",
        "bookmakers": BOOKMAKERS,
    }
    try:
        resp = requests.get(API_URL.format(sport=SPORT), params=params, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code
        if code == 401:
            msg = "401 ‑ Unauthorized. The API key is invalid or expired."
        elif code == 429:
            msg = "429 ‑ Rate limit exceeded. Slow down or upgrade your OddsAPI plan."
        elif code == 403:
            msg = "403 ‑ Forbidden. This key may not have soccer access."
        else:
            msg = f"{code} ‑ {e.response.reason}"
        return [], msg
    except requests.exceptions.RequestException as e:
        return [], f"Network error: {e}"

    matches = resp.json()
    arbs: List[Dict] = []
    for m in matches:
        odds, books = best_prices(m["bookmakers"])
        calc = calc_arbitrage(odds, base_stake)
        if not calc:
            continue
        kick_iso = m["commence_time"].replace("Z", "+00:00")
        kick_local = datetime.fromisoformat(kick_iso).astimezone(IST).strftime("%d %b %H:%M")
        arbs.append({
            "match": f'{m["home_team"]} vs {m["away_team"]}',
            "kickoff": kick_local,
            "odds": odds,
            "books": books,
            **calc,
        })
    return arbs, None

# ─────────────── UI START ─────────────── #
st.set_page_config(page_title="MR GLOBAL SPORTS – Arbitrage", layout="wide")

st.markdown("""
<div style="text-align:center">
  <h1 style="margin-bottom:0">MR&nbsp;GLOBAL&nbsp;SPORTS</h1>
  <small>AI Football Arbitrage Platform — Public Display</small>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Controls")
    api_key = st.text_input("OddsAPI Key", type="password", value=os.getenv("ODDS_API_KEY", ""))
    mult = st.radio("Stake Multiplier", [1, 2, 3], horizontal=True, index=0)
    base_stake = st.number_input("Base total stake (£)", 100, 10_000, BASE_STAKE_DEFAULT)
    disclaimer_btn = st.button("Show Disclaimer")
    st.caption("Odds are refreshed every 15 min and cached locally.")

# Disclaimer
if "disclaimer_seen" not in st.session_state:
    st.session_state.disclaimer_seen = False

if disclaimer_btn or not st.session_state.disclaimer_seen:
    with st.expander("📜 Disclaimer — click to read / hide", expanded=True):
        st.markdown("""
> **This app provides AI‑based arbitrage recommendations only.**  
> MR Global Sports does **not** place bets or guarantee winnings.  
> Use of this information is entirely at your own risk.
""")
    st.session_state.disclaimer_seen = True

if not api_key:
    st.warning("Enter a valid OddsAPI key on the left to begin.")
    st.stop()

# Fetch data
with st.spinner("Fetching odds & scanning for arbitrage…"):
    arbs, err = fetch_arbs(api_key, base_stake * mult)

if err:
    st.error(err)
    st.stop()

if not arbs:
    st.info("No arbitrage opportunities right now. Try again later.")
    st.stop()

st.success(f"Found {len(arbs)} arbitrage matches (stake ×{mult})")

# Display each arbitrage opportunity
for arb in arbs:
    head = f'{arb["match"]} — KO {arb["kickoff"]} | ROI {arb["roi"]}%'
    with st.expander(head):
        col1, col2, col3, col4 = st.columns([2, 2, 1, 2])
        col1.markdown("**Outcome**")
        col2.markdown("**Bookmaker**")
        col3.markdown("**Odds**")
        col4.markdown("**Stake (£)**")
        for k, label in zip(["home", "draw", "away"], ["Home Win", "Draw", "Away Win"]):
            c1, c2, c3, c4 = st.columns([2, 2, 1, 2])
            c1.write(label)
            c2.write(arb["books"][k])
            c3.write(arb["odds"][k])
            c4.write(arb["stakes"][k])
        st.divider()
        st.write(
            f'**Total Stake:** £{arb["total"]}    '
            f'**Guaranteed Return:** £{arb["payout"]}    '
            f'**Profit:** £{arb["profit"]}    '
            f'(**ROI:** {arb["roi"]}% )'
        )
