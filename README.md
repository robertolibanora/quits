# Future Wife Quiz 💍

Test di compatibilità sentimentale ironico ma serio. Misura allineamento mentale, visione, fiducia e maturità.

## Caratteristiche

- **Questionario strutturato**: 13 domande con risposte corrette e interpretative
- **Sistema di punteggio**: Calcolo automatico basato su regole precise
- **Interpretazione avanzata**: Analisi approfondita con OpenAI (opzionale)
- **Resoconto finale**: Valutazione testuale lucida e diretta
- **Database**: Salvataggio automatico di tutte le valutazioni
- **Admin panel**: Dashboard per visualizzare statistiche e valutazioni

## Installazione

1. Clona il repository:
```bash
git clone https://github.com/robertolibanora/quits.git
cd quits
```

2. Crea un ambiente virtuale:
```bash
python3 -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

3. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

4. Configura le variabili d'ambiente (opzionale, per interpretazione avanzata):
```bash
echo "OPENAI_API_KEY=your_key_here" > .env
```

5. Avvia l'applicazione:
```bash
python app.py
```

L'applicazione sarà disponibile su `http://localhost:5000`

## Admin Panel

Accesso admin: `http://localhost:5000/admin`
Password: `liba2004`

## Struttura del progetto

```
futurewife/
├── app.py                 # Applicazione Flask principale
├── database.py            # Gestione database SQLite
├── interpretation.py      # Sistema di interpretazione avanzata
├── questions.py           # Definizione domande e regole
├── requirements.txt       # Dipendenze Python
├── static/
│   ├── app.js            # Frontend JavaScript
│   └── style.css         # Stili CSS
└── templates/
    ├── index.html         # Pagina principale
    └── admin_*.html       # Pagine admin
```

## Tecnologie utilizzate

- Python 3
- Flask
- SQLite
- OpenAI API (opzionale)
- HTML/CSS/JavaScript vanilla

## Licenza

MIT
