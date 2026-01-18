import os
import json
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from .questions import QUESTIONS, OPEN_QUESTIONS
from .database import init_db, save_evaluation, get_evaluation, get_all_evaluations, get_statistics
from .interpretation import generate_interpretation, generate_final_report

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "liba2004-secret-key-change-in-production")

# Password admin
ADMIN_PASSWORD = "liba2004"

# Inizializza il database all'avvio
init_db()

def admin_required(f):
    """Decorator per proteggere le route admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

def calculate_score(answers: dict) -> dict:
    """
    Calcola il punteggio totale e la valutazione completa secondo le regole specificate.
    """
    points_breakdown = []
    total_points = 0
    max_possible_points = 0
    
    # Mappatura per calcolare gli indici
    trust_questions = ["trust_future"]  # La più importante, interpretativa
    vision_questions = ["mare_montagna", "where_live", "vacation_type"]  # Stile di vita e visione
    emotional_maturity_questions = ["attractive_woman", "wife_job", "how_die"]  # Maturità e valori
    ambition_questions = ["rich_priority", "representative_phrase", "money_relationship"]  # Ambizione e costruzione
    
    trust_points = 0
    vision_points = 0
    emotional_maturity_points = 0
    ambition_points = 0
    
    trust_max = 0
    vision_max = 0
    emotional_maturity_max = 0
    ambition_max = 0
    
    # Valuta ogni domanda
    for question in QUESTIONS:
        q_id = question["id"]
        answer_value = answers.get(q_id)
        
        if not answer_value:
            continue
        
        multiplier = question.get("importance_multiplier", 1.0)
        question_points = 0
        reason = ""
        
        if question["type"] == "correct_answer":
            correct = question["correct_answer"]
            if answer_value == correct:
                question_points = 8
                reason = "Risposta corretta"
            else:
                # Controlla se indica incompatibilità forte
                option = question["options"].get(answer_value, {})
                base_points = option.get("points", 0)
                if base_points < 0:
                    question_points = -4
                    reason = "Incompatibilità forte rilevata"
                else:
                    question_points = 0
                    reason = "Risposta non corretta"
        
        elif question["type"] == "interpretive":
            option = question["options"].get(answer_value, {})
            question_points = option.get("points", 0)
            if question_points > 0:
                reason = "Valutazione psicologica positiva"
            elif question_points < 0:
                reason = "Valutazione psicologica negativa"
            else:
                reason = "Valutazione neutra"
        
        # Applica moltiplicatore
        final_points = question_points * multiplier
        total_points += final_points
        
        # Calcola max possibile per questa domanda
        max_for_question = max([opt.get("points", 0) * multiplier for opt in question["options"].values()])
        max_possible_points += max_for_question
        
        # Aggiorna indici
        if q_id in trust_questions:
            trust_points += final_points
            trust_max += max_for_question
        if q_id in vision_questions:
            vision_points += final_points
            vision_max += max_for_question
        if q_id in emotional_maturity_questions:
            emotional_maturity_points += final_points
            emotional_maturity_max += max_for_question
        if q_id in ambition_questions:
            ambition_points += final_points
            ambition_max += max_for_question
        
        # Trova il label della risposta
        answer_label = question["options"].get(answer_value, {}).get("label", answer_value)
        
        points_breakdown.append({
            "question": question["text"],
            "answer": answer_label,
            "points": round(final_points, 1),
            "reason": reason
        })
    
    # Calcola final_score (0-100)
    if max_possible_points > 0:
        final_score = max(0, min(100, int((total_points / max_possible_points) * 100)))
    else:
        final_score = 0
    
    # Calcola indici (0-10)
    trust_index = round((trust_points / trust_max * 10) if trust_max > 0 else 0, 1)
    vision_index = round((vision_points / vision_max * 10) if vision_max > 0 else 0, 1)
    emotional_maturity_index = round((emotional_maturity_points / emotional_maturity_max * 10) if emotional_maturity_max > 0 else 0, 1)
    ambition_alignment_index = round((ambition_points / ambition_max * 10) if ambition_max > 0 else 0, 1)
    
    # Determina compatibility_level
    if final_score >= 80:
        compatibility_level = "wife material"
    elif final_score >= 60:
        compatibility_level = "compatibile"
    elif final_score >= 40:
        compatibility_level = "potenziale"
    else:
        compatibility_level = "non compatibile"
    
    # Genera verdict (ironico ma intelligente)
    if final_score >= 85:
        verdict = "Wife material. Allineamento solido, costruire insieme è possibile."
    elif final_score >= 70:
        verdict = "Compatibile sul piano mentale, ma non ancora pronta per reggere il ritmo."
    elif final_score >= 55:
        verdict = "Potenziale presente, ma serve chiarimento su alcuni punti critici."
    elif final_score >= 40:
        verdict = "Compatibilità limitata. Differenze significative su valori chiave."
    else:
        verdict = "Incompatibilità strutturale. Visioni troppo distanti per costruire insieme."
    
    # Analizza risposte aperte per red flags e strengths
    strengths = []
    concerns = []
    red_flags = []
    
    # Analisi basata sui punteggi
    if trust_index >= 8:
        strengths.append("Fiducia solida nel futuro e nelle capacità")
    elif trust_index < 5:
        concerns.append("Fiducia limitata o assente")
        if trust_index < 3:
            red_flags.append("Mancanza di fiducia nel futuro")
    
    if vision_index >= 8:
        strengths.append("Visione chiara e a lungo termine")
    elif vision_index < 5:
        concerns.append("Visione a lungo termine poco chiara")
    
    if emotional_maturity_index >= 8:
        strengths.append("Maturità emotiva e gestione costruttiva dei conflitti")
    elif emotional_maturity_index < 5:
        concerns.append("Maturità emotiva da sviluppare")
        if emotional_maturity_index < 3:
            red_flags.append("Gestione emotiva problematica")
    
    if ambition_alignment_index >= 8:
        strengths.append("Allineamento su ambizione e progetti futuri")
    elif ambition_alignment_index < 5:
        concerns.append("Differenze significative su ambizione e progetti")
        if ambition_alignment_index < 3:
            red_flags.append("Incompatibilità su ambizione e visione futura")
    
    # Analisi specifiche dalle risposte
    if answers.get("trust_future") == "1_2_anni":
        strengths.append("Fiducia totale nel futuro: valore fondamentale")
    elif answers.get("trust_future") == "ci_sono_nato":
        red_flags.append("Possibile interesse strumentale: risposta 'ci sono nato/a'")
    
    if answers.get("attractive_woman") == "intelligente_carattere":
        strengths.append("Valorizza intelligenza e carattere: allineamento sui valori")
    
    if answers.get("wife_job") == "direttrice":
        strengths.append("Visione ambiziosa per la coppia: direttrice")
    
    if answers.get("money_relationship") == "investo":
        strengths.append("Approccio costruttivo al denaro: investe")
    elif answers.get("money_relationship") == "mignotte_cocaina":
        red_flags.append("Rapporto problematico con il denaro")
    
    if answers.get("rich_priority") == "aumentare_livello":
        strengths.append("Priorità su crescita e livello, non su apparenza")
    
    if answers.get("representative_phrase") == "costruisco_fatica":
        strengths.append("Mentalità costruttiva: 'costruisco anche se costa fatica'")
    
    # Analizza risposte aperte (se presenti)
    why_us = answers.get("why_us", "").strip()
    non_negotiables = answers.get("non_negotiables", "").strip()
    
    if why_us:
        if len(why_us) < 20:
            concerns.append("Risposta 'Perché funzioneremmo' troppo breve o superficiale")
        elif "soldi" in why_us.lower() or "ricco" in why_us.lower() or "denaro" in why_us.lower():
            red_flags.append("Possibile interesse strumentale rilevato nelle risposte aperte")
        elif "futuro" in why_us.lower() or "crescita" in why_us.lower() or "costruire" in why_us.lower():
            strengths.append("Visione costruttiva espressa nelle risposte")
    
    if non_negotiables:
        if "gelosia" in non_negotiables.lower() or "controllo" in non_negotiables.lower():
            concerns.append("Possibili dinamiche di controllo")
    
    # Genera final_message (elegante e tagliente)
    if final_score >= 85:
        final_message = "Allineamento solido. La costruzione insieme è possibile."
    elif final_score >= 70:
        final_message = "Buona base mentale. Serve maturità e rispetto reciproco per reggere il ritmo."
    elif final_score >= 55:
        final_message = "Potenziale presente, ma le differenze richiedono chiarimento e crescita."
    elif final_score >= 40:
        final_message = "Compatibilità limitata. Le visioni divergono su punti fondamentali."
    else:
        final_message = "Incompatibilità strutturale. Visioni troppo distanti per costruire insieme."
    
    return {
        "final_score": final_score,
        "verdict": verdict,
        "compatibility_level": compatibility_level,
        "points_breakdown": points_breakdown,
        "strengths": strengths if strengths else ["Nessun punto di forza significativo rilevato"],
        "concerns": concerns if concerns else ["Nessuna criticità significativa rilevata"],
        "red_flags": red_flags if red_flags else [],
        "trust_index": trust_index,
        "vision_index": vision_index,
        "emotional_maturity_index": emotional_maturity_index,
        "ambition_alignment_index": ambition_alignment_index,
        "final_message": final_message
    }

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/questions")
def get_questions():
    """Endpoint per ottenere le domande strutturate"""
    return jsonify({
        "questions": QUESTIONS,
        "open_questions": OPEN_QUESTIONS
    })

@app.post("/api/score")
def score():
    data = request.get_json(force=True)
    
    # Validazione
    if not data or "answers" not in data:
        return jsonify({"error": "Payload non valido"}), 400
    
    try:
        # Calcola il punteggio
        result = calculate_score(data["answers"])
        
        # Genera interpretazione avanzata
        interpretation = generate_interpretation(result, data["answers"])
        
        # Genera resoconto finale
        final_report = generate_final_report(result, data["answers"])
        
        # Prepara i dati per il salvataggio
        evaluation_data = {
            "name": data.get("name", ""),
            "answers": data["answers"],
            **result
        }
        
        # Salva nel database
        eval_id = save_evaluation(evaluation_data, interpretation, final_report)
        
        # Aggiungi interpretazione, resoconto finale e ID al risultato
        result["interpretation"] = interpretation
        result["final_report"] = final_report
        result["evaluation_id"] = eval_id
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "Errore durante la valutazione", "details": str(e)}), 500

@app.get("/api/evaluations")
def get_evaluations():
    """Endpoint per recuperare tutte le valutazioni salvate."""
    try:
        evaluations = get_all_evaluations()
        return jsonify({"evaluations": evaluations})
    except Exception as e:
        return jsonify({"error": "Errore nel recupero delle valutazioni", "details": str(e)}), 500

@app.get("/api/evaluations/<int:eval_id>")
def get_evaluation_detail(eval_id):
    """Endpoint per recuperare una valutazione specifica."""
    try:
        evaluation = get_evaluation(eval_id)
        if not evaluation:
            return jsonify({"error": "Valutazione non trovata"}), 404
        return jsonify(evaluation)
    except Exception as e:
        return jsonify({"error": "Errore nel recupero della valutazione", "details": str(e)}), 500

@app.get("/api/statistics")
def statistics():
    """Endpoint per recuperare statistiche aggregate."""
    try:
        stats = get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": "Errore nel recupero delle statistiche", "details": str(e)}), 500

# ========== ADMIN ROUTES ==========

@app.get("/admin")
def admin_login():
    """Pagina di login admin."""
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html")

@app.post("/admin/login")
def admin_login_post():
    """Processa il login admin."""
    password = request.form.get("password", "")
    if password == ADMIN_PASSWORD:
        session["admin_logged_in"] = True
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html", error="Password errata")

@app.get("/admin/logout")
def admin_logout():
    """Logout admin."""
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

@app.get("/admin/dashboard")
@admin_required
def admin_dashboard():
    """Dashboard admin con tutte le valutazioni."""
    try:
        evaluations = get_all_evaluations(limit=1000)
        stats = get_statistics()
        return render_template("admin_dashboard.html", evaluations=evaluations, stats=stats)
    except Exception as e:
        return render_template("admin_dashboard.html", error=str(e), evaluations=[], stats={})

@app.get("/admin/evaluation/<int:eval_id>")
@admin_required
def admin_evaluation_detail(eval_id):
    """Dettaglio di una singola valutazione."""
    try:
        evaluation = get_evaluation(eval_id)
        if not evaluation:
            return render_template("admin_error.html", message="Valutazione non trovata"), 404
        return render_template("admin_evaluation_detail.html", evaluation=evaluation)
    except Exception as e:
        return render_template("admin_error.html", message=f"Errore: {str(e)}"), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
