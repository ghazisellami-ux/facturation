# SIC Facture 🧾

Application de **facturation et gestion commerciale** pour TPE/PME, adaptée au contexte fiscal tunisien.

## 🚀 Stack Technique

| Composant | Technologie |
|-----------|-------------|
| **Frontend** | Next.js 14 (App Router, TypeScript) |
| **Backend** | FastAPI (Python 3.11) |
| **Base de données** | PostgreSQL 16 |
| **Conteneurisation** | Docker & Docker Compose |

## 📋 Fonctionnalités

- ✅ Authentification JWT (inscription, connexion)
- ✅ Tableau de bord avec KPIs et graphiques
- ✅ Gestion des clients (CRUD complet)
- ✅ Catalogue produits & services
- ✅ Facturation avec calculs automatiques (TVA, FODEC, Timbre fiscal)
- ✅ Devis avec conversion en facture
- ✅ Gestion des statuts (Brouillon, Envoyée, Payée, En retard)
- ✅ Numérotation automatique des documents

## 🏃 Démarrage rapide

### Prérequis
- Docker & Docker Compose installés
- Node.js 18+ (pour le dev local)
- Python 3.11+ (pour le dev local)

### Avec Docker (recommandé)

```bash
# Cloner le projet
git clone https://github.com/ghazisellami-ux/facturation.git
cd facturation

# Lancer tous les services
docker-compose up --build

# L'application sera disponible sur :
# Frontend : http://localhost:3000
# Backend API : http://localhost:8000/api/docs
# PostgreSQL : localhost:5432
```

### Développement local

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (autre terminal)
cd frontend
npm install
npm run dev
```

## 🏗️ Structure du projet

```
facturation/
├── frontend/          # Next.js 14
│   └── src/app/       # Pages (login, dashboard, factures, clients, produits)
├── backend/           # FastAPI
│   └── app/           # Models, Schemas, Routers, Services
├── docker-compose.yml # Orchestration Docker
└── README.md
```

## 💰 Fiscalité tunisienne

- **TVA** : 19%, 13%, 7%, 0%
- **FODEC** : Configurable par produit
- **Timbre fiscal** : 1.000 TND par défaut

## 📄 Licence

Projet privé — © SIC Facture 2024
