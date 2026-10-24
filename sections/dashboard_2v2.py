"""Page Streamlit autonome pour les CSV issus de analyze_2v2.py.

Exécution : streamlit run dashboard_2v2.py
Dépendances : streamlit pandas numpy
"""
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Rocket League | Analyse 2v2", page_icon="🚗", layout="wide")

RANKS = ["bronze", "silver", "gold", "platinum", "diamond", "champion", "grand_champion", "supersonic_legend", "unknown"]
LABELS = {"bronze":"Bronze", "silver":"Argent", "gold":"Or", "platinum":"Platine", "diamond":"Diamant", "champion":"Champion", "grand_champion":"Grand Champion", "supersonic_legend":"SSL", "unknown":"Inconnu"}
METRICS = {
    "goals":"Buts / match", "shots":"Tirs / match", "assists":"Passes décisives / match",
    "saves":"Arrêts / match", "score":"Score / match",
    "speed_mean_uu_s":"Vitesse moyenne (uu/s)",
    "distance_traveled_uu":"Distance parcourue (uu)",
    "distance_to_ball_mean_uu":"Distance au ballon (uu)",
    "distance_to_teammate_mean_uu":"Distance au coéquipier (uu)",
    "height_mean_uu":"Hauteur moyenne (uu)",
    "airtime_percent":"Temps en l'air (%)",
    "time_own_half_percent":"Temps dans son camp (%)",
}
BOOST = ("boost_mean", "boost_low_percent", "boost_spent_estimated")

@st.cache_data(show_spinner=False)
def load_csv(path: str, modified: float) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)

st.title("🚗 Rocket League — Analyse des rangs en 2v2")
st.caption("Comparaison par rang individuel · Une observation = un joueur dans un match")

candidates = [Path("data/analyse_2v2"), Path("data/analyses_2v2"), Path("analyses_2v2"), Path("analyses_2v2_corrige")]
base = next((p for p in candidates if (p / "players_all.csv").is_file()), None)
if base is None:
    st.error("Impossible de trouver players_all.csv. Dossier attendu : data/analyse_2v2/ (ou data/analyses_2v2/).")
    st.code("data/\n└── analyse_2v2/\n    ├── players_all.csv\n    ├── averages_by_rank.csv\n    └── errors.csv")
    st.stop()

try:
    csv_path = base / "players_all.csv"
    df = load_csv(str(csv_path), csv_path.stat().st_mtime).copy()
except Exception as exc:
    st.error(f"Erreur de lecture : {exc}")
    st.stop()

required = {"replay_id", "rank_group", "player_name"}
missing = required - set(df.columns)
if missing:
    st.error(f"Colonnes absentes de players_all.csv : {', '.join(sorted(missing))}")
    st.stop()

for col in METRICS:
    if col in df:
        df[col] = pd.to_numeric(df[col], errors="coerce")
for col in BOOST:
    if col in df:
        df[col] = pd.to_numeric(df[col], errors="coerce")
df["rank_group"] = df["rank_group"].fillna("unknown").astype(str)
df["rank_label"] = df["rank_group"].map(LABELS).fillna(df["rank_group"])
if "spatial_available" in df:
    df["spatial_available"] = df["spatial_available"].astype(str).str.lower().eq("true")
else:
    df["spatial_available"] = False

available = [r for r in RANKS if r in set(df["rank_group"])]
available += sorted(set(df["rank_group"]) - set(available))
st.sidebar.header("Filtres")
selected = st.sidebar.multiselect("Rangs", available, default=available, format_func=lambda x: LABELS.get(x, x))
min_n = st.sidebar.number_input("Effectif minimum par rang pour les moyennes", min_value=1, max_value=10000, value=10)
spatial_only = st.sidebar.checkbox("Uniquement les observations avec données spatiales", value=False)

filtered = df[df["rank_group"].isin(selected)].copy()
if spatial_only:
    filtered = filtered[filtered["spatial_available"]]
if filtered.empty:
    st.info("Aucune observation ne correspond aux filtres.")
    st.stop()

n_players = filtered["player_id"].dropna().nunique() if "player_id" in filtered else None
k1, k2, k3, k4 = st.columns(4)
k1.metric("Observations joueur-match", f"{len(filtered):,}".replace(",", " "))
k2.metric("Replays distincts", filtered["replay_id"].nunique())
k3.metric("Joueurs distincts", n_players if n_players is not None else "—")
k4.metric("Observations spatiales", int(filtered["spatial_available"].sum()))

if any(c in filtered for c in BOOST):
    boost_counts = {c: int(filtered[c].notna().sum()) for c in BOOST if c in filtered}
    if boost_counts and max(boost_counts.values()) == 0:
        st.warning("Statistiques de boost indisponibles : elles ne sont pas utilisées dans les comparaisons.")

counts = filtered.groupby("rank_group").size().reindex(available, fill_value=0)
counts = counts[counts > 0]
st.subheader("Répartition des observations par rang")
st.bar_chart(
    pd.DataFrame({
        "Rang": [LABELS.get(r, r) for r in counts.index],
        "Observations": counts.values
    }),
    x="Rang",
    y="Observations",
    sort=False
)
st.caption("Il s'agit d'observations joueur-match, pas nécessairement de joueurs différents. Plusieurs joueurs proviennent du même replay.")

st.subheader("Comparer les statistiques")
metrics_available = [c for c in METRICS if c in filtered and filtered[c].notna().any()]
if not metrics_available:
    st.warning("Aucune métrique exploitable dans le CSV.")
else:
    metric = st.selectbox("Indicateur", metrics_available, format_func=lambda c: METRICS[c])
    stats = filtered.groupby("rank_group")[metric].agg(["mean", "median", "count", "std"])
    stats = stats.reindex([r for r in available if r in stats.index]).dropna(subset=["mean"])
    excluded = stats[stats["count"] < min_n]
    eligible = stats[stats["count"] >= min_n]
    if not excluded.empty:
        st.info("Rangs exclus du graphique des moyennes (effectif insuffisant) : " + ", ".join(f"{LABELS.get(r, r)} (n={int(row['count'])})" for r, row in excluded.iterrows()))
    if eligible.empty:
        st.warning("Aucun rang ne satisfait le seuil d'effectif. Réduis-le dans les filtres.")
    else:
        chart_data = pd.DataFrame({METRICS[metric]: eligible["mean"].values}, index=[LABELS.get(r, r) for r in eligible.index])
        st.bar_chart(
    chart_data.reset_index().rename(columns={"index": "Rang"}),
    x="Rang",
    y=METRICS[metric],
    sort=False
)
    display = stats.rename(columns={"mean":"Moyenne", "median":"Médiane", "count":"Observations valides", "std":"Écart-type"}).copy()
    display.index = [LABELS.get(r, r) for r in display.index]
    st.dataframe(display.round(2), use_container_width=True)
    if metric in ("distance_traveled_uu", "score", "goals", "shots", "assists", "saves"):
        st.caption("Attention : les statistiques par match peuvent dépendre de la durée du replay ; elles ne sont pas normalisées par minute.")

st.subheader("Qualité des données")
quality = filtered.groupby("rank_group").agg(observations=("replay_id", "size"), replays=("replay_id", "nunique"), spatial=("spatial_available", "sum"))
quality["spatial_pct"] = (100 * quality["spatial"] / quality["observations"]).round(1)
quality.index = [LABELS.get(r, r) for r in quality.index]
st.dataframe(quality.rename(columns={"observations":"Observations", "replays":"Replays", "spatial":"Avec spatial", "spatial_pct":"Spatial (%)"}), use_container_width=True)

st.subheader("Explorer les observations")
search = st.text_input("Rechercher un joueur", placeholder="Nom du joueur")
shown = filtered
if search:
    shown = shown[shown["player_name"].astype(str).str.contains(search, case=False, regex=False, na=False)]
show_cols = [c for c in ["replay_id", "player_name", "player_id", "rank_label", "team", "goals", "shots", "saves", "assists", "score", "speed_mean_uu_s", "distance_to_ball_mean_uu", "airtime_percent", "spatial_available"] if c in shown]
st.dataframe(shown[show_cols], use_container_width=True, hide_index=True)
st.download_button("Télécharger les observations filtrées (CSV)", shown.drop(columns=["rank_label"], errors="ignore").to_csv(index=False).encode("utf-8-sig"), file_name="rl_2v2_filtered.csv", mime="text/csv")

st.caption("Analyse descriptive uniquement : l'échantillon n'est pas équilibré par rang, les joueurs d'un même replay ne sont pas indépendants et certaines mesures spatiales peuvent nécessiter une validation supplémentaire.")
