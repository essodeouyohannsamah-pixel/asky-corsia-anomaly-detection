
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import os

# ================================
# CONFIGURATION — change ici chaque mois
# ================================
FICHIER_MOIS = 'CORSIA MAI 2026.xlsx'  
NOM_FEUILLE = 'MAI' 
MOIS_LABEL = 'MAI_2026'
HISTORIQUE = 'historique_corsia.csv'

print("✅ Outils chargés !")

# ================================
# BLOC 2 — Charger et préparer
# ================================

# Charger le fichier du mois
df = pd.read_excel(FICHIER_MOIS, sheet_name=NOM_FEUILLE)
print(f"✅ {len(df)} vols chargés pour {MOIS_LABEL}")

# Calculer la durée du vol en minutes
df['Block Off Time'] = pd.to_datetime(
    df['Block Off Time'],
    format='%H:%M:%S'
)

df['Block On Time'] = pd.to_datetime(
    df['Block On Time'],
    format='%H:%M:%S'
)

df['duree_vol'] = (
    df['Block On Time'] - df['Block Off Time']
).dt.seconds / 60

# Ajouter le mois pour l'historique
df['mois'] = MOIS_LABEL

print("✅ Durée calculée !")
print("\nAperçu durées :")
print(
    df[
        ['FlightNb', 'Block Off Time', 'Block On Time', 'duree_vol']
    ].head()
)

# ================================
# BLOC 3 — Sélectionner les features
# ================================

cols = [
    'PAX',
    'Freight',
    'Seats',
    'Fuel',
    'Scheduled',
    'duree_vol'
]

df_ml = df[cols].copy()

# Supprimer les lignes avec valeurs manquantes
df_ml = df_ml.dropna()

print("✅ Features sélectionnées !")
print(f"Vols disponibles : {len(df_ml)}")
print("\nStatistiques :")
print(df_ml.describe())

# ================================
# BLOC 4 — Historique et normalisation
# ================================

# Ajouter le mois à l'historique
if os.path.exists(HISTORIQUE):
    historique = pd.read_csv(HISTORIQUE)

    historique = pd.concat(
        [historique, df_ml],
        ignore_index=True
    )

    print("✅ Historique mis à jour !")
else:
    historique = df_ml.copy()
    print("✅ Premier mois — historique créé !")

# Sauvegarder l'historique
historique.to_csv(HISTORIQUE, index=False)

print(f"Total vols dans l'historique : {len(historique)}")

# Normaliser
scaler = StandardScaler()

historique_scaled = scaler.fit_transform(
    historique[cols]
)

print("✅ Données normalisées !")

# ================================
# BLOC 5 — Entraînement et détection
# ================================

# Entraîner sur tout l'historique
modele = IsolationForest(
    contamination=0.05,
    random_state=42
)

modele.fit(historique_scaled)

print("✅ Modèle entraîné sur l'historique complet !")

# Normaliser uniquement le mois en cours
mois_scaled = scaler.transform(
    df_ml[cols]
)

# Détecter les anomalies du mois en cours
predictions = modele.predict(mois_scaled)

# Ajouter les résultats
df_ml = df_ml.copy()

df_ml['STATUT'] = predictions

df_ml['STATUT'] = df_ml['STATUT'].map(
    {
        1: 'Normal',
        -1: 'Anomalie'
    }
)

# Ajouter les infos du vol
df_ml['FlightNb'] = df['FlightNb'].values
df_ml['DateDep'] = df['DateDep'].values
df_ml['Origin'] = df['Origin'].values
df_ml['Destination'] = df['Destination'].values
df_ml['Aircraft'] = df['Aircraft'].values

print("\nRépartition :")
print(df_ml['STATUT'].value_counts())

# ================================
# BLOC 6 — Rapport complet
# ================================

# Prendre toutes les colonnes originales
rapport = df.copy()

# Ajouter la colonne STATUT
rapport['STATUT'] = df_ml['STATUT'].values

rapport['duree_vol'] = df_ml['duree_vol'].values

# Trier — anomalies en premier
rapport = rapport.sort_values(
    'STATUT',
    ascending=True
)

# Exporter tout en Excel
rapport.to_excel(
    f'rapport_anomalies_{MOIS_LABEL}.xlsx',
    index=False
)

# Résumé
anomalies = rapport[
    rapport['STATUT'] == 'Anomalie'
]

print(
    f"✅ Rapport exporté : "
    f"rapport_anomalies_{MOIS_LABEL}.xlsx"
)

print(f"\n📊 Résumé {MOIS_LABEL} :")

print(f"   Total vols    : {len(rapport)}")

print(
    f"   Vols normaux  : "
    f"{len(rapport[rapport['STATUT'] == 'Normal'])}"
)

print(
    f"   Anomalies     : "
    f"{len(anomalies)}"
)

print("\n⚠️ Vols anormaux :")

print(
    anomalies[
        [
            'FlightNb',
            'DateDep',
            'Origin',
            'Destination',
            'PAX',
            'Fuel',
            'duree_vol',
            'STATUT'
        ]
    ].to_string()
)

# ================================
# BLOC 7 — Nature des anomalies
# ================================

def nature_anomalie(row):
    raisons = []
    
    # Carburant
    if row['Fuel'] > 10000:
        raisons.append("Carburant excessif")
    elif row['Fuel'] < 1500:
        raisons.append("Carburant très faible")
    
    # Passagers
    if row['PAX'] == 0:
        raisons.append("Vol sans passagers")
    elif row['PAX'] < 20:
        raisons.append("Très peu de passagers")
    
    # Durée
    if row['duree_vol'] > 250:
        raisons.append("Durée excessive")
    elif row['duree_vol'] < 50:
        raisons.append("Durée très courte")
    
    # Consommation par minute
    if row['duree_vol'] > 0:
        conso_min = row['Fuel'] / row['duree_vol']
        if conso_min > 60:
            raisons.append("Consommation/minute élevée")
        elif conso_min < 15:
            raisons.append("Consommation/minute faible")
    
    # Fret anormal
    if row['Freight'] == 0 and row['PAX'] > 50:
        raisons.append("Fret nul avec passagers")
    
    # Si aucune règle
    if not raisons:
        raisons.append("Combinaison inhabituelle")
    
    return " + ".join(raisons)
    # Si aucune règle ne s'applique
    if not raisons:
        raisons.append(
            "Combinaison inhabituelle"
        )

    return " + ".join(raisons)


# Appliquer sur les anomalies
anomalies_rapport = df_ml[
    df_ml['STATUT'] == 'Anomalie'
].copy()

anomalies_rapport['NATURE_ANOMALIE'] = (
    anomalies_rapport.apply(
        nature_anomalie,
        axis=1
    )
)

# Ajouter les infos complètes
anomalies_final = df[
    df.index.isin(
        anomalies_rapport.index
    )
].copy()

anomalies_final['STATUT'] = 'Anomalie'

anomalies_final['duree_vol'] = (
    anomalies_rapport['duree_vol']
)

anomalies_final['NATURE_ANOMALIE'] = (
    anomalies_rapport['NATURE_ANOMALIE'].values
)

# Exporter
anomalies_final.to_excel(
    f'rapport_anomalies_{MOIS_LABEL}.xlsx',
    index=False
)

print(
    "✅ Rapport exporté avec nature des anomalies !"
)

print("\n📊 Répartition des anomalies :")

print(
    anomalies_rapport[
        'NATURE_ANOMALIE'
    ].value_counts()
)

