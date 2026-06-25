# 🐾 Grile Medicină Veterinară

Aplicație web pentru exersarea grilelor pentru examenul de medicină veterinară,
construită cu [Streamlit](https://streamlit.io). Funcționează atât pe desktop, cât
și pe telefon.

## Funcționalități

- Grile organizate pe materii, stocate în fișiere JSON (ușor de extins).
- Fiecare grilă are 3 răspunsuri (marcate **A / B / C**), dintre care unul corect.
- Selectezi câte grile vrei de la fiecare materie; ordinea este aleatorie.
- Două moduri de lucru:
  - **Examen** — răspunzi la toate grilele, primești rezultatul la final.
  - **Antrenament** — primești răspunsul corect imediat după fiecare grilă.
- **Mod întunecat (dark mode)** comutabil din bara laterală.
- **Login de administrator** pentru a încărca / edita fișierele JSON direct din aplicație.
- Ecran de rezultate cu scor, recapitulare și explicații.
- Design responsive, optimizat și pentru ecrane de telefon.

## Structura proiectului

```
grileVet/
├── app.py              # aplicația Streamlit (interfața)
├── quiz_data.py        # încărcarea și validarea grilelor
├── requirements.txt    # dependențe
├── .streamlit/
│   └── config.toml     # tema aplicației
└── data/               # grilele, câte un fișier JSON pe materie
    ├── anatomie.json
    ├── fiziologie.json
    ├── farmacologie.json
    └── microbiologie.json
```

## Rulare locală

```powershell
# 1. (opțional) creează un mediu virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. instalează dependențele
pip install -r requirements.txt

# 3. pornește aplicația
streamlit run app.py
```

Aplicația se deschide automat în browser la `http://localhost:8501`.

## Cum adaugi grile noi

### Adaugă grile la o materie existentă

Deschide fișierul materiei din `data/` și adaugă un obiect nou în lista
`intrebari`:

```json
{
  "id": "ana-006",
  "intrebare": "Textul întrebării?",
  "raspunsuri": ["Varianta A", "Varianta B", "Varianta C"],
  "corect": "b",
  "explicatie": "Explicație opțională afișată la recapitulare."
}
```

- `id` — identificator unic (ex. prefix materie + număr).
- `raspunsuri` — exact **3** variante (afișate ca A, B, C).
- `corect` — litera răspunsului corect: `"a"`, `"b"` sau `"c"`.
- `explicatie` — opțională.

### Adaugă o materie nouă

Creează un fișier nou `data/nume_materie.json`:

```json
{
  "materie": "Parazitologie",
  "intrebari": [
    {
      "id": "par-001",
      "intrebare": "...",
      "raspunsuri": ["...", "...", "..."],
      "corect": "a"
    }
  ]
}
```

Materia apare automat la următoarea pornire a aplicației — nu trebuie modificat codul.

## Administrare din aplicație (admin)

În bara laterală, secțiunea **🔐 Admin** protejează accesul printr-un **cod unic
trimis pe email** (2FA). După introducerea codului corect, panoul de administrare
permite:

- editarea conținutului JSON al materiilor existente;
- **ștergerea** unei materii;
- încărcarea unui fișier `.json` nou;
- crearea unei materii noi de la zero (pornind de la un șablon).

Toate modificările sunt validate înainte de salvare, iar numele fișierelor sunt
igienizate pentru a preveni traversarea de cale.

### Configurarea codului pe email (gratuit)

Trimiterea emailului folosește SMTP (gratuit cu Gmail + parolă de aplicație).
Creează fișierul `.streamlit/secrets.toml` (vezi `.streamlit/secrets.toml.example`):

```toml
admin_email   = "salajanmelisa@gmail.com"
smtp_host     = "smtp.gmail.com"
smtp_port     = 587
smtp_user     = "adresa-de-trimitere@gmail.com"
smtp_password = "parola-de-aplicatie"   # https://myaccount.google.com/apppasswords
otp_debug     = false
```

Pașii pentru parola de aplicație Gmail:
1. Activează verificarea în doi pași pe contul Google.
2. Mergi la <https://myaccount.google.com/apppasswords> și generează o parolă.
3. Pune-o la `smtp_password` (16 caractere, fără spații).

Fișierul `secrets.toml` este ignorat de git. Pe Streamlit Community Cloud, pune
aceste valori în **Settings → Secrets**.

> **Testare fără email:** dacă `otp_debug = true` și SMTP nu e completat, codul se
> afișează direct pe ecran, ca să poți testa local.

> **Atenție:** pe Streamlit Community Cloud, fișierele scrise de panoul admin sunt
> temporare (se pierd la redeploy). Pentru modificări permanente, actualizează
> fișierele JSON în repository.

## Deploy

### Streamlit Community Cloud (gratuit)

1. Urcă proiectul pe GitHub.
2. Intră pe [share.streamlit.io](https://share.streamlit.io) și conectează repo-ul.
3. Alege `app.py` ca fișier principal și apasă **Deploy**.

Aplicația devine accesibilă de pe orice dispozitiv, inclusiv telefon, printr-un link public.

> **Notă:** grilele de aici sunt mock-uri pentru testarea aplicației. Înlocuiește-le
> cu grilele reale înainte de utilizare.
