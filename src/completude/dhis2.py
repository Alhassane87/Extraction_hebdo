"""Client HTTP pour l'API DHIS2 : authentification, retries, et repli SSL explicite.

Contrairement a l'ancien notebook (qui retentait silencieusement en
verify=False si verify=True echouait), ce client ne fait JAMAIS de repli SSL
automatique : le mode (strict ou desactive) vient de la configuration et,
s'il est desactive, un avertissement est explicitement logue.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import requests
import urllib3

logger = logging.getLogger(__name__)


class Dhis2ConnectionError(RuntimeError):
    """Aucune URL candidate n'a repondu correctement."""


@dataclass
class Dhis2Client:
    base_url: str
    session: requests.Session
    timeout_s: int = 180

    @classmethod
    def connecter(
        cls,
        urls_candidates: list[str],
        username: str,
        password: str,
        verify_ssl: bool = True,
        timeout_s: int = 180,
    ) -> Dhis2Client:
        session = requests.Session()
        session.auth = (username, password)

        if not verify_ssl:
            logger.warning(
                "DHIS2_VERIFY_SSL=false : verification SSL desactivee explicitement "
                "par la configuration (aucun repli automatique n'est effectue)."
            )
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        erreurs = []
        for url in urls_candidates:
            try:
                r = session.get(
                    f"{url}/api/me.json",
                    params={"fields": "username"},
                    timeout=30,
                    verify=verify_ssl,
                )
                if r.status_code == 200 and "username" in r.text:
                    logger.info("Connecte a %s (SSL verifie=%s)", url, verify_ssl)
                    session.verify = verify_ssl
                    return cls(base_url=url, session=session, timeout_s=timeout_s)
                erreurs.append(f"{url} -> HTTP {r.status_code}")
            except requests.RequestException as e:
                erreurs.append(f"{url} -> {type(e).__name__}: {e}")

        raise Dhis2ConnectionError(
            "Connexion DHIS2 impossible sur " + ", ".join(urls_candidates) + " "
            f"(SSL verifie={verify_ssl}). Details : " + " | ".join(erreurs)
        )

    def api(self, path: str, max_retries: int = 3, backoff_s: float = 2.0, **params):
        """GET /api/{path}, avec retries exponentiels sur erreur reseau/HTTP."""
        derniere_erreur: Exception | None = None
        for tentative in range(1, max_retries + 1):
            try:
                r = self.session.get(
                    f"{self.base_url}/api/{path}", params=params, timeout=self.timeout_s
                )
                r.raise_for_status()
                return r.json()
            except requests.RequestException as e:
                derniere_erreur = e
                if tentative < max_retries:
                    attente = backoff_s * (2 ** (tentative - 1))
                    logger.warning(
                        "Echec appel %s (tentative %d/%d) : %s - nouvelle tentative dans %.0fs",
                        path, tentative, max_retries, e, attente,
                    )
                    time.sleep(attente)
        assert derniere_erreur is not None
        raise derniere_erreur
