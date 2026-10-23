
import streamlit as st
import pandas as pd

from utils.io import load_data
from utils.prep import make_tables
from utils.viz import (
    FEATURES,
    bar_chart,
    distribution_chart,
    map_chart,
    show_feature_analysis,
    dumbbell_chart,
    correlation_heatmap,
)


# ========================================
# SIDEBAR — STUDENT & PROJECT INFORMATION
# ========================================

with st.sidebar:
    st.image("assets/efrei_logo.png", width=150)

    st.title("Student Information")

    st.markdown("---")

    st.subheader("My Profile")

    st.write("**Full Name:** Liam Croguennec")
    st.write("**Program:** Master in Bioinformatics & Data Science")
    st.write("**Year:** 2026")
    st.write("**ID:** 20231675")
    st.write("**Email:** liam.croguennec@efrei.net")

    st.markdown("**LinkedIn:** [My LinkedIn](https://www.linkedin.com/in/liam-croguennec-17904a292/)")
    st.markdown("**GitHub:** [My GitHub](https://github.com/LiamCroguennec)")

    st.markdown("---")

    st.subheader("Project Information")

    st.write("**Course Name:** Data Analysis & Visualization")
    st.write("**Project proposed by:** Prof. Mano Mathew")

    st.markdown(
        "**Professor's LinkedIn / Email:** mano.mathew@efrei.net"
        "[Contact information](https://www.linkedin.com/in/manomathew/)"
    )

    st.markdown("---")

    st.caption("Rocket League Data Storytelling Project")

st.set_page_config(
    page_title="Rocket League Data Storytelling",
    page_icon="🚗",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def get_data():
    df_raw = load_data()
    tables = make_tables(df_raw)
    return df_raw, tables


st.title("Rocket League: What Makes a Winning Team?")
st.caption(
    "Source: RL-xG-Predictor — GitHub — "
    "https://github.com/isaactallack/RL-xG-Predictor"
)

# Chargement des données
try:
    raw, tables = get_data()
except (FileNotFoundError, ValueError) as error:
    st.error(str(error))
    st.stop()

teams = tables["teams"]
comparison = tables["comparison"]
summary = tables["summary"]

# Sidebar : filtres
with st.sidebar:
    st.header("Filters")

    metrics = [
        col for col in comparison["metric"].tolist()
        if col in teams.columns
    ]

    if not metrics:
        st.error("Aucune statistique numérique à afficher.")
        st.stop()

    metric = st.selectbox(
        "Choose a statistic",
        options=metrics,
        index=0,
    )

    result_filter = st.multiselect(
        "Match result",
        options=["Win", "Loss", "Draw"],
        default=["Win", "Loss"],
    )

# Appliquer le filtre de résultat
filtered_teams = teams[teams["result"].isin(result_filter)]

# KPI row
c1, c2, c3 = st.columns(3)

c1.metric(
    "Matches analysed",
    f"{summary['matches']:,}",
)

c2.metric(
    "Team observations",
    f"{summary['teams']:,}",
)

c3.metric(
    "Missing values",
    f"{summary['missing_values']:,}",
)

st.divider()

# Overview
st.header("1. Overview")

st.write(
    "Explore the match data and compare the performance of winning "
    "and losing teams."
)

result_counts = (
    filtered_teams["result"]
    .value_counts()
    .rename_axis("result")
    .reset_index(name="count")
)

if not result_counts.empty:
    st.subheader("Distribution of results")

    st.bar_chart(
        result_counts.set_index("result")["count"]
    )


# 2. Analyse détaillée par catégorie
st.header("2. What distinguishes winning teams?")

st.write(
    "Explore the differences between winning and losing teams "
    "across six aspects of Rocket League gameplay."
)

tabs = st.tabs(list(FEATURES.keys()))

for tab, (category, features) in zip(tabs, FEATURES.items()):
    with tab:
        show_feature_analysis(
            teams=filtered_teams,
            comparison=comparison,
            category=category,
            features=features,
        )

# 3. Positionnement sur le terrain
st.header("3. Field positioning")

st.write(
    "Compare the average presence of winning and losing teams "
    "in the defensive, neutral and offensive thirds."
)

map_chart(filtered_teams)

# 4. Qualité des données
st.header("4. Data Quality & Limitations")

st.write(f"- Matches: {summary['matches']:,}")
st.write(f"- Team observations: {summary['teams']:,}")
st.write(f"- Missing values: {summary['missing_values']:,}")
st.write(f"- Duplicate rows: {summary['duplicate_rows']:,}")

st.info(
    "The dataset contains team-level match statistics, not individual "
    "player statistics. Associations do not prove causation. Some "
    "variables may be unavailable or contain missing values."
)

# 5. Conclusions
st.header("5. Key Insights & Next Steps")

st.markdown(
    """
    - **Attack:** examine whether winning teams tend to generate
      different offensive statistics.
    - **Defense:** investigate differences in shots conceded and
      defensive positioning.
    - **Boost and speed:** explore whether resource management and
      movement statistics differ between results.
    - **Positioning and physical play:** compare field presence and
      demolitions.

    These are questions to investigate, not conclusions established
    before examining the charts.
    """
)


# 6. Comparaison détaillée des gagnants et perdants
st.header("6. What separates winners from losers?")

st.write(
    "Compare the standardized average statistics of winning "
    "and losing teams. Larger gaps indicate stronger descriptive differences."
)

dumbbell_chart(filtered_teams)

# 7. Corrélations entre les statistiques
st.header("7. Gameplay Correlations")

st.write(
    "Explore which gameplay statistics tend to increase or decrease "
    "together across the observed team performances."
)

correlation_heatmap(filtered_teams)
