
import pandas as pd
import plotly.express as px
import streamlit as st


# Variables sélectionnées pour l'analyse
FEATURES = {
    "Attaque": [
        "goals",
        "shots",
        "percentage offensive third",
    ],
    "Défense": [
        "shots_conceded",
        "percentage defensive third",
    ],
    "Gestion du boost": [
        "avg boost amount",
        "amount collected",
        "amount stolen",
    ],
    "Vitesse": [
        "avg speed",
        "percentage supersonic speed",
    ],
    "Positionnement": [
        "avg distance to ball",
        "percentage behind ball",
        "percentage offensive half",
    ],
    "Interactions physiques": [
        "demos inflicted",
        "demos taken",
    ],
}


def bar_chart(comparison, metric):
    """Compare la moyenne d'une statistique entre gagnants et perdants."""

    row = comparison.loc[comparison["metric"] == metric]

    if row.empty or not {"Win", "Loss"}.issubset(row.columns):
        st.warning(f"Données indisponibles pour : {metric}")
        return

    chart_data = pd.DataFrame({
        "Résultat": ["Gagnants", "Perdants"],
        "Moyenne": [
            row["Win"].iloc[0],
            row["Loss"].iloc[0],
        ],
    }).dropna(subset=["Moyenne"])

    if chart_data.empty:
        st.warning("Aucune valeur exploitable pour ce graphique.")
        return

    fig = px.bar(
        chart_data,
        x="Résultat",
        y="Moyenne",
        color="Résultat",
        title=f"Moyenne — {metric}",
        text_auto=".2f",
        color_discrete_map={
            "Gagnants": "#2E8B57",
            "Perdants": "#D95F59",
        },
    )

    fig.update_layout(
        template="plotly_white",
        showlegend=False,
        xaxis_title="Résultat du match",
        yaxis_title="Valeur moyenne",
    )

    st.plotly_chart(fig, use_container_width=True)


def distribution_chart(teams, metric):
    """Compare la distribution d'une statistique selon le résultat."""

    if metric not in teams.columns:
        st.warning(f"Variable absente du jeu de données : {metric}")
        return

    plot_data = teams[
        teams["result"].isin(["Win", "Loss"])
    ].copy()

    plot_data[metric] = pd.to_numeric(
        plot_data[metric],
        errors="coerce",
    )

    plot_data = plot_data.dropna(subset=[metric])

    if plot_data.empty:
        st.warning("Aucune donnée exploitable pour cette statistique.")
        return

    plot_data["Résultat"] = plot_data["result"].map({
        "Win": "Gagnants",
        "Loss": "Perdants",
    })

    fig = px.box(
        plot_data,
        x="Résultat",
        y=metric,
        color="Résultat",
        points="outliers",
        title=f"Distribution — {metric}",
        color_discrete_map={
            "Gagnants": "#2E8B57",
            "Perdants": "#D95F59",
        },
    )

    fig.update_layout(
        template="plotly_white",
        showlegend=False,
        xaxis_title="Résultat du match",
        yaxis_title="Valeur observée",
    )

    st.plotly_chart(fig, use_container_width=True)


def map_chart(teams):
    """Compare le positionnement moyen dans les trois zones du terrain."""

    zone_columns = {
        "Zone défensive": "percentage defensive third",
        "Zone neutre": "percentage neutral third",
        "Zone offensive": "percentage offensive third",
    }

    available_zones = {
        label: col
        for label, col in zone_columns.items()
        if col in teams.columns
    }

    if not available_zones:
        st.warning("Les variables de positionnement sont indisponibles.")
        return

    rows = []

    for result, label in [("Win", "Gagnants"), ("Loss", "Perdants")]:
        subset = teams[teams["result"] == result]

        for zone, col in available_zones.items():
            values = pd.to_numeric(subset[col], errors="coerce")

            rows.append({
                "Résultat": label,
                "Zone": zone,
                "Moyenne": values.mean(),
            })

    chart_data = pd.DataFrame(rows).dropna(subset=["Moyenne"])

    if chart_data.empty:
        st.warning("Aucune donnée de positionnement exploitable.")
        return

    fig = px.bar(
        chart_data,
        x="Zone",
        y="Moyenne",
        color="Résultat",
        barmode="group",
        title="Positionnement moyen sur le terrain",
        color_discrete_map={
            "Gagnants": "#2E8B57",
            "Perdants": "#D95F59",
        },
    )

    fig.update_layout(template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)


def show_feature_analysis(teams, comparison, category, features):
    """Affiche les graphiques des variables d'une catégorie."""

    st.subheader(category)

    available = [
        feature
        for feature in features
        if feature in teams.columns
        and feature in comparison["metric"].values
    ]

    if not available:
        st.info(
            "Aucune des variables sélectionnées n'est disponible "
            "pour cette catégorie."
        )
        return

    for metric in available:
        with st.expander(metric, expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                bar_chart(comparison, metric)

            with col2:
                distribution_chart(teams, metric)


def dumbbell_chart(teams):
    """Compare les moyennes des gagnants et perdants sur une échelle standardisée."""
    import plotly.graph_objects as go

    candidates = [
        "goals",
        "shots",
        "shots_conceded",
        "avg boost amount",
        "amount collected",
        "amount stolen",
        "avg speed",
        "percentage supersonic speed",
        "avg distance to ball",
        "percentage behind ball",
        "percentage offensive third",
        "percentage defensive third",
        "demos inflicted",
        "demos taken",
    ]

    if not {"result"}.issubset(teams.columns):
        st.warning("La colonne result est absente.")
        return

    data = teams[teams["result"].isin(["Win", "Loss"])].copy()
    available = [c for c in candidates if c in data.columns]

    rows = []

    for metric in available:
        data[metric] = pd.to_numeric(data[metric], errors="coerce")
        win = data.loc[data["result"] == "Win", metric].dropna()
        loss = data.loc[data["result"] == "Loss", metric].dropna()

        if len(win) < 2 or len(loss) < 2:
            continue

        pooled_std = data[metric].std()

        if pd.isna(pooled_std) or pooled_std == 0:
            continue

        # Standardisation : permet de comparer des variables
        # qui n'ont pas les mêmes unités.
        overall_mean = data[metric].mean()
        win_z = (win.mean() - overall_mean) / pooled_std
        loss_z = (loss.mean() - overall_mean) / pooled_std

        rows.append({
            "metric": metric,
            "Gagnants": win_z,
            "Perdants": loss_z,
            "Écart": abs(win_z - loss_z),
            "Moyenne gagnants": win.mean(),
            "Moyenne perdants": loss.mean(),
        })

    if not rows:
        st.info(
            "Pas assez de données pour comparer les gagnants "
            "et les perdants. Vérifie les filtres et les valeurs disponibles."
        )
        return

    plot_data = (
        pd.DataFrame(rows)
        .sort_values("Écart", ascending=True)
    )

    fig = go.Figure()

    for _, row in plot_data.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["Perdants"], row["Gagnants"]],
            y=[row["metric"], row["metric"]],
            mode="lines",
            line=dict(color="#B8B8B8", width=2),
            showlegend=False,
            hoverinfo="skip",
        ))

    fig.add_trace(go.Scatter(
        x=plot_data["Perdants"],
        y=plot_data["metric"],
        mode="markers",
        name="Perdants",
        marker=dict(color="#D95F59", size=10),
        customdata=plot_data[["Moyenne perdants"]],
        hovertemplate=(
            "%{y}<br>Perdants : %{customdata[0]:.2f}"
            "<extra></extra>"
        ),
    ))

    fig.add_trace(go.Scatter(
        x=plot_data["Gagnants"],
        y=plot_data["metric"],
        mode="markers",
        name="Gagnants",
        marker=dict(color="#2E8B57", size=10),
        customdata=plot_data[["Moyenne gagnants"]],
        hovertemplate=(
            "%{y}<br>Gagnants : %{customdata[0]:.2f}"
            "<extra></extra>"
        ),
    ))

    fig.add_vline(x=0, line_dash="dash", line_color="gray")

    fig.update_layout(
        title="Gagnants vs perdants : comparaison des statistiques",
        xaxis_title="Moyenne standardisée (écarts-types)",
        yaxis_title="Statistique",
        template="plotly_white",
        height=max(450, len(plot_data) * 34),
        legend_title="Résultat du match",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Les positions sont standardisées pour comparer des variables "
        "d'échelles différentes. Au survol, tu peux voir les moyennes "
        "dans leurs unités d'origine. Un écart descriptif ne prouve "
        "pas que la statistique cause la victoire."
    )


def correlation_heatmap(teams):
    """Affiche les corrélations entre les statistiques de gameplay."""

    candidates = [
        "goals",
        "shots",
        "shots_conceded",
        "goals_conceded",
        "avg boost amount",
        "amount collected",
        "amount stolen",
        "avg speed",
        "percentage supersonic speed",
        "avg distance to ball",
        "percentage behind ball",
        "percentage offensive half",
        "percentage offensive third",
        "percentage defensive third",
        "demos inflicted",
        "demos taken",
    ]

    available = [c for c in candidates if c in teams.columns]

    if len(available) < 2:
        st.info(
            "Il faut au moins deux statistiques numériques disponibles "
            "pour calculer les corrélations."
        )
        return

    data = teams[available].apply(pd.to_numeric, errors="coerce")
    data = data.dropna(axis=1, how="all")

    # Retirer les variables constantes, qui ne possèdent pas
    # de corrélation calculable.
    data = data.loc[:, data.nunique(dropna=True) > 1]

    if data.shape[1] < 2:
        st.info("Pas assez de variables différentes pour calculer les corrélations.")
        return

    corr = data.corr()

    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        origin="lower",
        title="Corrélations entre les statistiques de gameplay",
        labels={
            "x": "Statistique",
            "y": "Statistique",
            "color": "Corrélation",
        },
    )

    fig.update_layout(
        template="plotly_white",
        height=max(600, len(corr.columns) * 38),
        xaxis={"tickangle": -45},
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Une corrélation proche de +1 indique une association positive, "
        "proche de -1 une association négative, et proche de 0 une "
        "absence de relation linéaire marquée. Cela ne démontre pas "
        "de causalité."
    )
