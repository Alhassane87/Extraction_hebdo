from unittest.mock import MagicMock, patch

import pytest
import requests

from completude.dhis2 import Dhis2Client, Dhis2ConnectionError


def _reponse(status_code=200, texte="", json_data=None):
    r = MagicMock()
    r.status_code = status_code
    r.text = texte
    r.json.return_value = json_data or {}
    r.raise_for_status.side_effect = (
        None if status_code < 400 else requests.HTTPError(f"HTTP {status_code}")
    )
    return r


def test_connecter_essaie_les_urls_dans_l_ordre_et_s_arrete_au_premier_succes():
    appels = []

    def get_fake(self, url, **kwargs):
        appels.append(url)
        if "senegal.dhis2.org/dhis" in url:
            return _reponse(status_code=404)
        return _reponse(status_code=200, texte='{"username":"test"}')

    with patch.object(requests.Session, "get", get_fake):
        client = Dhis2Client.connecter(
            urls_candidates=["https://senegal.dhis2.org/dhis", "https://senegal.dhis2.org"],
            username="u", password="p", verify_ssl=True,
        )

    assert client.base_url == "https://senegal.dhis2.org"
    assert len(appels) == 2


def test_connecter_leve_une_erreur_claire_si_aucune_url_ne_repond():
    with patch.object(requests.Session, "get", lambda self, url, **kw: _reponse(status_code=500)):
        with pytest.raises(Dhis2ConnectionError):
            Dhis2Client.connecter(
                urls_candidates=["https://senegal.dhis2.org/dhis"],
                username="u", password="p", verify_ssl=True,
            )


def test_connecter_ne_bascule_jamais_automatiquement_en_ssl_desactive():
    # Avec verify_ssl=True explicite, aucun second essai en verify=False ne doit avoir lieu :
    # on vérifie juste que l'appel reçoit bien verify=True, jamais verify=False en interne.
    appels_verify = []

    def get_fake(self, url, **kwargs):
        appels_verify.append(kwargs.get("verify"))
        return _reponse(status_code=500)

    with patch.object(requests.Session, "get", get_fake):
        with pytest.raises(Dhis2ConnectionError):
            Dhis2Client.connecter(
                urls_candidates=["https://senegal.dhis2.org/dhis"],
                username="u", password="p", verify_ssl=True,
            )

    assert appels_verify == [True]


def test_api_retente_puis_reussit():
    appels = {"n": 0}

    def get_fake(self, url, params=None, timeout=None):
        appels["n"] += 1
        if appels["n"] < 3:
            raise requests.ConnectionError("réseau indisponible")
        return _reponse(status_code=200, json_data={"ok": True})

    client = Dhis2Client(base_url="https://x", session=requests.Session())
    with patch.object(requests.Session, "get", get_fake), patch("completude.dhis2.time.sleep"):
        resultat = client.api("me.json", max_retries=3, backoff_s=0.01)

    assert resultat == {"ok": True}
    assert appels["n"] == 3


def test_api_leve_apres_epuisement_des_tentatives():
    def get_fake(self, url, params=None, timeout=None):
        raise requests.ConnectionError("toujours indisponible")

    client = Dhis2Client(base_url="https://x", session=requests.Session())
    with patch.object(requests.Session, "get", get_fake), patch("completude.dhis2.time.sleep"):
        with pytest.raises(requests.ConnectionError):
            client.api("me.json", max_retries=2, backoff_s=0.01)
