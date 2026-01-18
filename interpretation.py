"""
Sistema di interpretazione avanzata usando OpenAI per analizzare le risposte.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Client OpenAI inizializzato lazy (solo quando necessario)
_client = None

def get_client():
    """Ottiene il client OpenAI, inizializzandolo solo se necessario."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI
                _client = OpenAI(api_key=api_key)
            except Exception as e:
                print(f"Errore nell'inizializzazione del client OpenAI: {e}")
                _client = False  # Marca come non disponibile
    return _client if _client else None

SYSTEM_PROMPT = """
Sei un valutatore di compatibilità sentimentale ironico ma serio.
Il test misura allineamento mentale, visione, fiducia e maturità.

NON giudicare moralmente.
NON usare criteri discriminatori.
NON fare diagnosi psicologiche.
Valuta solo COMPATIBILITÀ con il soggetto.

Il soggetto ha:
- forte ambizione
- mentalità costruttiva
- bisogno di autonomia + rispetto
- visione a lungo termine
- intolleranza per superficialità, caos emotivo, interesse strumentale

TONO: ironico ma intelligente, diretto, mai offensivo, mai compiacente.
Stile: "lucido, adulto, selettivo".
"""

def generate_interpretation(evaluation_data: dict, answers: dict) -> str:
    """
    Genera un'interpretazione avanzata delle risposte usando OpenAI.
    
    Args:
        evaluation_data: Dati della valutazione (score, indici, etc.)
        answers: Dizionario con tutte le risposte (incluse quelle aperte)
    
    Returns:
        Testo dell'interpretazione avanzata
    """
    client = get_client()
    if not client:
        return None
    
    why_us = answers.get("why_us", "").strip()
    non_negotiables = answers.get("non_negotiables", "").strip()
    
    user_prompt = f"""
Analizza questa valutazione di compatibilità sentimentale.

PUNTEGGIO FINALE: {evaluation_data.get("final_score")}/100
LIVELLO: {evaluation_data.get("compatibility_level")}
VERDETTO: {evaluation_data.get("verdict")}

INDICI:
- Fiducia: {evaluation_data.get("trust_index")}/10
- Visione: {evaluation_data.get("vision_index")}/10
- Maturità emotiva: {evaluation_data.get("emotional_maturity_index")}/10
- Allineamento ambizione: {evaluation_data.get("ambition_alignment_index")}/10

RISPOSTE APERTE:
"Perché funzioneremmo": {why_us if why_us else "Non fornita"}
"Non negoziabili": {non_negotiables if non_negotiables else "Non forniti"}

PUNTI DI FORZA: {', '.join(evaluation_data.get("strengths", []))}
CRITICITÀ: {', '.join(evaluation_data.get("concerns", []))}
RED FLAGS: {', '.join(evaluation_data.get("red_flags", []))}

Genera un'interpretazione avanzata (max 300 parole) che:
1. Analizza la compatibilità reale oltre i numeri
2. Evidenzia pattern psicologici rilevanti
3. Indica se c'è allineamento profondo o solo superficiale
4. Suggerisce cosa potrebbe funzionare o non funzionare nella relazione
5. Mantiene un tono ironico ma intelligente, diretto, mai compiacente

Scrivi in italiano, stile lucido e adulto.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Errore nella generazione dell'interpretazione: {e}")
        return None

RESOCONTO_SYSTEM_PROMPT = """
Sei un valutatore di compatibilità sentimentale.
Il contesto è un questionario ironico ma serio chiamato "Come diventare la mia futura moglie".

Il tuo compito NON è ricalcolare punteggi.
Il tuo compito è INTERPRETARE il risultato complessivo.

Il soggetto ha:
- forte ambizione
- mentalità costruttiva
- bisogno di autonomia + rispetto
- visione a lungo termine
- intolleranza per superficialità, caos emotivo, interesse strumentale

TONO E STILE:
- Ironico leggero, mai volgare
- Diretto, mai aggressivo
- Intelligente, mai paternalistico
- Sicuro, non arrogante
- Lucido, adulto, selettivo
- Non romantico, non crudele

Scrivi come qualcuno che "non cerca chiunque, ma riconosce chi può stare al passo".

OUTPUT:
- SOLO testo semplice (no JSON, no markdown, no emoji, no elenchi puntati)
- Lunghezza: 120-200 parole
- La valutazione deve sembrare scritta da una persona reale, non da un algoritmo
"""

def generate_final_report(evaluation_data: dict, answers: dict) -> str:
    """
    Genera il resoconto finale testuale secondo le specifiche.
    
    Args:
        evaluation_data: Dati della valutazione (score, indici, etc.)
        answers: Dizionario con tutte le risposte
    
    Returns:
        Testo del resoconto finale
    """
    client = get_client()
    if not client:
        return None
    
    why_us = answers.get("why_us", "").strip()
    non_negotiables = answers.get("non_negotiables", "").strip()
    
    # Prepara il breakdown dei punti in formato leggibile
    breakdown_text = "\n".join([
        f"- {item['question']}: {item['answer']} ({item['points']:+} punti)"
        for item in evaluation_data.get("points_breakdown", [])
    ])
    
    user_prompt = f"""
Scrivi una valutazione testuale finale che interpreti questo risultato complessivo.

PUNTEGGIO FINALE: {evaluation_data.get("final_score")}/100
LIVELLO COMPATIBILITÀ: {evaluation_data.get("compatibility_level")}

INDICI SINTETICI:
- Fiducia: {evaluation_data.get("trust_index")}/10
- Visione: {evaluation_data.get("vision_index")}/10
- Maturità emotiva: {evaluation_data.get("emotional_maturity_index")}/10
- Allineamento ambizione: {evaluation_data.get("ambition_alignment_index")}/10

BREAKDOWN PUNTI:
{breakdown_text}

PUNTI DI FORZA: {', '.join(evaluation_data.get("strengths", []))}
CRITICITÀ: {', '.join(evaluation_data.get("concerns", []))}
RED FLAGS: {', '.join(evaluation_data.get("red_flags", []))}

RISPOSTE APERTE:
"Perché funzioneremmo": {why_us if why_us else "Non fornita"}
"Non negoziabili": {non_negotiables if non_negotiables else "Non forniti"}

---

La valutazione deve includere:

1. LETTURA GENERALE: Una breve sintesi del profilo emerso (mentalità, visione, atteggiamento).

2. TIPO DI COMPATIBILITÀ: Scegli UNA categoria coerente con il risultato:
   - Non compatibile
   - Potenziale, ma fragile
   - Compatibile
   - Wife material

3. COSA FUNZIONA: 2-4 aspetti chiave che sono allineati con il soggetto.

4. COSA RISCHIA DI NON FUNZIONARE: 1-3 punti critici, senza giudizio morale.

5. VERDETTO FINALE: Una frase conclusiva elegante, netta, memorabile.

Scrivi tutto in un unico testo fluido, senza sezioni separate, senza elenchi puntati, senza emoji.
Il testo deve essere naturale, come se fosse scritto da una persona reale che valuta con lucidità.
Lunghezza: 120-200 parole.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.8,
            messages=[
                {"role": "system", "content": RESOCONTO_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=400
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Errore nella generazione del resoconto finale: {e}")
        return None
