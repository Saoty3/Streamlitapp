
import pandas as pd


def make_tables(df_raw):
    """Prépare les données et construit les tables pour le dashboard."""

    df = df_raw.copy()

    # Conversion des colonnes en valeurs numériques lorsque possible
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")

    # Vérification des colonnes nécessaires pour déterminer le résultat
    required = ["goals-a", "goals conceded-a"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(
            f"Colonnes nécessaires absentes : {missing}. "
            "Vérifie les noms des colonnes de train.csv."
        )

    # Scores observés du point de vue de l'équipe A
    goals_a = pd.to_numeric(df["goals-a"], errors="coerce")
    goals_b = pd.to_numeric(df["goals conceded-a"], errors="coerce")

    # Résultat de l'équipe A
    df["result-a"] = "Draw"
    df.loc[goals_a > goals_b, "result-a"] = "Win"
    df.loc[goals_a < goals_b, "result-a"] = "Loss"

    # Résultat de l'équipe B : inverse de celui de l'équipe A
    df["result-b"] = df["result-a"].map(
        {"Win": "Loss", "Loss": "Win", "Draw": "Draw"}
    )

    # Construire une table longue : une ligne par équipe et par match
    # On ne conserve que les statistiques réellement présentes dans le CSV.
    team_rows = []

    for suffix, result_col in [("-a", "result-a"), ("-b", "result-b")]:
        stats = {
            col[:-len(suffix)]: df[col]
            for col in df.columns
            if col.endswith(suffix)
            and col not in ["result-a", "result-b"]
        }

        team_df = pd.DataFrame(stats)
        team_df["team"] = "A" if suffix == "-a" else "B"
        team_df["result"] = df[result_col].values
        team_df["match_id"] = df.index

        # Ajouter les buts et les tirs à partir des colonnes disponibles.
        if suffix == "-a":
            team_df["goals"] = goals_a.values
            team_df["goals_conceded"] = goals_b.values
            if "shots-a" in df.columns:
                team_df["shots"] = df["shots-a"].values
            if "shots conceded-a" in df.columns:
                team_df["shots_conceded"] = df["shots conceded-a"].values
        else:
            team_df["goals"] = goals_b.values
            team_df["goals_conceded"] = goals_a.values
            if "shots conceded-a" in df.columns:
                team_df["shots"] = df["shots conceded-a"].values
            if "shots-a" in df.columns:
                team_df["shots_conceded"] = df["shots-a"].values

        team_rows.append(team_df)

    teams = pd.concat(team_rows, ignore_index=True)

    # Garder uniquement les statistiques numériques pour les comparaisons.
    excluded = {"match_id"}
    numeric_cols = [
        col for col in teams.select_dtypes(include="number").columns
        if col not in excluded
    ]

    # Comparaison moyenne des gagnants et des perdants
    comparison = (
        teams[teams["result"].isin(["Win", "Loss"])]
        .groupby("result")[numeric_cols]
        .mean()
        .T
        .reset_index(names="metric")
    )

    # Informations générales sur le jeu de données
    summary = {
        "matches": len(df),
        "teams": len(teams),
        "wins_a": int((df["result-a"] == "Win").sum()),
        "wins_b": int((df["result-b"] == "Win").sum()),
        "draws": int((df["result-a"] == "Draw").sum()),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }

    return {
        "raw": df,
        "teams": teams,
        "comparison": comparison,
        "summary": summary,
    }
