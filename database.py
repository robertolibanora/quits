"""
Gestione database SQLite per salvare le valutazioni di compatibilità.
"""
import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

DB_PATH = "futurewife.db"

@contextmanager
def get_db():
    """Context manager per gestire le connessioni al database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Inizializza il database creando le tabelle se non esistono."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                final_score INTEGER,
                compatibility_level TEXT,
                verdict TEXT,
                trust_index REAL,
                vision_index REAL,
                emotional_maturity_index REAL,
                ambition_alignment_index REAL,
                answers_json TEXT,
                points_breakdown_json TEXT,
                strengths_json TEXT,
                concerns_json TEXT,
                red_flags_json TEXT,
                interpretation TEXT,
                final_message TEXT,
                final_report TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_evaluation(evaluation_data: dict, interpretation: str = None, final_report: str = None):
    """
    Salva una valutazione nel database.
    
    Args:
        evaluation_data: Dizionario con i dati della valutazione
        interpretation: Testo dell'interpretazione avanzata (opzionale)
        final_report: Testo del resoconto finale (opzionale)
    
    Returns:
        ID della valutazione salvata
    """
    with get_db() as conn:
        # Controlla se la colonna final_report esiste, altrimenti la aggiunge
        try:
            conn.execute("ALTER TABLE evaluations ADD COLUMN final_report TEXT")
        except sqlite3.OperationalError:
            pass  # Colonna già esistente
        
        cursor = conn.execute("""
            INSERT INTO evaluations (
                name, final_score, compatibility_level, verdict,
                trust_index, vision_index, emotional_maturity_index, ambition_alignment_index,
                answers_json, points_breakdown_json, strengths_json, concerns_json, red_flags_json,
                interpretation, final_message, final_report
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            evaluation_data.get("name", ""),
            evaluation_data.get("final_score", 0),
            evaluation_data.get("compatibility_level", ""),
            evaluation_data.get("verdict", ""),
            evaluation_data.get("trust_index", 0),
            evaluation_data.get("vision_index", 0),
            evaluation_data.get("emotional_maturity_index", 0),
            evaluation_data.get("ambition_alignment_index", 0),
            json.dumps(evaluation_data.get("answers", {}), ensure_ascii=False),
            json.dumps(evaluation_data.get("points_breakdown", []), ensure_ascii=False),
            json.dumps(evaluation_data.get("strengths", []), ensure_ascii=False),
            json.dumps(evaluation_data.get("concerns", []), ensure_ascii=False),
            json.dumps(evaluation_data.get("red_flags", []), ensure_ascii=False),
            interpretation,
            evaluation_data.get("final_message", ""),
            final_report
        ))
        return cursor.lastrowid

def get_evaluation(eval_id: int):
    """Recupera una valutazione dal database per ID."""
    with get_db() as conn:
        row = conn.execute("""
            SELECT * FROM evaluations WHERE id = ?
        """, (eval_id,)).fetchone()
        
        if not row:
            return None
        
        return {
            "id": row["id"],
            "name": row["name"],
            "final_score": row["final_score"],
            "compatibility_level": row["compatibility_level"],
            "verdict": row["verdict"],
            "trust_index": row["trust_index"],
            "vision_index": row["vision_index"],
            "emotional_maturity_index": row["emotional_maturity_index"],
            "ambition_alignment_index": row["ambition_alignment_index"],
            "answers": json.loads(row["answers_json"]),
            "points_breakdown": json.loads(row["points_breakdown_json"]),
            "strengths": json.loads(row["strengths_json"]),
            "concerns": json.loads(row["concerns_json"]),
            "red_flags": json.loads(row["red_flags_json"]),
            "interpretation": row["interpretation"],
            "final_message": row["final_message"],
            "final_report": row.get("final_report"),  # Usa get per compatibilità con DB vecchi
            "created_at": row["created_at"]
        }

def get_all_evaluations(limit: int = 50):
    """Recupera tutte le valutazioni (più recenti prima)."""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT id, name, final_score, compatibility_level, verdict, created_at
            FROM evaluations
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        
        return [dict(row) for row in rows]

def get_statistics():
    """Recupera statistiche aggregate sulle valutazioni."""
    with get_db() as conn:
        stats = conn.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(final_score) as avg_score,
                COUNT(CASE WHEN compatibility_level = 'wife material' THEN 1 END) as wife_material_count,
                COUNT(CASE WHEN compatibility_level = 'compatibile' THEN 1 END) as compatible_count,
                COUNT(CASE WHEN compatibility_level = 'potenziale' THEN 1 END) as potential_count,
                COUNT(CASE WHEN compatibility_level = 'non compatibile' THEN 1 END) as incompatible_count
            FROM evaluations
        """).fetchone()
        
        return dict(stats)
