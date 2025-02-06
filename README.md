# KIDIKOI 🎙️ - Assistant de réunion

## 🎯 Track 2 : Cas d'Usage à Fort Impact avec des APIs

KIDIKOI est une application web innovante conçue pour faciliter la transcription, l'analyse et la compréhension des conversations dans le secteur public. Elle combine des technologies de pointe en traitement du langage naturel pour transformer les enregistrements audio et vidéo en insights exploitables.

## 🚀 Fonctionnalités Principales

- **Transcription Multimodale**
  - Support audio (MP3, WAV, OGG, M4A, FLAC)
  - Support vidéo (MP4, AVI, MOV, MKV)
  - Enregistrement audio en direct
  - Détection automatique des locuteurs

- **Analyses Avancées**
  - Compte-rendu détaillé automatique
  - Attribution des propos par intervenant
  - Analyse des questions/réponses
  - Analyse émotionnelle des échanges
  - Statistiques de conversation
  - Génération de cartes mentales
  - Identification des points d'attention

- **Interface Utilisateur Intuitive**
  - Interface web responsive avec Streamlit
  - Visualisation des transcriptions en temps réel
  - Chat contextuel pour interroger le contenu
  - Export des rapports en format Word

## Fonctionnalités à terminer / Suite du projet

- **Fonctionnalités à finir de développer**
    - Support vidéo
    - Enregistrement audio en direct

- **Fonctionnalités à venir**
    - Amélioration de l'identification des locuteurs

## 💡 Cas d'Usage dans le Service Public

- **Réunions Administratives**
  - Transcription automatique des séances
  - Génération de comptes-rendus structurés
  - Suivi des décisions et actions

- **Services aux Usagers**
  - Documentation des entretiens
  - Analyse des besoins exprimés
  - Traçabilité des échanges

- **Formation et Documentation**
  - Capitalisation des connaissances
  - Support pour la formation des agents
  - Base de connaissances searchable

## 🛠️ Architecture Technique

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Modèles IA**:
  - Whisper (Transcription)
  - Pyannote (Diarization)
  - LLMs pour l'analyse (Mistral)

## 📊 Évaluation selon les Critères du Track 2

### 🎯 Pertinence (25%)
- Répond au besoin crucial de documentation et d'analyse des échanges dans l'administration
- Automatise des tâches chronophages de transcription et synthèse
- Améliore la qualité et la traçabilité des interactions

### 📈 Impact (25%)
- Gain de temps significatif pour les agents (estimation : 30-40%)
- Amélioration de la qualité des comptes-rendus
- Meilleure exploitation des informations échangées
- Accessibilité accrue des contenus

### 🔧 Faisabilité (25%)
- MVP fonctionnel déjà développé
- Utilisation de technologies éprouvées
- Architecture modulaire et maintenable
- Documentation technique complète

### 🌍 Scalabilité (25%)
- Architecture cloud-native
- APIs standardisées
- Open source et interopérable
- Adaptable à différents contextes administratifs

## 🚀 Installation

```bash
# Cloner le repository
git clone [url-du-repo]
cd kidikoi

# Installer les dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Éditer .env avec vos tokens

# Lancer l'application
uvicorn backend.main:app --host 0.0.0.0 --port 8502
streamlit run ui/app.py
```

## 📝 Licence

Ce projet est distribué sous licence MIT.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request. 