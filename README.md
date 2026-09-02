# 🛫 ASKY Airlines — Détection d'Anomalies Carburant CORSIA

## 📋 Description
Outil de contrôle qualité automatique des données CORSIA d'ASKY Airlines.
Détecte automatiquement les vols avec une consommation de carburant anormale
chaque fin de mois — en quelques secondes au lieu de plusieurs heures d'analyse manuelle.

## 🎯 Problème résolu
Les données CORSIA de chaque mois contiennent des milliers de vols.
Détecter manuellement les anomalies de consommation dans Excel prend des heures.
Ce modèle ML le fait automatiquement en quelques secondes.

## 🤖 Algorithme utilisé
**IsolationForest** — algorithme de détection d'anomalies non supervisé.
- S'entraîne sur l'historique cumulé de tous les mois précédents
- Devient plus précis chaque mois
- Détecte les combinaisons inhabituelles de variables

## 📊 Features utilisées
| Feature | Description |
|---|---|
| `Fuel` | Carburant consommé (kg) |
| `PAX` | Nombre de passagers |
| `Freight` | Fret transporté (kg) |
| `Seats` | Capacité de l'avion |
| `Scheduled` | Vol schedulé ou non |
| `duree_vol` | Durée réelle du vol (minutes) |

## ⚠️ Types d'anomalies détectées
- Carburant excessif par rapport à la durée du vol
- Carburant très faible
- Vols sans passagers (vols techniques)
- Durée de vol excessive
- Consommation par minute anormale
- Combinaisons inhabituelles de variables

## 📈 Résultats sur 4 mois (Mars-Juin 2026)
| Mois | Vols analysés | Anomalies détectées |
|---|---|---|
| Mars 2026 | 1 427 | 71 |
| Avril 2026 | ~1 400 | 71 |
| Mai 2026 | ~1 400 | 87 |
| Juin 2026 | ~1 400 | 93 |

## 🚀 Comment utiliser
1. Copier le fichier CORSIA du mois dans le dossier
2. Modifier les 3 lignes de configuration :
```python
FICHIER_MOIS = 'CORSIA_MOIS_2026.xlsx'
NOM_FEUILLE = 'MOIS'
MOIS_LABEL = 'MOIS_2026'
```
3. Lancer le script
4. Récupérer le rapport Excel généré automatiquement

## 🛠️ Technologies utilisées
- Python 3.13
- pandas
- scikit-learn (IsolationForest)
- numpy
- matplotlib

## 👤 Auteur
**SAMAH Essodeou Yohann**
Data Analyst — ASKY Airlines, Lomé, Togo
essodeouyohannsamah@gmail.com