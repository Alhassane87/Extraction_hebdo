"""Génération de l'Excel de complétude stylé (seuils rouge/orange/vert)."""
from __future__ import annotations

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

COULEUR_ENTETE = "1F4E78"
COULEUR_CRITIQUE = "FF0000"
COULEUR_SURVEILLER = "FFC000"
COULEUR_CONFORME = "00B050"


def _police(**kwargs) -> Font:
    return Font(name="Segoe UI", **kwargs)


def _remplissage(couleur: str) -> PatternFill:
    return PatternFill(start_color=couleur, end_color=couleur, fill_type="solid")


def _bordure() -> Border:
    cote = Side(style="thin", color="D9D9D9")
    return Border(left=cote, right=cote, top=cote, bottom=cote)


def ecrire_excel(
    par_region: dict[str, pd.DataFrame],
    chemin_sortie: str,
    seuil_critique: float,
    seuil_conforme: float,
) -> None:
    with pd.ExcelWriter(chemin_sortie, engine="openpyxl") as writer:
        for nom_region, df in par_region.items():
            df.to_excel(writer, sheet_name=nom_region[:31], index=False)

    classeur = load_workbook(chemin_sortie)
    for feuille in classeur.worksheets:
        nb_lignes, nb_colonnes = feuille.max_row, feuille.max_column
        feuille.row_dimensions[1].height = 28

        for c in range(1, nb_colonnes + 1):
            cellule = feuille.cell(1, c)
            cellule.font = _police(size=11, bold=True, color="FFFFFF")
            cellule.fill = _remplissage(COULEUR_ENTETE)
            cellule.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cellule.border = _bordure()

        for r in range(2, nb_lignes + 1):
            feuille.row_dimensions[r].height = 20
            for c in range(1, nb_colonnes + 1):
                cellule = feuille.cell(r, c)
                cellule.font = _police(size=10)
                cellule.border = _bordure()
                cellule.alignment = Alignment(
                    horizontal="left" if c == 1 else "center",
                    vertical="center",
                    wrap_text=(c == 1),
                )
                if c >= 3 and isinstance(cellule.value, (int, float)):
                    cellule.number_format = "0.0"
                    if cellule.value < seuil_critique:
                        cellule.fill = _remplissage(COULEUR_CRITIQUE)
                        cellule.font = _police(size=10, bold=True, color="FFFFFF")
                    elif cellule.value < seuil_conforme:
                        cellule.fill = _remplissage(COULEUR_SURVEILLER)
                        cellule.font = _police(size=10, bold=True, color="000000")
                    else:
                        cellule.fill = _remplissage(COULEUR_CONFORME)
                        cellule.font = _police(size=10, bold=True, color="FFFFFF")

        # Fusionne verticalement les cellules de district répétées (colonne 1)
        r = 2
        while r <= nb_lignes:
            valeur, fin = feuille.cell(r, 1).value, r
            while fin + 1 <= nb_lignes and feuille.cell(fin + 1, 1).value == valeur:
                fin += 1
            if fin > r and valeur is not None:
                for k in range(r + 1, fin + 1):
                    feuille.cell(k, 1).value = None
                feuille.merge_cells(start_row=r, start_column=1, end_row=fin, end_column=1)
            r = fin + 1

        for c in range(1, nb_colonnes + 1):
            largeur_max = max(len(str(feuille.cell(r, c).value or "")) for r in range(1, nb_lignes + 1))
            feuille.column_dimensions[get_column_letter(c)].width = min(max(largeur_max + 3, 12), 30)

    classeur.save(chemin_sortie)
