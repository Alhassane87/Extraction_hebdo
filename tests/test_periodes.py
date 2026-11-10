from datetime import date

from completude.periodes import code_periode, fenetre_mois, libelle_periode, norm, parse_periode


def test_norm_enleve_accents_et_ponctuation():
    assert norm("Région de Dakar !") == "region de dakar"


def test_parse_periode_texte_francais():
    assert parse_periode("Juillet 2026") == (2026, 7)
    assert parse_periode("  Août   2026 ") == (2026, 8)


def test_parse_periode_vide_ou_absente():
    assert parse_periode(None) is None
    assert parse_periode("") is None
    assert parse_periode(float("nan")) is None


def test_libelle_periode_recalcule_depuis_le_code():
    assert libelle_periode(code_periode(2026, 7)) == "Juillet 2026"
    assert libelle_periode("202612") == "Décembre 2026"


def test_libelle_periode_code_invalide_renvoie_chaine_vide():
    assert libelle_periode("abc123") == ""
    assert libelle_periode("202613") == ""  # mois 13 inexistant


def test_fenetre_mois_mois_courant_et_deux_precedents():
    assert fenetre_mois(date(2026, 11, 10), 3) == [(2026, 9), (2026, 10), (2026, 11)]


def test_fenetre_mois_traverse_le_changement_d_annee():
    assert fenetre_mois(date(2026, 1, 10), 3) == [(2025, 11), (2025, 12), (2026, 1)]
