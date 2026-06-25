"""Aplicație de grile pentru examenul de medicină veterinară.

Rulare locală:
    streamlit run app.py
"""

from __future__ import annotations

import html
import json
import random
import time

import streamlit as st

from auth import (
    MAX_INCERCARI,
    OTP_TTL,
    email_admin,
    genereaza_cod,
    masca_email,
    otp_debug,
    trimite_email_cod,
)
from quiz_data import (
    DATA_DIR,
    incarca_materii,
    index_la_litera,
    nume_fisier_sigur,
    salveaza_materie,
    sterge_materie,
    valideaza_materie,
)

st.set_page_config(
    page_title="Grile Medicină Veterinară",
    page_icon="🐾",
    layout="centered",
    initial_sidebar_state="collapsed",
)

CSS_TEMPLATE = """
<style>
:root {{
  --bg: {bg};
  --card: {card};
  --border: {border};
  --text: {text};
  --muted: {muted};
  --soft: {soft};
  --primary: {primary};
  --primary_soft: {primary_soft};
  --correct_bg: {correct_bg};
  --correct_border: {correct_border};
  --wrong_bg: {wrong_bg};
  --wrong_border: {wrong_border};
}}

/* --- suprafete principale --- */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {{
  background-color: var(--bg) !important;
}}
header[data-testid="stHeader"] {{ background: transparent !important; }}
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {{ background-color: var(--soft) !important; }}
.block-container {{ padding-top: 2rem; padding-bottom: 4rem; max-width: 720px; }}

/* --- text --- */
.stApp, .stMarkdown, p, label, li, h1, h2, h3, h4, h5,
strong, b, em,
[data-testid="stWidgetLabel"] *,
[data-testid="stMetricValue"], [data-testid="stMetricLabel"],
[data-testid="stMetricDelta"] {{ color: var(--text) !important; }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *,
small {{ color: var(--muted) !important; }}

/* --- cardul intrebarii --- */
.question-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.3rem 1.5rem;
  margin-bottom: 1.1rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}}
.question-card h4 {{ color: var(--text) !important; }}
.materie-tag {{
  display: inline-block; background: var(--primary); color: #fff !important;
  font-size: 0.7rem; font-weight: 700; letter-spacing: .04em;
  padding: 0.22rem 0.7rem; border-radius: 999px; margin-bottom: 0.6rem;
  text-transform: uppercase;
}}

/* --- butoane (raspunsuri + actiuni) --- */
.stButton > button,
[data-testid="stFormSubmitButton"] > button,
[data-testid="stBaseButton-secondaryFormSubmit"],
[data-testid="baseButton-secondaryFormSubmit"] {{
  border-radius: 14px !important;
  padding: 0.85rem 1.05rem !important;
  font-weight: 600 !important;
  text-align: left;
  border: 1px solid var(--border) !important;
  background: var(--soft) !important;
  color: var(--text) !important;
  white-space: normal;
  line-height: 1.4;
  transition: all 0.12s ease-in-out;
}}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {{
  border-color: var(--primary) !important;
  background: var(--primary_soft) !important;
  color: var(--text) !important;
}}
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"],
.stButton > button[data-testid="stBaseButton-primary"],
[data-testid="stFormSubmitButton"] > button[kind="primary"],
[data-testid="stBaseButton-primaryFormSubmit"],
[data-testid="baseButton-primaryFormSubmit"] {{
  background: var(--primary) !important;
  border-color: var(--primary) !important;
  color: #fff !important;
}}
.stButton > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {{
  filter: brightness(1.08); color: #fff !important;
}}
/* butoane din sidebar: centrate */
section[data-testid="stSidebar"] .stButton > button {{ text-align: center; }}

/* --- carduri de raspuns dezvaluit (feedback) --- */
.ans {{
  border-radius: 14px; padding: 0.8rem 1rem; margin-bottom: 0.55rem;
  border: 1px solid var(--border); background: var(--soft); color: var(--text);
  display: flex; gap: 0.75rem; align-items: center; line-height: 1.4;
}}
.ans .lit {{
  flex: none; width: 1.8rem; height: 1.8rem; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.85rem; background: var(--card); color: var(--text);
}}
.ans.correct {{ background: var(--correct_bg); border-color: var(--correct_border); }}
.ans.correct .lit {{ background: var(--correct_border); color: #fff; }}
.ans.wrong {{ background: var(--wrong_bg); border-color: var(--wrong_border); }}
.ans.wrong .lit {{ background: var(--wrong_border); color: #fff; }}

/* --- componente native --- */
div[data-testid="stForm"] {{
  background: var(--card) !important; border: 1px solid var(--border) !important;
  border-radius: 16px;
}}
details[data-testid="stExpander"],
[data-testid="stExpander"] > details,
[data-testid="stExpander"] details {{
  background: transparent !important; border: 1px solid var(--border) !important;
  border-radius: 14px;
}}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary > div,
[data-testid="stExpander"] summary div,
[data-testid="stExpanderHeader"],
.streamlit-expanderHeader {{
  background: var(--soft) !important; color: var(--text) !important;
  border-radius: 12px;
}}
[data-testid="stExpander"] [data-testid="stExpanderDetails"],
[data-testid="stExpanderDetails"] {{ background: transparent !important; }}
[data-testid="stExpander"] summary:hover {{ color: var(--primary) !important; }}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpanderToggleIcon"] {{ color: var(--text) !important; }}

[data-testid="stTickBarMin"], [data-testid="stTickBarMax"],
[data-testid="stThumbValue"] {{ color: var(--muted) !important; }}

[data-baseweb="input"], [data-baseweb="base-input"],
[data-baseweb="textarea"], [data-baseweb="select"] > div {{
  background: var(--card) !important; color: var(--text) !important;
  border-color: var(--border) !important;
}}
[data-baseweb="base-input"] input, [data-baseweb="textarea"] textarea {{
  background: var(--card) !important; color: var(--text) !important;
}}

div[role="radiogroup"] label {{
  background: var(--card) !important; border: 1px solid var(--border) !important;
  border-radius: 12px; padding: 0.7rem 0.9rem; margin-bottom: 0.5rem; width: 100%;
}}
div[role="radiogroup"] label:hover {{ border-color: var(--primary) !important; }}
div[role="radiogroup"] label p {{ color: var(--text) !important; }}

[data-testid="stAlert"] {{ border-radius: 12px; }}
[data-baseweb="tab-list"] button {{ color: var(--text) !important; }}

section[data-testid="stSidebar"] * {{ color: var(--text); }}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {{
  color: var(--muted) !important;
}}
</style>
"""

TEMA_LIGHT = dict(
    bg="#ffffff", card="#ffffff", border="#e1e5ea", text="#1b1b1b",
    muted="#5f6b7a", soft="#f1f4f8", primary="#2e7d32", primary_soft="#eaf4ea",
    correct_bg="#e7f6e9", correct_border="#2e9e4f",
    wrong_bg="#fdebec", wrong_border="#e0414e",
)
TEMA_DARK = dict(
    bg="#0e1117", card="#1a1f2b", border="#2a3142", text="#e6e9ef",
    muted="#9aa4b2", soft="#161b26", primary="#4caf50", primary_soft="#1d2b22",
    correct_bg="#16301f", correct_border="#3fae5e",
    wrong_bg="#341a1e", wrong_border="#e0556a",
)


def inject_css(dark: bool) -> None:
    tema = TEMA_DARK if dark else TEMA_LIGHT
    st.markdown(CSS_TEMPLATE.format(**tema), unsafe_allow_html=True)


@st.cache_data
def get_materii() -> dict[str, list[dict]]:
    return incarca_materii()


def init_state() -> None:
    st.session_state.setdefault("etapa", "configurare")
    st.session_state.setdefault("mod", "examen")
    st.session_state.setdefault("dark", False)
    st.session_state.setdefault("admin", False)
    st.session_state.setdefault("otp_cod", None)
    st.session_state.setdefault("otp_exp", 0.0)
    st.session_state.setdefault("otp_incercari", 0)
    st.session_state.setdefault("intrebari", [])
    st.session_state.setdefault("index", 0)
    st.session_state.setdefault("raspunsuri_user", {})


def cere_cod_email() -> None:
    """Generează și trimite un cod pe email; salvează-l în sesiune."""
    destinatar = email_admin()
    if not destinatar:
        st.error("Nu e setată adresa de email (admin_email în secrets.toml).")
        return
    cod = genereaza_cod()
    try:
        trimite_email_cod(destinatar, cod)
    except Exception:
        if otp_debug():
            st.session_state.otp_cod = cod
            st.session_state.otp_exp = time.time() + OTP_TTL
            st.session_state.otp_incercari = 0
            st.warning(f"Email neconfigurat (mod debug). Codul tău: **{cod}**")
            return
        st.error("Nu am putut trimite emailul. Verifică setările SMTP.")
        return
    st.session_state.otp_cod = cod
    st.session_state.otp_exp = time.time() + OTP_TTL
    st.session_state.otp_incercari = 0
    st.success(f"Cod trimis la {masca_email(destinatar)}. Verifică emailul.")


def verifica_cod(introdus: str) -> None:
    """Validează codul introdus și autentifică adminul dacă e corect."""
    if not st.session_state.otp_cod:
        st.error("Cere mai întâi un cod.")
        return
    if time.time() > st.session_state.otp_exp:
        st.error("Codul a expirat. Cere unul nou.")
        return
    if st.session_state.otp_incercari >= MAX_INCERCARI:
        st.error("Prea multe încercări. Cere un cod nou.")
        return
    if introdus.strip() == st.session_state.otp_cod:
        st.session_state.admin = True
        st.session_state.otp_cod = None
        st.rerun()
    else:
        st.session_state.otp_incercari += 1
        ramase = MAX_INCERCARI - st.session_state.otp_incercari
        st.error(f"Cod greșit. Încercări rămase: {ramase}.")


def porneste_test(
    selectie: dict[str, int], materii: dict[str, list[dict]], mod: str
) -> None:
    """Construiește lista de grile aleatorii pe baza selecției pe materii."""
    intrebari: list[dict] = []
    for nume, nr in selectie.items():
        disponibile = materii.get(nume, [])
        alese = random.sample(disponibile, min(nr, len(disponibile)))
        for grila in alese:
            intrebari.append({**grila, "materie": nume})

    random.shuffle(intrebari)
    st.session_state.intrebari = intrebari
    st.session_state.index = 0
    st.session_state.raspunsuri_user = {}
    st.session_state.mod = mod
    st.session_state.etapa = "test"


def reset() -> None:
    st.session_state.etapa = "configurare"
    st.session_state.intrebari = []
    st.session_state.index = 0
    st.session_state.raspunsuri_user = {}


# ---------------------------------------------------------------- componente


def card_intrebare(grila: dict) -> None:
    st.markdown(
        f"<div class='question-card'>"
        f"<span class='materie-tag'>{html.escape(grila['materie'])}</span>"
        f"<h4 style='margin:0'>{html.escape(grila['intrebare'])}</h4>"
        f"</div>",
        unsafe_allow_html=True,
    )


def optiuni_selectie(grila: dict, idx: int) -> None:
    """Afișează răspunsurile ca butoane A/B/C; reține alegerea curentă."""
    ales = st.session_state.raspunsuri_user.get(idx)
    for j, text in enumerate(grila["raspunsuri"]):
        litera = index_la_litera(j)
        eticheta = f"{litera.upper()}.  {text}"
        tip = "primary" if ales == litera else "secondary"
        if st.button(
            eticheta, key=f"opt_{idx}_{j}", use_container_width=True, type=tip
        ):
            st.session_state.raspunsuri_user[idx] = litera
            st.rerun()


def feedback_raspuns(grila: dict, idx: int) -> None:
    """Afișează răspunsurile colorate (corect/greșit) + explicația."""
    ales = st.session_state.raspunsuri_user.get(idx)
    corect = grila["corect"]
    blocuri = ""
    for j, text in enumerate(grila["raspunsuri"]):
        litera = index_la_litera(j)
        cls = "correct" if litera == corect else "wrong" if litera == ales else ""
        blocuri += (
            f"<div class='ans {cls}'>"
            f"<div class='lit'>{litera.upper()}</div>"
            f"<div>{html.escape(text)}</div></div>"
        )
    st.markdown(blocuri, unsafe_allow_html=True)

    if ales == corect:
        st.success("Răspuns corect! ✅")
    else:
        st.error(f"Greșit. Răspunsul corect este **{corect.upper()}**.")
    if grila.get("explicatie"):
        st.info(grila["explicatie"])


# ---------------------------------------------------------------- ecrane


def ecran_configurare(materii: dict[str, list[dict]]) -> None:
    st.title("🐾 Grile Medicină Veterinară")
    st.caption("Alege modul de lucru și câte grile vrei de la fiecare materie.")

    if not materii:
        st.warning("Nu există grile. Adaugă fișiere JSON în directorul `data/`.")
        return

    mod_label = st.radio(
        "Mod de lucru",
        ["📝 Examen — răspunsuri la final", "⚡ Antrenament — răspuns imediat"],
        horizontal=False,
    )
    mod = "examen" if mod_label.startswith("📝") else "antrenament"

    selectie: dict[str, int] = {}
    with st.form("config"):
        for nume, intrebari in materii.items():
            total = len(intrebari)
            selectie[nume] = st.slider(
                f"{nume}  ·  {total} grile disponibile",
                min_value=0,
                max_value=total,
                value=min(3, total),
            )
        trimis = st.form_submit_button(
            "Începe ▶", use_container_width=True, type="primary"
        )

    total_ales = sum(selectie.values())
    st.info(f"Total grile selectate: **{total_ales}**")

    if trimis:
        if total_ales == 0:
            st.error("Selectează cel puțin o grilă pentru a începe.")
        else:
            porneste_test(selectie, materii, mod)
            st.rerun()


def ecran_test() -> None:
    intrebari = st.session_state.intrebari
    idx = st.session_state.index
    total = len(intrebari)
    grila = intrebari[idx]
    mod = st.session_state.mod

    st.progress(idx / total, text=f"Grila {idx + 1} din {total}")
    card_intrebare(grila)

    if mod == "examen":
        optiuni_selectie(grila, idx)
        col1, _, col3 = st.columns([1, 1, 1])
        with col1:
            if idx > 0 and st.button("◀ Înapoi", use_container_width=True):
                st.session_state.index -= 1
                st.rerun()
        with col3:
            if idx < total - 1:
                if st.button("Următoarea ▶", use_container_width=True, type="primary"):
                    st.session_state.index += 1
                    st.rerun()
            elif st.button("Finalizează ✔", use_container_width=True, type="primary"):
                st.session_state.etapa = "rezultate"
                st.rerun()
    else:  # antrenament — răspuns imediat
        if idx in st.session_state.raspunsuri_user:
            feedback_raspuns(grila, idx)
            if idx < total - 1:
                if st.button("Următoarea ▶", use_container_width=True, type="primary"):
                    st.session_state.index += 1
                    st.rerun()
            elif st.button("Vezi rezultatele ✔", use_container_width=True, type="primary"):
                st.session_state.etapa = "rezultate"
                st.rerun()
        else:
            optiuni_selectie(grila, idx)


def ecran_rezultate() -> None:
    intrebari = st.session_state.intrebari
    raspunsuri = st.session_state.raspunsuri_user
    total = len(intrebari)
    corecte = sum(
        1 for i, g in enumerate(intrebari) if raspunsuri.get(i) == g["corect"]
    )
    procent = corecte / total * 100 if total else 0

    st.title("Rezultate")
    st.metric("Scor", f"{corecte} / {total}", f"{procent:.0f}%")
    st.progress(procent / 100)

    if procent >= 50:
        st.success("Felicitări! Ai trecut testul. 🎉")
    else:
        st.warning("Mai exersează. Revezi grilele greșite mai jos.")

    st.divider()
    st.subheader("Recapitulare")

    for i, grila in enumerate(intrebari):
        ales = raspunsuri.get(i)
        corect = grila["corect"]
        e_corect = ales == corect

        with st.expander(
            f"{'✅' if e_corect else '❌'} Grila {i + 1} · {grila['materie']}",
            expanded=not e_corect,
        ):
            st.markdown(f"**{grila['intrebare']}**")
            for j, text in enumerate(grila["raspunsuri"]):
                litera = index_la_litera(j).upper()
                if litera.lower() == corect:
                    st.markdown(f"- ✅ **{litera}. {text}** (răspuns corect)")
                elif litera.lower() == ales:
                    st.markdown(f"- ❌ {litera}. {text} (răspunsul tău)")
                else:
                    st.markdown(f"- {litera}. {text}")
            if grila.get("explicatie"):
                st.info(grila["explicatie"])

    st.divider()
    if st.button("🔄 Test nou", use_container_width=True, type="primary"):
        reset()
        st.rerun()


def bara_laterala(materii: dict[str, list[dict]]) -> None:
    """Conținutul barei laterale, afișat pe toate ecranele."""
    with st.sidebar:
        st.markdown("## 🐾 Grile Vet")
        st.caption("Pregătire pentru examenul de medicină veterinară")

        st.session_state.dark = st.toggle(
            "🌙 Mod întunecat", value=st.session_state.dark
        )

        if st.session_state.etapa == "test":
            st.divider()
            total = len(st.session_state.intrebari)
            raspunse = len(st.session_state.raspunsuri_user)
            idx = st.session_state.index
            etichete_mod = {"examen": "📝 Examen", "antrenament": "⚡ Antrenament"}
            st.markdown("### ▶ Test în desfășurare")
            st.write(f"Mod: **{etichete_mod.get(st.session_state.mod)}**")
            st.write(f"Grila curentă: **{idx + 1}/{total}**")
            st.write(f"Răspunse: **{raspunse}/{total}**")
            if st.button("✖ Renunță la test", use_container_width=True):
                reset()
                st.rerun()

        st.divider()
        with st.expander("ℹ️ Cum funcționează"):
            st.markdown(
                "- **Examen** — răspunzi la toate grilele, vezi scorul la final.\n"
                "- **Antrenament** — afli imediat dacă ai greșit, cu explicație.\n"
                "- Răspunsurile sunt marcate **A**, **B**, **C**.\n"
                "- Ordinea grilelor este aleatorie de fiecare dată."
            )

        with st.expander("🔐 Admin", expanded=st.session_state.admin):
            if st.session_state.admin:
                st.success("Autentificat ca admin.")
                if st.button("🛠 Panou administrare", use_container_width=True):
                    st.session_state.etapa = "admin"
                    st.rerun()
                if st.button("Deconectare", use_container_width=True):
                    st.session_state.admin = False
                    if st.session_state.etapa == "admin":
                        st.session_state.etapa = "configurare"
                    st.rerun()
            else:
                st.caption("Acces protejat prin cod trimis pe email.")
                if st.button("✉️ Trimite cod pe email", use_container_width=True):
                    cere_cod_email()
                cod = st.text_input("Cod primit", key="otp_input")
                if st.button("Verifică codul", use_container_width=True):
                    verifica_cod(cod)

        st.caption("v1.0 · date demonstrative")


TEMPLATE_MATERIE = """{
  "materie": "Nume materie",
  "intrebari": [
    {
      "id": "abc-001",
      "intrebare": "Textul întrebării?",
      "raspunsuri": ["Varianta A", "Varianta B", "Varianta C"],
      "corect": "a",
      "explicatie": "Explicație opțională."
    }
  ]
}
"""


def _salveaza_din_text(nume_fisier: str, text: str) -> None:
    """Parsează, validează și salvează conținut JSON; afișează feedback în UI."""
    try:
        continut = json.loads(text)
    except json.JSONDecodeError as e:
        st.error(f"JSON invalid: {e}")
        return
    try:
        cale = salveaza_materie(nume_fisier, continut)
    except ValueError as e:
        st.error(f"Validare eșuată: {e}")
        return
    get_materii.clear()
    st.success(f"Salvat în `{cale.name}`. Reîncarcă testul pentru a vedea grilele.")


def ecran_admin() -> None:
    if not st.session_state.admin:
        st.session_state.etapa = "configurare"
        st.rerun()

    st.title("🛠 Administrare grile")
    if st.button("← Înapoi la aplicație"):
        st.session_state.etapa = "configurare"
        st.rerun()

    tab_edit, tab_incarca = st.tabs(["✏️ Editează existente", "⬆️ Încarcă / Adaugă"])

    with tab_edit:
        fisiere = sorted(DATA_DIR.glob("*.json"))
        if not fisiere:
            st.info("Nu există fișiere în `data/`.")
        else:
            nume_sel = st.selectbox(
                "Alege fișierul", [f.name for f in fisiere], key="admin_sel"
            )
            cale = DATA_DIR / nume_sel
            continut_curent = cale.read_text(encoding="utf-8")
            text = st.text_area(
                "Conținut JSON",
                value=continut_curent,
                height=420,
                key=f"edit_{nume_sel}",
            )
            if st.button("💾 Salvează modificările", type="primary"):
                _salveaza_din_text(nume_sel, text)

            with st.expander("🗑️ Șterge acest fișier"):
                st.warning(
                    f"Ștergerea fișierului **{nume_sel}** este permanentă."
                )
                confirm = st.checkbox(f"Confirm ștergerea {nume_sel}")
                if st.button("Șterge definitiv", disabled=not confirm):
                    try:
                        sterge_materie(nume_sel)
                    except ValueError as e:
                        st.error(f"Eroare: {e}")
                    else:
                        get_materii.clear()
                        st.success(f"Fișierul `{nume_sel}` a fost șters.")
                        st.rerun()

    with tab_incarca:
        st.markdown("#### Încarcă un fișier JSON")
        fisier = st.file_uploader("Fișier .json", type=["json"], key="admin_upload")
        if fisier is not None:
            try:
                continut = json.loads(fisier.getvalue().decode("utf-8"))
                valideaza_materie(continut, fisier.name)
            except (json.JSONDecodeError, ValueError) as e:
                st.error(f"Fișier invalid: {e}")
            else:
                nr = len(continut.get("intrebari", []))
                st.success(
                    f"Materie validă: **{continut['materie']}** · {nr} grile."
                )
                nume_propus = nume_fisier_sigur(continut["materie"])
                nume_fisier = st.text_input("Salvează ca", value=nume_propus)
                if st.button("💾 Salvează fișierul încărcat", type="primary"):
                    _salveaza_din_text(nume_fisier, json.dumps(continut))

        st.divider()
        st.markdown("#### Sau creează o materie nouă")
        text_nou = st.text_area(
            "Conținut JSON", value=TEMPLATE_MATERIE, height=320, key="admin_nou"
        )
        nume_nou = st.text_input("Nume fișier nou", value="materie_noua.json")
        if st.button("💾 Creează materia"):
            _salveaza_din_text(nume_nou, text_nou)


# ---------------------------------------------------------------- main

init_state()
materii = get_materii()
bara_laterala(materii)
inject_css(st.session_state.dark)

if st.session_state.etapa == "configurare":
    ecran_configurare(materii)
elif st.session_state.etapa == "test":
    ecran_test()
elif st.session_state.etapa == "rezultate":
    ecran_rezultate()
elif st.session_state.etapa == "admin":
    ecran_admin()
