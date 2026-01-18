let questionsData = null;
let currentPage = 0;
let answers = {};
let totalPages = 0;

// Struttura pagine: [nome, ...domande, domande_aperte]
const pageStructure = ['name'];

// Carica le domande all'avvio
async function loadQuestions() {
  try {
    const res = await fetch("/api/questions");
    questionsData = await res.json();
    setupPages();
  } catch (error) {
    console.error("Errore nel caricamento delle domande:", error);
    document.getElementById("questions-pages").innerHTML = "<p class='err'>Errore nel caricamento delle domande</p>";
  }
}

function setupPages() {
  if (!questionsData) return;
  
  const questions = questionsData.questions || [];
  const openQuestions = questionsData.open_questions || [];
  
  // Aggiungi le domande alla struttura (escludendo la pagina nome che è già presente)
  questions.forEach(q => {
    if (!pageStructure.includes(q.id)) {
      pageStructure.push(q.id);
    }
  });
  
  // Le domande aperte sono gestite come una singola pagina
  // Non le aggiungiamo alla struttura perché hanno una pagina dedicata
  
  totalPages = pageStructure.length + 1; // +1 per la pagina domande aperte
  console.log("Total pages:", totalPages, "Questions:", questions.length, "PageStructure:", pageStructure.length);
  
  // Crea le pagine delle domande
  const questionsPagesContainer = document.getElementById("questions-pages");
  let html = "";
  
  questions.forEach((q, idx) => {
    const optionsHtml = Object.entries(q.options)
      .map(([value, opt]) => 
        `<option value="${value}">${opt.label}</option>`
      )
    .join("");

    const pageNum = idx + 1; // +1 perché c'è la pagina nome
    
    html += `
      <div id="page-${q.id}" class="quiz-page">
        <div class="card">
          <div class="progress-bar">
            <div class="progress-fill"></div>
          </div>
          <div class="question-number">Domanda ${pageNum} di ${questions.length}</div>
          <h2>${q.text}</h2>
          <select id="select-${q.id}" required>
            <option value="">Seleziona…</option>
            ${optionsHtml}
          </select>
          <div class="page-actions">
            <button type="button" class="btn-prev" onclick="prevPage()">← Indietro</button>
            <button type="button" class="btn-next" onclick="nextPage()">Avanti →</button>
          </div>
        </div>
      </div>
    `;
  });
  
  questionsPagesContainer.innerHTML = html;
  
  // Aggiorna progress bar pagina domande aperte
  const progressOpen = document.getElementById("progress-open");
  if (progressOpen) {
    progressOpen.style.width = "100%";
  }
  
  // Mostra la prima pagina
  showPage(0);
  updateProgressBar();
}

function showPage(pageIndex) {
  // Nascondi tutte le pagine
  document.querySelectorAll(".quiz-page").forEach(page => {
    page.classList.remove("active");
  });
  
  let pageElement;
  
  if (pageIndex === 0) {
    // Pagina nome
    pageElement = document.getElementById("page-name");
  } else if (pageIndex === totalPages - 1) {
    // Pagina domande aperte (ultima pagina prima del risultato)
    pageElement = document.getElementById("page-open-questions");
    if (!pageElement) {
      console.error("Pagina domande aperte non trovata! totalPages:", totalPages, "pageIndex:", pageIndex);
    }
  } else {
    // Pagina domanda (pageIndex - 1 perché la prima è il nome)
    const question = questionsData.questions[pageIndex - 1];
    if (question) {
      pageElement = document.getElementById(`page-${question.id}`);
    } else {
      console.error("Domanda non trovata per pageIndex:", pageIndex);
    }
  }
  
  if (pageElement) {
    pageElement.classList.add("active");
    currentPage = pageIndex;
    
    // Aggiorna progress bar
    updateProgressBar();
  } else {
    console.error("Nessuna pagina trovata per index:", pageIndex);
  }
}

function updateProgressBar() {
  const progress = ((currentPage + 1) / totalPages) * 100;
  document.querySelectorAll(".progress-fill").forEach(bar => {
    if (!bar.id || bar.id !== "progress-open") {
      bar.style.width = `${progress}%`;
    }
  });
}

function nextPage() {
  // Salva la risposta corrente
  saveCurrentAnswer();
  
  // Valida la pagina corrente
  if (!validateCurrentPage()) {
    return;
  }
  
  console.log("Next page - current:", currentPage, "totalPages:", totalPages, "next:", currentPage + 1);
  
  if (currentPage < totalPages - 1) {
    showPage(currentPage + 1);
  } else {
    console.log("Già all'ultima pagina!");
  }
}

function prevPage() {
  if (currentPage > 0) {
    showPage(currentPage - 1);
  }
}

function saveCurrentAnswer() {
  if (currentPage === 0) {
    // Salva il nome
    const nameInput = document.getElementById("input-name");
    if (nameInput) {
      answers.name = nameInput.value;
    }
  } else if (currentPage === totalPages - 1) {
    // Salva le domande aperte (ultima pagina prima del risultato)
    const whyUs = document.getElementById("textarea-why-us");
    const nonNegotiables = document.getElementById("textarea-non-negotiables");
    if (whyUs) answers.why_us = whyUs.value;
    if (nonNegotiables) answers.non_negotiables = nonNegotiables.value;
  } else {
    // Salva la risposta alla domanda
    const question = questionsData.questions[currentPage - 1];
    if (question) {
      const select = document.getElementById(`select-${question.id}`);
      if (select && select.value) {
        answers[question.id] = select.value;
      }
    }
  }
}

function validateCurrentPage() {
  if (currentPage === 0) {
    const nameInput = document.getElementById("input-name");
    if (!nameInput || !nameInput.value.trim()) {
      alert("Inserisci il tuo nome per continuare");
      return false;
    }
    return true;
  }
  
  if (currentPage === totalPages - 1) {
    // Pagina domande aperte (ultima pagina prima del risultato)
    const whyUs = document.getElementById("textarea-why-us");
    if (!whyUs || !whyUs.value.trim()) {
      alert("Rispondi alla domanda 'Perché funzioneremmo' per continuare");
      return false;
    }
    return true;
  }
  
  // Valida domanda
  const question = questionsData.questions[currentPage - 1];
  if (!question) {
    return false;
  }
  const select = document.getElementById(`select-${question.id}`);
  if (!select || !select.value) {
    alert("Seleziona una risposta per continuare");
    return false;
  }
  return true;
}

async function submitQuiz() {
  // Salva le risposte finali
  saveCurrentAnswer();
  
  // Valida
  if (!validateCurrentPage()) {
    return;
  }
  
  // Mostra pagina risultato
  showPageResult();
  
  // Prepara payload
  const payload = {
    name: answers.name || "",
    answers: {}
  };
  
  // Aggiungi tutte le risposte alle domande
  questionsData.questions.forEach(q => {
    if (answers[q.id]) {
      payload.answers[q.id] = answers[q.id];
    }
  });
  
  // Aggiungi domande aperte
  if (answers.why_us) payload.answers.why_us = answers.why_us;
  if (answers.non_negotiables) payload.answers.non_negotiables = answers.non_negotiables;
  
  // Mostra loading
  document.getElementById("result-content").innerHTML = "<div class='loading'>Calcolo compatibilità...</div>";
  
  try {
  const res = await fetch("/api/score", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await res.json();

  if (!res.ok) {
      document.getElementById("result-content").innerHTML = `<p class="err">Errore: ${data.error || "sconosciuto"}</p>`;
    return;
  }

    renderResult(data);
  } catch (error) {
    document.getElementById("result-content").innerHTML = `<p class="err">Errore di connessione: ${error.message}</p>`;
  }
}

function showPageResult() {
  document.querySelectorAll(".quiz-page").forEach(page => {
    page.classList.remove("active");
  });
  document.getElementById("page-result").classList.add("active");
}

function renderResult(obj) {
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

  document.getElementById("result-content").innerHTML = `
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

function restartQuiz() {
  // Reset tutto
  currentPage = 0;
  answers = {};
  
  // Reset form
  document.getElementById("input-name").value = "";
  questionsData.questions.forEach(q => {
    const select = document.getElementById(`select-${q.id}`);
    if (select) select.value = "";
  });
  document.getElementById("textarea-why-us").value = "";
  document.getElementById("textarea-non-negotiables").value = "";
  
  // Torna alla prima pagina
  showPage(0);
}

// Carica le domande all'avvio
loadQuestions();
