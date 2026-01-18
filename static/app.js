const form = document.getElementById("quiz");
const result = document.getElementById("result");
const out = document.getElementById("out");
const questionsContainer = document.getElementById("questions-container");

let questionsData = null;

// Carica le domande all'avvio
async function loadQuestions() {
  try {
    const res = await fetch("/api/questions");
    questionsData = await res.json();
    renderQuestions();
  } catch (error) {
    console.error("Errore nel caricamento delle domande:", error);
    questionsContainer.innerHTML = "<p class='err'>Errore nel caricamento delle domande</p>";
  }
}

function renderQuestions() {
  if (!questionsData) return;
  
  const questions = questionsData.questions || [];
  let html = "";
  
  questions.forEach((q, idx) => {
    const optionsHtml = Object.entries(q.options)
      .map(([value, opt]) => 
        `<option value="${value}">${opt.label}</option>`
      )
      .join("");
    
    html += `
      <section class="card">
        <label>${q.text}</label>
        <select name="${q.id}" required>
          <option value="">Seleziona…</option>
          ${optionsHtml}
        </select>
      </section>
    `;
  });
  
  questionsContainer.innerHTML = html;
}

function formToJSON(formEl) {
  const data = new FormData(formEl);
  const obj = { name: "", answers: {} };

  for (const [k, v] of data.entries()) {
    if (k === "name") {
      obj.name = v;
    } else {
      obj.answers[k] = v;
    }
  }
  return obj;
}

function render(obj) {
  const compatibilityLevels = {
    "non compatibile": "❌ Non compatibile",
    "potenziale": "⚠️ Potenziale",
    "compatibile": "✅ Compatibile",
    "wife material": "💍 Wife Material"
  };
  
  const levelLabel = compatibilityLevels[obj.compatibility_level] || obj.compatibility_level;
  
  const breakdownHtml = obj.points_breakdown
    .map(item => {
      const pointsClass = item.points > 0 ? "positive" : item.points < 0 ? "negative" : "neutral";
      return `
        <li class="breakdown-item">
          <div class="question-text">${item.question}</div>
          <div class="answer-text">Risposta: ${item.answer}</div>
          <div class="points ${pointsClass}">${item.points > 0 ? '+' : ''}${item.points.toFixed(1)}</div>
          <div class="reason">${item.reason}</div>
        </li>
      `;
    })
    .join("");

  const list = (arr) => (arr || []).map(x => `<li>${x}</li>`).join("");

  out.innerHTML = `
    <div class="score-header">
      <div class="final-score">${obj.final_score}/100</div>
      <div class="compatibility-level">${levelLabel}</div>
      <div class="verdict">${obj.verdict}</div>
      ${obj.evaluation_id ? `<div class="eval-id">ID valutazione: #${obj.evaluation_id}</div>` : ''}
    </div>

    ${obj.final_report ? `
    <div class="final-report">
      <h3>📋 Resoconto finale</h3>
      <div class="final-report-text">${obj.final_report}</div>
    </div>
    ` : ''}

    ${obj.interpretation ? `
    <div class="interpretation">
      <h3>🧠 Interpretazione avanzata</h3>
      <div class="interpretation-text">${obj.interpretation}</div>
    </div>
    ` : ''}

    <div class="indices">
      <h3>Indici di compatibilità</h3>
      <div class="indices-grid">
        <div class="index-item">
          <span class="index-label">Fiducia</span>
          <span class="index-value">${obj.trust_index}/10</span>
        </div>
        <div class="index-item">
          <span class="index-label">Visione</span>
          <span class="index-value">${obj.vision_index}/10</span>
        </div>
        <div class="index-item">
          <span class="index-label">Maturità emotiva</span>
          <span class="index-value">${obj.emotional_maturity_index}/10</span>
        </div>
        <div class="index-item">
          <span class="index-label">Allineamento ambizione</span>
          <span class="index-value">${obj.ambition_alignment_index}/10</span>
        </div>
      </div>
    </div>

    <div class="breakdown">
      <h3>Dettaglio punteggi</h3>
      <ul class="breakdown-list">${breakdownHtml}</ul>
    </div>

    <div class="analysis">
      <div class="analysis-section">
        <h3>Punti di forza</h3>
        <ul>${list(obj.strengths)}</ul>
      </div>

      <div class="analysis-section">
        <h3>Criticità</h3>
        <ul>${list(obj.concerns)}</ul>
      </div>

      ${obj.red_flags && obj.red_flags.length > 0 ? `
      <div class="analysis-section red-flags">
        <h3>Red flags</h3>
        <ul>${list(obj.red_flags)}</ul>
      </div>
      ` : ''}
    </div>

    <div class="final-message">
      <p>${obj.final_message}</p>
    </div>
  `;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  result.classList.add("hidden");
  out.innerHTML = "<div class='loading'>Calcolo compatibilità...</div>";

  const payload = formToJSON(form);

  try {
    const res = await fetch("/api/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      out.innerHTML = `<p class="err">Errore: ${data.error || "sconosciuto"}</p>`;
      result.classList.remove("hidden");
      return;
    }

    render(data);
    result.classList.remove("hidden");
  } catch (error) {
    out.innerHTML = `<p class="err">Errore di connessione: ${error.message}</p>`;
    result.classList.remove("hidden");
  }
});

// Carica le domande all'avvio
loadQuestions();
