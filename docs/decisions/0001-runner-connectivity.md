# 0001 — Connectivité des runners GitHub Actions vers DHIS2

**Statut : en attente d'exécution.**

## Contexte

Avant de figer l'architecture du cron hebdomadaire (Phase 3), il faut savoir
si les runners `ubuntu-latest` hébergés par GitHub (IP cloud dynamiques,
US/EU) peuvent atteindre `https://senegal.dhis2.org` — un pare-feu côté
DHIS2 limité à des IP connues bloquerait silencieusement ces appels.

## Comment obtenir la réponse

1. Configurer les secrets du dépôt : `Settings → Secrets and variables →
   Actions` → ajouter `DHIS2_USER` et `DHIS2_PASSWORD`.
2. Lancer manuellement le workflow `Test de connectivite DHIS2`
   (`.github/workflows/connectivity-check.yml`) depuis l'onglet **Actions**.
3. Lire le tableau produit dans le résumé du run (code HTTP + latence pour
   chaque combinaison URL × SSL).

## Lecture du résultat

- **Code 200** sur au moins une combinaison → les runners GitHub-hosted
  joignent DHIS2 ; l'architecture peut rester 100% cloud (Phase 3 telle que
  planifiée).
- **Code 401/403** → le serveur est bien atteint (pas de blocage réseau),
  mais les identifiants sont refusés — vérifier les secrets, pas un problème
  de connectivité.
- **Code 000 / timeout / aucune réponse** sur toutes les combinaisons →
  blocage réseau probable. Décision à prendre : mettre en place un runner
  auto-hébergé (machine sous contrôle du MSHP ou du prestataire, enregistrée
  sur ce dépôt privé) exécutant les mêmes workflows YAML (seul `runs-on:`
  change).

## Décision

*(à compléter après exécution du test — résultat obtenu, date, choix final
runner cloud vs auto-hébergé)*
