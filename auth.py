"""Autentificare admin prin cod unic (OTP) trimis pe email.

Folosește SMTP (gratuit, ex. Gmail cu parolă de aplicație). Datele de conectare
se citesc din ``.streamlit/secrets.toml``:

    admin_email   = "destinatarul codului"
    smtp_host     = "smtp.gmail.com"
    smtp_port     = 587
    smtp_user     = "adresa.de.trimitere@gmail.com"
    smtp_password = "parola-de-aplicatie"
    otp_debug     = true   # opțional: afișează codul pe ecran pentru testare locală
"""

from __future__ import annotations

import secrets as pysecrets
import smtplib
import ssl
from email.message import EmailMessage

import streamlit as st

OTP_TTL = 300  # valabilitatea codului, în secunde (5 minute)
MAX_INCERCARI = 5


def email_admin() -> str:
    """Adresa de email pe care se trimite codul (din secrets)."""
    try:
        return str(st.secrets["admin_email"]).strip()
    except Exception:
        return ""


def otp_debug() -> bool:
    """Dacă e activ, codul e afișat pe ecran când emailul nu e configurat."""
    try:
        return bool(st.secrets["otp_debug"])
    except Exception:
        return False


def _smtp_config() -> dict | None:
    try:
        return {
            "host": str(st.secrets["smtp_host"]),
            "port": int(st.secrets["smtp_port"]),
            "user": str(st.secrets["smtp_user"]),
            "password": str(st.secrets["smtp_password"]),
        }
    except Exception:
        return None


def genereaza_cod() -> str:
    """Cod numeric de 6 cifre, generat criptografic."""
    return f"{pysecrets.randbelow(1_000_000):06d}"


def masca_email(adresa: str) -> str:
    """Maschează adresa pentru afișare: ``sa***@gmail.com``."""
    if "@" not in adresa:
        return adresa
    local, domeniu = adresa.split("@", 1)
    vizibil = local[:2]
    return f"{vizibil}***@{domeniu}"


def trimite_email_cod(destinatar: str, cod: str) -> None:
    """Trimite codul prin SMTP. Ridică ``RuntimeError`` dacă nu e configurat."""
    cfg = _smtp_config()
    if not cfg or not cfg["user"] or not cfg["password"]:
        raise RuntimeError("SMTP neconfigurat")

    mesaj = EmailMessage()
    mesaj["Subject"] = "Cod administrare · Grile Vet"
    mesaj["From"] = cfg["user"]
    mesaj["To"] = destinatar
    mesaj.set_content(
        f"Codul tău de acces la administrarea grilelor este: {cod}\n\n"
        f"Codul expiră în {OTP_TTL // 60} minute.\n"
        "Dacă nu ai cerut tu acest cod, ignoră acest mesaj."
    )

    context = ssl.create_default_context()
    with smtplib.SMTP(cfg["host"], cfg["port"], timeout=20) as server:
        server.starttls(context=context)
        server.login(cfg["user"], cfg["password"])
        server.send_message(mesaj)
