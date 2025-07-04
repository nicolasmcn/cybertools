# CyberTools – Application Flask de Cybersécurité

> CyberTools est une plateforme web qui permet à un utilisateur de :
> - Créer un compte sécurisé
> - Analyser un nom de domaine
> - Enregistrer ses mots de passe pour évaluation
> - Supprimer ses données personnelles conformément au RGPD

---

## Sommaire

1. [Présentation du projet](#-présentation-du-projet)
2. [Fonctionnalités](#-fonctionnalités)
3. [Technologies utilisées](#-technologies-utilisées)
4. [Installation en local](#-installation-en-local)

---

## Présentation du projet

CyberTools est un outil pédagogique développé dans le cadre d'un projet de fin de formation de Concepteur Développeur d’Applications. Il vise à intégrer les bonnes pratiques de sécurité, de persistance des données, et de développement web.

L'utilisateur peut :
- Créer un compte avec mot de passe sécurisé (conformité RGPD)
- Se connecter et accéder à son tableau de bord
- Analyser un domaine web
- Sauvegarder l'historique de ses mots de passe
- Supprimer définitivement ses données

---

## Fonctionnalités

- Authentification sécurisée avec Flask-Login, Bcrypt, sessions
- Vérification de mot de passe fort (8+ caractères, 2 chiffres, 1 spécial)
- Analyse de domaine (simulation)
- Historique des mots de passe
- Supprimer ses données (conformité RGPD)
- Pagination, dashboard utilisateur

---

## Technologies utilisées

- **Back-end** : Flask, SQLAlchemy, Flask-Bcrypt, Flask-Cors
- **Front-end** : HTML5, CSS3, Bootstrap 5, Jinja2
- **Base de données** : MySQL (en production), SQLite (pour tests)
- **Déploiement** : DigitalOcean, Gunicorn, Nginx
- **Tests** : Pytest
- **Autres** : Python 3.10+

---

## Installation en local

```bash
git clone https://github.com/votre-utilisateur/cybertools.git
cd cybertools
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```