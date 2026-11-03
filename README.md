# API de gestion d'un atelier de couture

Back-end REST (FastAPI + PostgreSQL) pour la gestion d'un atelier de couture :
clients, mesures, commandes, paiements, livraisons, statistiques.

> **Périmètre de ce dépôt — Partie A (Palier 1 : socle).**
> Cette partie livre l'infrastructure complète et le socle fonctionnel :
> authentification JWT, gestion des utilisateurs, des clients et du catalogue,
> ainsi que la route de santé. Le schéma de base de données est **complet**
> (toutes les tables du projet) afin que la **Partie B** (mesures, commandes,
> statuts, paiements, livraisons, statistiques) se branche dessus sans refonte.

## Sommaire
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Lancement avec Docker (recommandé)](#lancement-avec-docker-recommandé)
- [Lancement en local](#lancement-en-local)
- [Comptes de test](#comptes-de-test)
- [Routes réalisées (Partie A)](#routes-réalisées-partie-a)
- [Tests](#tests)
- [Conventions](#conventions)

## Architecture

Séparation stricte des responsabilités (exigée par l'énoncé) :

```
app/
  core/        config (.env), base de données, sécurité (Argon2 + JWT)
  models/      modèles SQLAlchemy 2 (Mapped, mapped_column)
  schemas/     schémas Pydantic (création / modification / lecture séparés)
  services/    logique métier, testable hors des routes
  routers/     APIRouter par domaine (auth, utilisateurs, clients, catalogue, santé)
  deps.py      dépendances d'authentification et de contrôle des rôles
  main.py      assemblage de l'application
  seed.py      script d'initialisation (admin + catalogue)
alembic/       migrations (schéma initial complet)
tests/         pytest (TestClient)
```

- **Routeurs** : vérifient les droits, appellent un service, valident la
  transaction. Aucune règle de gestion.
- **Services** : toute la logique métier (unicité du téléphone, droits RG24…).
- **Modèles ≠ schémas** : le hash du mot de passe n'est jamais renvoyé (RG21).

## Prérequis

- Docker + Docker Compose, **ou** Python 3.12+ et PostgreSQL 14+.

## Lancement avec Docker (recommandé)

```bash
cp .env.example .env        # puis adaptez SECRET_KEY, ADMIN_PASSWORD, etc.
docker compose up --build
```

L'entrypoint attend la base, applique les migrations (`alembic upgrade head`),
exécute le seed (`python -m app.seed`) puis démarre l'API.

- API : http://localhost:8000
- Documentation Swagger : http://localhost:8000/docs
- Santé : http://localhost:8000/health

## Lancement en local

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # DATABASE_URL doit pointer vers votre PostgreSQL

alembic upgrade head             # crée le schéma
python -m app.seed               # crée l'admin + le catalogue de départ
uvicorn app.main:app --reload
```

> La base de production est **PostgreSQL** (aucun SQLite). SQLite n'est utilisé
> que par la suite de tests.

## Comptes de test

Le script `app.seed` crée l'administrateur initial à partir des variables
d'environnement (`ADMIN_EMAIL`, `ADMIN_PASSWORD`). Valeurs par défaut du
`.env.example` :

| Rôle  | E-mail            | Mot de passe  |
|-------|-------------------|---------------|
| admin | `admin@atelier.sn`| `changeme123` |

Les comptes `accueil` et `tailleur` se créent ensuite via `POST /utilisateurs`
(réservé à l'administrateur). **Changez le mot de passe admin en production.**

## Routes réalisées (Partie A)

Préfixe : `/api/v1` (sauf `/health`).

### Authentification
| Méthode | Chemin        | Rôle     | Description |
|---------|---------------|----------|-------------|
| POST    | `/auth/login` | Public   | Connexion OAuth2 (username = e-mail). Renvoie `access_token`, `token_type`, `expires_in`. |
| GET     | `/auth/me`    | Connecté | Profil de l'utilisateur connecté. |

### Utilisateurs (admin)
| Méthode | Chemin               | Description |
|---------|----------------------|-------------|
| POST    | `/utilisateurs`      | Crée un compte (409 si e-mail existant). |
| GET     | `/utilisateurs`      | Liste triée par nom. |
| GET     | `/utilisateurs/{id}` | Détail (404 sinon). |
| PATCH   | `/utilisateurs/{id}` | Modifie nom, rôle, état actif, mot de passe (RG24). |

### Clients
| Méthode | Chemin                     | Rôle  | Description |
|---------|----------------------------|-------|-------------|
| POST    | `/clients`                 | Tous  | Crée un client (RG1 : téléphone unique normalisé). |
| GET     | `/clients`                 | Tous  | Liste paginée (filtres `q`, `genre`, `limit`, `offset`). |
| GET     | `/clients/{id}`            | Tous  | Fiche client. |
| PATCH   | `/clients/{id}`            | Tous  | Modification partielle. |
| DELETE  | `/clients/{id}`            | Admin | Supprime (409 s'il a des commandes — RG4). |
| GET     | `/clients/{id}/commandes`  | Tous  | Commandes du client (paginées). |
| GET     | `/clients/{id}/resume`     | Tous  | Résumé d'activité (commandes annulées exclues). |

### Catalogue des prestations
| Méthode | Chemin            | Rôle  | Description |
|---------|-------------------|-------|-------------|
| POST    | `/catalogue`      | Admin | Ajoute une prestation (409 si nom existant). |
| GET     | `/catalogue`      | Tous  | Liste triée (actives par défaut ; `actifs_seulement=false` pour tout). |
| GET     | `/catalogue/{id}` | Tous  | Détail (404 sinon). |
| PATCH   | `/catalogue/{id}` | Admin | Modifie prix, délai, nom, état actif. |

### Santé
| Méthode | Chemin    | Description |
|---------|-----------|-------------|
| GET     | `/health` | `{"status": "ok"}` après vérification de la base. |

### Règles de gestion couvertes
RG1 (téléphone unique normalisé), RG4 (suppression client protégée),
RG21 (Argon2, mot de passe ≥ 8, jamais renvoyé), RG22 (JWT + compte désactivé
refusé), RG23 (message de connexion indifférencié), RG24 (admin ne se désactive
pas / ne retire pas son rôle).

## Tests

```bash
pip install -r requirements.txt
pytest
```

Les tests utilisent une base **SQLite en mémoire** (via surcharge de la
dépendance `get_db`) et couvrent : santé, authentification, droits par rôle,
règles clients (RG1, RG4), utilisateurs (RG24) et catalogue.

## Conventions

- Erreurs : `{"detail": "message en français"}`.
- Listes paginées : `{"items": [...], "total": n, "limit": n, "offset": n}`
  (défaut `limit=20`, max `100`, `offset=0`).
- Noms de routes, champs et statuts en français.
- Montants en entiers (FCFA), mesures en centimètres.

---
Projet pédagogique — Module « Développement d'API avec FastAPI et PostgreSQL ».
