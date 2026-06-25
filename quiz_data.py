"""Încărcarea și validarea grilelor din fișierele JSON.

Fiecare materie are propriul fișier JSON în directorul ``data/``.
Pentru a adăuga o materie nouă este suficient să creezi un fișier nou
``data/nume_materie.json`` cu aceeași structură (vezi README.md).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / "data"

LITERE = ["a", "b", "c"]


def litera_la_index(litera: str) -> int:
    """Transformă litera răspunsului ('a'/'b'/'c') în index (0/1/2)."""
    return LITERE.index(str(litera).strip().lower())


def index_la_litera(index: int) -> str:
    """Transformă indexul (0/1/2) în litera răspunsului ('a'/'b'/'c')."""
    return LITERE[index]


def _valideaza_intrebare(intrebare: dict[str, Any], fisier: str) -> None:
    """Verifică structura unei grile și ridică o eroare clară dacă e invalidă."""
    obligatorii = {"id", "intrebare", "raspunsuri", "corect"}
    lipsa = obligatorii - intrebare.keys()
    if lipsa:
        raise ValueError(f"{fisier}: grilă fără câmpurile {sorted(lipsa)}: {intrebare}")

    raspunsuri = intrebare["raspunsuri"]
    if not isinstance(raspunsuri, list) or len(raspunsuri) != 3:
        raise ValueError(
            f"{fisier}: grila '{intrebare['id']}' trebuie să aibă exact 3 răspunsuri."
        )

    corect = str(intrebare["corect"]).strip().lower()
    if corect not in LITERE:
        raise ValueError(
            f"{fisier}: grila '{intrebare['id']}' are răspunsul corect invalid "
            f"(trebuie 'a', 'b' sau 'c')."
        )


def incarca_materii(data_dir: Path = DATA_DIR) -> dict[str, list[dict[str, Any]]]:
    """Returnează un dicționar {nume_materie: [grile]} din toate fișierele JSON.

    Materiile sunt sortate alfabetic pentru o afișare stabilă.
    """
    materii: dict[str, list[dict[str, Any]]] = {}

    for fisier in sorted(data_dir.glob("*.json")):
        with fisier.open(encoding="utf-8") as f:
            continut = json.load(f)

        nume = continut.get("materie", fisier.stem).strip()
        intrebari = continut.get("intrebari", [])

        for intrebare in intrebari:
            _valideaza_intrebare(intrebare, fisier.name)

        if intrebari:
            materii[nume] = intrebari

    return materii


def valideaza_materie(continut: Any, sursa: str = "fișier") -> None:
    """Validează structura completă a unei materii (dict cu materie + intrebari)."""
    if not isinstance(continut, dict):
        raise ValueError(f"{sursa}: conținutul trebuie să fie un obiect JSON.")
    if "materie" not in continut or not str(continut["materie"]).strip():
        raise ValueError(f"{sursa}: lipsește câmpul 'materie'.")
    intrebari = continut.get("intrebari")
    if not isinstance(intrebari, list) or not intrebari:
        raise ValueError(f"{sursa}: 'intrebari' trebuie să fie o listă ne-vidă.")
    for intrebare in intrebari:
        _valideaza_intrebare(intrebare, sursa)


def nume_fisier_sigur(nume: str) -> str:
    """Transformă un nume în nume de fișier sigur (fără traversare de cale).

    Păstrează doar litere, cifre, cratimă și underscore; adaugă extensia .json.
    """
    baza = nume.strip().lower()
    if baza.endswith(".json"):
        baza = baza[:-5]
    # înlocuiește diacriticele uzuale românești
    inlocuiri = {"ă": "a", "â": "a", "î": "i", "ș": "s", "ş": "s", "ț": "t", "ţ": "t"}
    for vechi, nou in inlocuiri.items():
        baza = baza.replace(vechi, nou)
    sigur = "".join(c if (c.isalnum() or c in "-_") else "_" for c in baza)
    sigur = sigur.strip("_") or "materie"
    return f"{sigur}.json"


def salveaza_materie(
    nume_fisier: str, continut: dict[str, Any], data_dir: Path = DATA_DIR
) -> Path:
    """Validează și salvează o materie într-un fișier JSON din ``data_dir``.

    Numele fișierului este igienizat pentru a preveni traversarea de cale.
    """
    valideaza_materie(continut, nume_fisier)
    fisier_curat = nume_fisier_sigur(nume_fisier)
    cale = (data_dir / fisier_curat).resolve()
    # protecție: fișierul trebuie să rămână în interiorul directorului data/
    if data_dir.resolve() not in cale.parents:
        raise ValueError("Cale de fișier invalidă.")
    data_dir.mkdir(parents=True, exist_ok=True)
    cale.write_text(
        json.dumps(continut, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return cale


def sterge_materie(nume_fisier: str, data_dir: Path = DATA_DIR) -> None:
    """Șterge un fișier de materie din ``data_dir`` (cu protecție de cale)."""
    fisier_curat = nume_fisier_sigur(nume_fisier)
    cale = (data_dir / fisier_curat).resolve()
    if data_dir.resolve() not in cale.parents:
        raise ValueError("Cale de fișier invalidă.")
    if cale.exists():
        cale.unlink()
