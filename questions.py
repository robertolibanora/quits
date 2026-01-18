"""
Definizione delle domande del test di compatibilità sentimentale.
Ogni domanda ha:
- id: identificatore univoco
- text: testo della domanda
- type: "correct_answer" | "interpretive" | "open"
- options: lista di opzioni con punteggi
- correct_answer: (solo per type="correct_answer") valore corretto
- importance_multiplier: moltiplicatore per domande ad alta importanza (default 1.0)
"""

QUESTIONS = [
    {
        "id": "trust_future",
        "text": "Tra quanti anni farò il primo milione?",
        "type": "interpretive",
        "importance_multiplier": 2.0,  # La più importante
        "options": {
            "1_2_anni": {"points": 12, "label": "1-2 anni"},
            "gia_successo": {"points": -10, "label": "Già successo"},
            "ci_sono_nato": {"points": -15, "label": "Ci sono nato/a"},
            "5_10_anni": {"points": 6, "label": "5-10 anni"},
        }
    },
    {
        "id": "family_size",
        "text": "Quanti siamo in famiglia?",
        "type": "correct_answer",
        "correct_answer": "5",
        "options": {
            "3": {"points": 0, "label": "3"},
            "5": {"points": 8, "label": "5"},
            "4": {"points": 0, "label": "4"},
            "6": {"points": 0, "label": "6"},
        }
    },
    {
        "id": "how_die",
        "text": "Come vorrei morire",
        "type": "correct_answer",
        "correct_answer": "ferrari_70",
        "options": {
            "nel_sonno": {"points": 0, "label": "Nel sonno"},
            "sereno_affetti": {"points": 0, "label": "Sereno, circondato dagli affetti"},
            "attico_mare": {"points": 0, "label": "In un attico vista mare"},
            "ferrari_70": {"points": 8, "label": "Su una Ferrari a 70 anni"},
        }
    },
    {
        "id": "company_name",
        "text": "Come si chiama l'azienda dove vado a lavorare?",
        "type": "correct_answer",
        "correct_answer": "kpmg",
        "options": {
            "deloitte": {"points": 0, "label": "Deloitte"},
            "accenture": {"points": 0, "label": "Accenture"},
            "pwc": {"points": 0, "label": "PwC"},
            "kpmg": {"points": 8, "label": "KPMG"},
        }
    },
    {
        "id": "mare_montagna",
        "text": "Mare o montagna?",
        "type": "correct_answer",
        "correct_answer": "spiaggia",
        "options": {
            "montagna": {"points": 0, "label": "Montagna"},
            "dipende": {"points": 0, "label": "Dipende"},
            "montagna_spa": {"points": 0, "label": "Montagna con spa"},
            "spiaggia": {"points": 8, "label": "Spiaggia"},
        }
    },
    {
        "id": "wife_job",
        "text": "Che lavoro deve fare mia moglie?",
        "type": "correct_answer",
        "correct_answer": "direttrice",
        "options": {
            "cassiera_prix": {"points": 0, "label": "Cassiera del Prix"},
            "casalinga": {"points": 0, "label": "Casalinga"},
            "direttrice": {"points": 8, "label": "Direttrice"},
            "avvocato": {"points": 0, "label": "Avvocato"},
            "infermiera": {"points": 0, "label": "Infermiera"},
        }
    },
    {
        "id": "vacation_type",
        "text": "Che tipo di vacanza farei con mia moglie?",
        "type": "correct_answer",
        "correct_answer": "miami_lowcost",
        "options": {
            "ibiza_10": {"points": 0, "label": "Ibiza, 10 giorni"},
            "amsterdam": {"points": 0, "label": "Amsterdam"},
            "asia": {"points": 0, "label": "Asia"},
            "miami_lowcost": {"points": 8, "label": "Volo low cost + hotel 3 stelle a Miami"},
        }
    },
    {
        "id": "historical_figure",
        "text": "Personaggio storico che stimo di più",
        "type": "correct_answer",
        "correct_answer": "berlusconi",
        "options": {
            "berlusconi": {"points": 8, "label": "Silvio Berlusconi"},
            "trump": {"points": 0, "label": "Donald Trump"},
            "mussolini": {"points": -4, "label": "Benito Mussolini"},
            "signorini": {"points": 0, "label": "Alfonso Signorini"},
            "corona": {"points": 0, "label": "Fabrizio Corona"},
        }
    },
    {
        "id": "money_relationship",
        "text": "Il mio rapporto con i soldi è:",
        "type": "correct_answer",
        "correct_answer": "investo",
        "options": {
            "sboccio_malibu": {"points": 0, "label": "Sboccio al Malibu"},
            "investo": {"points": 8, "label": "Investo"},
            "viaggio": {"points": 0, "label": "Viaggio"},
            "mignotte_cocaina": {"points": -4, "label": "Mignotte e cocaina"},
        }
    },
    {
        "id": "attractive_woman",
        "text": "Una donna che mi attrae davvero è:",
        "type": "correct_answer",
        "correct_answer": "intelligente_carattere",
        "options": {
            "tettona": {"points": 0, "label": "Tettona"},
            "intelligente_carattere": {"points": 8, "label": "Intelligente, con carattere"},
            "sensibile": {"points": 0, "label": "Sensibile"},
            "ignorante": {"points": -4, "label": "Ignorante"},
        }
    },
    {
        "id": "where_live",
        "text": "Dove vorrei vivere:",
        "type": "correct_answer",
        "correct_answer": "porto_viro",
        "options": {
            "miami": {"points": 0, "label": "Miami"},
            "porto_viro": {"points": 8, "label": "Porto Viro"},
            "roma": {"points": 0, "label": "Roma"},
            "sempre_viaggio": {"points": 0, "label": "Sempre in viaggio"},
        }
    },
    {
        "id": "rich_priority",
        "text": "Se un giorno divento molto ricco, la mia priorità sarà:",
        "type": "correct_answer",
        "importance_multiplier": 2.0,  # Ultime due valgono ×2
        "correct_answer": "aumentare_livello",
        "options": {
            "farlo_vedere": {"points": 0, "label": "Farlo vedere"},
            "vendicarmi": {"points": 0, "label": "Vendicarmi di chi non credeva in me"},
            "smettere_lavorare": {"points": 0, "label": "Smettere di lavorare"},
            "aumentare_livello": {"points": 8, "label": "Aumentare il livello del gioco, non il rumore"},
        }
    },
    {
        "id": "representative_phrase",
        "text": "La frase che mi rappresenta di più è:",
        "type": "correct_answer",
        "importance_multiplier": 2.0,  # Ultime due valgono ×2
        "correct_answer": "costruisco_fatica",
        "options": {
            "vediamo_come_va": {"points": 0, "label": "\"Vediamo come va\""},
            "meglio_non_pensarci": {"points": 0, "label": "\"Meglio non pensarci troppo\""},
            "costruisco_fatica": {"points": 8, "label": "\"Costruisco, anche se costa fatica\""},
            "importante_divertirsi": {"points": 0, "label": "\"L'importante è divertirsi\""},
        }
    },
]

# Domande aperte (non hanno punteggio ma vengono analizzate per red flags)
OPEN_QUESTIONS = [
    {
        "id": "why_us",
        "text": "Perché io e te funzioneremmo davvero?",
        "required": True
    },
    {
        "id": "non_negotiables",
        "text": "C'è qualcosa che dovrei sapere (limiti, bisogni, non negoziabili)?",
        "required": False
    }
]
