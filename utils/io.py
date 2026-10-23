
from pathlib import Path

import pandas as pd


# Chemin vers le fichier CSV, à partir de la racine du projet
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "isaac_train_xG.csv"


def load_data():
    """Charge le jeu de données Rocket League."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {DATA_PATH}\n"
            "Vérifie que isaac_train_xG.csv se trouve dans le dossier data/."
        )

    df = pd.read_csv(DATA_PATH)

    # Nettoyage léger des noms de colonnes
    df.columns = df.columns.str.strip()

    return df
