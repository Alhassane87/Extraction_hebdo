# Dashboard de complétude DHIS2 — Sénégal

Suivi hebdomadaire (chaque lundi) de la complétude des rapports DHIS2 par
région, district, période et formulaire, pour la Division du Système
d'Information Sanitaire et Sociale (DSISS) du Ministère de la Santé et de
l'Hygiène publique du Sénégal.

Ce dépôt remplace un ancien fonctionnement manuel (notebook Google Colab +
dashboard HTML téléchargé à la main, conservés dans [`legacy/`](legacy/) à
titre de référence) par une plateforme hébergée sur GitHub : extraction
automatisée chaque lundi, historique dédupliqué par semaine, dashboard
accessible, mascotte « Goorgui », mode diaporama TV.

## État du projet

En cours de migration — voir le plan de construction et son avancement par
phases. Ce README sera complété au fil des phases (installation, variables
d'environnement, déploiement, exploitation) conformément au plan.

## Structure cible

```
config/          configuration (seuils, gabarit Excel)
src/completude/  extraction, historique, génération Excel/JSON (Python)
web/             dashboard front-end statique
data/            données publiées (history.csv, latest.json, geo/)
.github/workflows/  extraction automatisée, déploiement, CI
legacy/          notebook et dashboard d'origine (référence, non maintenus)
docs/            décisions d'architecture, runbook
```

## Sécurité

Aucun identifiant DHIS2 n'est stocké dans ce dépôt. Copier `.env.example`
en `.env` pour un usage local (jamais committé). En CI, les identifiants
vivent dans les secrets GitHub Actions du dépôt.
