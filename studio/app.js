/* Synthetic-only client journey. No real identities or customer data. */
(() => {
  "use strict";

  const STAGES = [
    {id:"DISCOVER",name:"Discover",question:"Is there a business problem worth solving?",description:"Establish the value hypothesis, business owner and existing process before proposing AI.",requirements:["A named fictional sponsor and bounded problem", "A proposed success measure or an explicit baseline gap", "A record of non-AI options"]},
    {id:"ASSESS",name:"Assess",question:"Are the data, capabilities and safeguards sufficient for evaluation?",description:"Understand current maturity, constraints, data authority, operational capacity and risk tolerance.",requirements:["Data and integration inventory", "Security, privacy and governance review needs", "Current/target gaps and unacceptable risks"]},
    {id:"PRIORITIZE",name:"Prioritize",question:"Is this opportunity better than credible alternatives?",description:"Select work based on expected value, feasibility, dependencies, cost and risk.",requirements:["Explicit non-AI baseline", "Value and implementation hypotheses", "Prioritization rationale and trade-offs"]},
    {id:"ARCHITECT",name:"Architect",question:"Is the chosen architecture fit for its intended context?",description:"Compare solution options and document the operating, integration, trust and evaluation boundaries.",requirements:["Alternatives and architecture decision records", "Identity and data-flow boundaries", "Evaluation, operations and cost plans"]},
    {id:"VALIDATE",name:"Validate",question:"Does a bounded proof of value satisfy predefined criteria?",description:"Test the solution with reproducible evidence, not a persuasive demonstration alone.",requirements:["Versioned cases and a baseline", "Observed quality, safety, cost and latency", "Recorded failures and independent critical blockers"]},
    {id:"ADOPT",name:"Adopt",question:"Are users and operations ready to adopt responsibly?",description:"Prepare rollout, communication, training, support, monitoring and human ownership.",requirements:["Named operational and decision owners", "Adoption and enablement roadmap", "Monitoring, incident and rollback plans"]},
    {id:"MEASURE_IMPROVE",name:"Improve",question:"Is value sustained, and what must change next?",description:"Compare operational evidence to business outcomes and revise investment decisions.",requirements:["Observed outcomes and usage against baselines", "User feedback and incident trends", "Review and improvement cadence"]}
  ];

  const state = { clients: [], client: null, record: null, stageIndex: 0, reportText: "" };
  const $ = id => document.getElementById(id);
  const escape = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[char]));
  const listLines = text => String(text || "").split("\n").map(s => s.trim()).filter(Boolean);

  let toastTimeout;
  function toast(message, error = false) {
    const element = $("toast");
    element.textContent = message;
    element.className = "toast visible" + (error ? " error" : "");
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => element.classList.remove("visible"), 4000);
  }

  async function api(path, options = {}) {
    const response = await fetch(path, {headers: {"Content-Type":"application/json"}, ...options});
    if (!response.ok) {
      let message = `Request failed (${response.status})`;
      try { const error = await response.json(); message = typeof error.detail === "string" ? error.detail : JSON.stringify(error.detail); } catch (_) { /* leave generic error */ }
      throw new Error(message);
    }
    const contentType = response.headers.get("content-type") || "";
    return contentType.includes("json") ? response.json() : response.text();
  }

  function renderClients() {
    $("portfolio-count").textContent = String(state.clients.length).padStart(2,"0");
    $("client-list").innerHTML = state.clients.map(client => `
      <button class="client-choice ${state.client?.client_id === client.client_id ? "selected" : ""}" data-client="${escape(client.client_id)}" aria-pressed="${state.client?.client_id === client.client_id}">
        <span class="client-avatar">${escape(client.initials)}</span><span><strong>${escape(client.name)}</strong><small>${escape(client.sector)}</small></span>
      </button>`).join("");
    $("client-list").querySelectorAll("[data-client]").forEach(button => button.addEventListener("click", () => selectClient(button.dataset.client)));
  }

  async function selectClient(clientId) {
    try {
      state.client = await api(`/api/clients/${encodeURIComponent(clientId)}`);
      state.stageIndex = 0;
      renderClients();
      $("breadcrumb-client").textContent = state.client.name;
      const first = state.client.use_cases[0];
      if (first) await selectCase(first.case_id);
    } catch (error) { toast(error.message, true); }
  }

  async function selectCase(caseId, keepStage = false) {
    state.record = await api(`/api/cases/${encodeURIComponent(caseId)}`);
    if (!keepStage) {
      const firstOpen = state.record.stage_states.findIndex(row => row.status !== "GO");
      state.stageIndex = firstOpen < 0 ? 6 : firstOpen;
    }
    renderCase();
  }

  function renderCase() {
    const record = state.record;
    if (!record) return;
    $("case-title").textContent = record.title;
    $("case-subtitle").textContent = record.problem;
    $("case-risk").textContent = `${record.risk_tier} RISK · ILLUSTRATIVE`;
    $("case-risk").classList.toggle("medium", record.risk_tier !== "HIGH");
    $("case-sector").textContent = record.sector.toUpperCase();
    $("approved-count").innerHTML = `${record.stage_states.filter(s => s.status === "GO").length} <small>/ 7</small>`;
    $("evidence-count").textContent = String(record.evidence.length).padStart(2,"0");
    const current = record.stage_states.find(row => row.status !== "GO") || record.stage_states.at(-1);
    $("current-status").textContent = current.status.replaceAll("_", " ");
    $("business-owner").textContent = record.business_owner;
    $("success-metric").textContent = record.success_metric;
    $("non-ai-alternative").textContent = record.non_ai_alternative;
    renderStages();
    renderEvidence();
  }

  function renderStages() {
    const record = state.record;
    $("stage-strip").innerHTML = STAGES.map((s, i) => {
      const decision = record.stage_states[i];
      return `<button data-stage="${i}" class="stage-tab ${state.stageIndex === i ? "active" : ""} ${decision.status === "LOCKED" ? "locked" : ""} ${decision.status === "GO" ? "go" : ""}" aria-pressed="${state.stageIndex === i}">
          <span class="stage-num">0${i+1} / 07</span><span class="stage-name">${escape(s.name)}</span><span class="stage-state">${escape(decision.status.replaceAll("_"," "))}</span>
        </button>`;
    }).join("");
    $("stage-strip").querySelectorAll("[data-stage]").forEach(button => button.addEventListener("click", () => {state.stageIndex = Number(button.dataset.stage); renderStages();}));
    const stage = STAGES[state.stageIndex], current = record.stage_states[state.stageIndex];
    $("stage-number").textContent = `STAGE 0${state.stageIndex + 1} / 07`;
    $("stage-status").textContent = current.status.replaceAll("_", " ");
    $("stage-title").textContent = stage.name;
    $("stage-description").textContent = stage.description;
    $("stage-question").textContent = stage.question;
    $("stage-requirements").innerHTML = stage.requirements.map(req => `<li>${escape(req)}</li>`).join("");
    const d = current.decision;
    $("latest-decision").innerHTML = d ? `<strong>${escape(current.status.replaceAll("_"," "))}</strong> · Recorded ${escape(d.status.replaceAll("_"," "))} by ${escape(d.owner)}<br>${escape(d.rationale)}<br>${current.invalidation_reason ? `<strong class="evidence-alert">${escape(current.invalidation_reason)}</strong><br>` : ""}<small>${escape(d.blockers.length ? "Open blockers: " + d.blockers.join("; ") : "No blockers recorded")}</small>` :
      current.status === "LOCKED" ? "This stage is locked until the previous gate is approved." : "No review decision recorded for this stage.";
    $("decision-button").disabled = current.status === "LOCKED";
    $("decision-button").textContent = current.status === "LOCKED" ? "Previous decision required" : "Record a review decision →";
  }

  function renderEvidence() {
    const evidence = state.record?.evidence || [];
    $("evidence-list").innerHTML = evidence.length ? evidence.map(item => `
      <article class="evidence-card"><div class="evidence-card-head"><div class="evidence-tags"><span class="evidence-tag">${escape(item.evidence_class)}</span><span class="evidence-tag ${escape(item.verification_status.toLowerCase())}">${escape(item.verification_status)}</span></div><button class="mini-button" data-review="${escape(item.evidence_id)}">Review</button></div>
        <p>${escape(item.summary)}</p><div class="evidence-source">${escape(item.source)} · ${escape(item.evidence_id)}</div>
      </article>`).join("") : '<div class="empty-state">No evidence has been recorded for this fictional case.</div>';
    $("evidence-list").querySelectorAll("[data-review]").forEach(button => button.addEventListener("click", () => openReview(button.dataset.review)));
  }

  function renderEvaluation(run) {
    const target = $("evaluation-results");
    if (!run || run.run_mode !== "OFFLINE_DETERMINISTIC") {
      target.innerHTML = '<div class="empty-state">No validated offline run was found.</div>';
      return;
    }
    const cards = run.systems.map(system => {
      const s = system.summary;
      const failures = system.cases.filter(c => !c.grade.passed).map(c => `<li><strong>${escape(c.case_id)}</strong> · ${escape(c.grade.reasons.join("; "))}</li>`).join("");
      return `<article class="evaluation-scorecard"><span class="eyebrow muted">${escape(system.provider.replaceAll("_"," "))}</span><div class="evaluation-score">${escape(s.passed)} <small>/ ${escape(s.total)}</small></div><p>${escape(s.failed)} heuristic check(s) failed · ${escape(s.critical_failures.length)} critical failures</p><details><summary>Inspect failures and limitations</summary>${failures ? `<ul>${failures}</ul>` : '<p>No failures in this small synthetic fixture set. This is not independent validation.</p>'}</details></article>`;
    }).join("");
    target.innerHTML = `<div class="evaluation-meta"><span>DATASET ${escape(run.dataset.version)}</span><span>CRITERIA ${escape(run.criteria_status)}</span><span>GATE ${escape(run.release_decision)}</span></div><div class="evaluation-grid">${cards}</div><p class="mini-disclaimer">These results are fixture-specific observations from a deterministic rules program, not model performance, real-world impact, or an enterprise release authorization.</p>`;
  }

  async function runEvaluation() {
    const button = $("eval-run-button");
    button.disabled = true;
    button.textContent = "Evaluating fictional cases…";
    try {
      const result = await api("/api/evaluations/offline", {method:"POST"});
      renderEvaluation(result);
      toast("Offline baseline and safety-rule evaluation completed.");
    } catch(error) { toast(error.message, true); }
    finally { button.disabled = false; button.textContent = "Run offline evaluation ▶"; }
  }

  function openModal(id) { $(id).showModal(); }
  function closeModal(id) { $(id).close(); }
  function openReview(evidenceId) {
    const record = state.record.evidence.find(e => e.evidence_id === evidenceId);
    if (!record) return;
    const form = $("review-form"); form.reset();
    form.elements.evidence_id.value = evidenceId;
    $("review-summary").textContent = `${record.evidence_class}: ${record.summary}`;
    openModal("review-dialog");
  }
  function openDecision() {
    if (state.record.stage_states[state.stageIndex].status === "LOCKED") return;
    const form = $("decision-form"); form.reset();
    $("decision-stage-tag").textContent = `STAGE ${state.stageIndex+1} — ${STAGES[state.stageIndex].name.toUpperCase()}`;
    $("evidence-options").innerHTML = state.record.evidence.length ? state.record.evidence.map(e => `<label><input name="evidence_ids" type="checkbox" value="${escape(e.evidence_id)}"/>${escape(e.evidence_class)} · ${escape(e.verification_status)} · ${escape(e.summary.slice(0,85))}</label>`).join("") : "<p>No evidence has been recorded.</p>";
    const d = state.record.stage_states[state.stageIndex].decision;
    if (d) {
      form.elements.owner.value = d.owner;
      form.elements.rationale.value = d.rationale;
      form.elements.status.value = d.status;
      form.elements.blockers.value = d.blockers.join("\n");
      form.elements.alternatives.value = d.alternatives.join("\n");
      form.querySelectorAll('input[name="evidence_ids"]').forEach(box => box.checked = d.evidence_ids.includes(box.value));
    }
    openModal("decision-dialog");
  }

  async function onEvidenceSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget, data = new FormData(form);
    try {
      await api(`/api/cases/${encodeURIComponent(state.record.case_id)}/evidence`, {method:"POST",body:JSON.stringify({evidence_class:data.get("evidence_class"),source:data.get("source"),summary:data.get("summary")})});
      closeModal("evidence-dialog"); form.reset(); await selectCase(state.record.case_id, true); toast("Synthetic evidence recorded as unverified.");
    } catch (error) { toast(error.message, true); }
  }
  async function onReviewSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget, data = new FormData(form);
    try {
      await api(`/api/evidence/${encodeURIComponent(data.get("evidence_id"))}/review`, {method:"POST",body:JSON.stringify({status:data.get("status"),reviewer:data.get("reviewer"),rationale:data.get("rationale")})});
      closeModal("review-dialog"); await selectCase(state.record.case_id, true); toast("Synthetic evidence review recorded.");
    } catch (error) { toast(error.message, true); }
  }
  async function onDecisionSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget, data = new FormData(form);
    const payload = {
      stage:STAGES[state.stageIndex].id,status:data.get("status"),owner:data.get("owner"),rationale:data.get("rationale"),
      evidence_ids:data.getAll("evidence_ids"),blockers:listLines(data.get("blockers")),alternatives:listLines(data.get("alternatives"))
    };
    try {
      await api(`/api/cases/${encodeURIComponent(state.record.case_id)}/decisions`, {method:"POST",body:JSON.stringify(payload)});
      closeModal("decision-dialog");await selectCase(state.record.case_id,true);toast("Synthetic stage decision appended to history.");
    } catch (error) { toast(error.message, true); }
  }
  async function openReport() {
    if (!state.record) return;
    try {
      state.reportText = await api(`/api/cases/${encodeURIComponent(state.record.case_id)}/executive-report`);
      $("report-content").textContent = state.reportText;
      openModal("report-dialog");
    } catch (error) { toast(error.message, true); }
  }
  function downloadReport() {
    if (!state.reportText || !state.record) return;
    const url = URL.createObjectURL(new Blob([state.reportText], {type:"text/markdown;charset=utf-8"}));
    const a = document.createElement("a");a.href = url;a.download = `synthetic-${state.record.case_id}-executive-brief.md`;a.click();setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  async function start() {
    document.querySelectorAll("[data-close]").forEach(button => button.addEventListener("click", () => closeModal(button.dataset.close)));
    $("evidence-button").addEventListener("click", () => {$("evidence-form").reset();openModal("evidence-dialog");});
    $("decision-button").addEventListener("click", openDecision);
    $("report-button").addEventListener("click", openReport);
    $("download-report").addEventListener("click", downloadReport);
    $("evidence-form").addEventListener("submit", onEvidenceSubmit);
    $("eval-run-button").addEventListener("click", runEvaluation);
    $("review-form").addEventListener("submit", onReviewSubmit);
    $("decision-form").addEventListener("submit", onDecisionSubmit);
    try {
      state.clients = await api("/api/clients");
      if (!state.clients.length) throw new Error("No synthetic clients are available.");
      await selectClient(state.clients[0].client_id);
      try { renderEvaluation(await api("/api/evaluations/latest")); } catch(_) { /* fresh local database */ }
    } catch(error) {toast(`Could not load the Studio: ${error.message}`, true);}
  }
  start();
})();
