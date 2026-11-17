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

  const ASSESSMENT_DIMENSIONS = [
    {id:"BUSINESS_VALUE",name:"Business value",question:"Is the problem worth solving and measurable?"},
    {id:"NON_AI_ALTERNATIVE",name:"Non-AI alternative",question:"Was a simpler approach considered fairly?"},
    {id:"DATA_GOVERNANCE",name:"Data governance",question:"Is the source current, suitable and authorized?"},
    {id:"AI_EVALUATION",name:"AI evaluation",question:"Is useful model behavior supported by measured evidence?",measured:true},
    {id:"SECURITY_PRIVACY",name:"Security and privacy",question:"Are access rights, privacy and misuse risks addressed?"},
    {id:"ECONOMICS",name:"Economics",question:"Are measured costs defensible against the alternative?",measured:true},
    {id:"OPERATIONS",name:"Operations",question:"Can the service be monitored, supported and rolled back?"},
    {id:"HUMAN_ACCOUNTABILITY",name:"Human accountability",question:"Who can review, authorize and escalate decisions?"},
    {id:"INDEPENDENT_REVIEW",name:"Independent review (high risk)",question:"Has independent scrutiny been documented?",highRisk:true}
  ];
  const UNKNOWN_REASON = "Not assessed: sufficient fictional supporting evidence has not been provided.";
  const UNKNOWN_ACTION = "Gather and review attributable evidence before recommending progress.";

  const state = { clients: [], client: null, record: null, stageIndex: 0, reportText: "", reportFileName: "", adoption: null, customAssessments: [] };
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
    if (state.adoption) renderAdoption(state.adoption);
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

  function renderAdoption(packet) {
    const target = $("adoption-results");
    if (!packet || !packet.synthetic || !Array.isArray(packet.recommendations)) {
      target.innerHTML = '<div class="empty-state">No synthetic decision scenarios are available.</div>';
      return;
    }
    target.innerHTML = `<div class="adoption-grid">${packet.recommendations.map(rec => {
      const sameClient = state.client?.client_id === rec.client_id;
      const shortReasons = rec.reasons.length ? rec.reasons.slice(0, 3).map(r => `<li><strong>${escape(r.dimension || r.code)}</strong> · ${escape(r.detail)}</li>`).join("") : "<li>Every fictional risk-profile criterion passed. Real evidence and human authorization remain missing.</li>";
      const allReasons = rec.reasons.length ? rec.reasons.map(r => `<li><strong>${escape(r.code)}</strong> · ${escape(r.detail)}<small>Next: ${escape(r.next_action)}</small></li>`).join("") : "<li>No blockers in this constructed scenario.</li>";
      return `<article class="adoption-card ${sameClient ? "highlight" : ""}">
          <div class="adoption-top"><span class="eyebrow muted">${escape(rec.risk_tier)} RISK · FICTIONAL</span><span class="adoption-state ${escape(rec.recommended_state.toLowerCase().replaceAll("_", "-"))}">${escape(rec.recommended_state.replaceAll("_", " "))}</span></div>
          <h4>${escape(rec.title)}</h4><p>${escape(rec.rationale)}</p>
          <ul class="adoption-reasons">${shortReasons}</ul>
          <details><summary>Evidence gaps and actions (${escape(rec.reasons.length)})</summary><ul class="adoption-reasons detail">${allReasons}</ul></details>
          <div class="adoption-foot">${escape(rec.mandatory_dimensions.length)} risk-profile checks · Approval: NOT RECORDED</div>
        </article>`;
    }).join("")}</div><p class="mini-disclaimer">Illustrative verified flags and measurements are deliberately fabricated for teaching. Even an advisory GO is never an actual authorization, and these scenarios do not react to changes in the editable local client records.</p>`;
  }

  function renderAssessmentChecks() {
    const target = $("assessment-checks");
    const previous = new Map([...target.querySelectorAll(".assessment-dimension")].map(card => [card.dataset.dimension, {
      status:card.querySelector('[data-field="status"]').value,
      kind:card.querySelector('[data-field="kind"]').value,
      verification:card.querySelector('[data-field="verification"]').value,
      source:card.querySelector('[data-field="source"]').value,
      rationale:card.querySelector('[data-field="rationale"]').value,
      action:card.querySelector('[data-field="next_action"]').value
    }]));
    const highRisk = $("assessment-form").elements.risk_tier.value === "HIGH";
    const dimensions = ASSESSMENT_DIMENSIONS.filter(d => !d.highRisk || highRisk);
    target.innerHTML = dimensions.map((d, i) => `<details class="assessment-dimension" data-dimension="${d.id}" ${i===0 ? "open" : ""}>
        <summary><span class="dimension-number">${String(i+1).padStart(2,"0")}</span><span><strong>${escape(d.name)}</strong><small>${escape(d.question)}</small></span><span class="dimension-status">UNKNOWN</span></summary>
        <div class="assessment-check-body">
          <div class="assessment-form-grid">
            <label>Criterion status<select data-field="status"><option value="UNKNOWN">UNKNOWN — not established</option><option value="PASS">PASS — evidence supports it</option><option value="GAP">GAP — remediable</option><option value="FAIL">FAIL — unacceptable</option></select></label>
            <label>Evidence class<select data-field="kind"><option value="DOCUMENTED">DOCUMENTED</option><option value="MEASURED">MEASURED (synthetic only)</option><option value="DECLARED">DECLARED</option><option value="INFERRED">INFERRED</option></select></label>
            <label>Evidence verification<select data-field="verification"><option value="UNVERIFIED">UNVERIFIED (default)</option><option value="SIMULATED_VERIFIED">SIMULATED_VERIFIED — invented</option><option value="REJECTED">REJECTED</option></select></label>
            <label>Synthetic evidence source (optional)<input data-field="source" minlength="3" maxlength="240" placeholder="Invented artifact, test or document" /></label>
          </div>
          <label>Rationale<textarea data-field="rationale" minlength="12" maxlength="1200" rows="2" required></textarea></label>
          <label>Next action<textarea data-field="next_action" minlength="10" maxlength="1200" rows="2" required></textarea></label>
          <p class="mini-disclaimer">A PASS with no suitable simulated-verified source becomes HOLD. AI evaluation and economics need the MEASURED class, even in a fictional case.</p>
        </div>
      </details>`).join("");
    target.querySelectorAll(".assessment-dimension").forEach(card => {
      const dim = ASSESSMENT_DIMENSIONS.find(d => d.id === card.dataset.dimension);
      const saved = previous.get(dim.id);
      const set = (key, value) => {card.querySelector(`[data-field="${key}"]`).value = value;};
      set("status", saved?.status || "UNKNOWN");
      set("kind", saved?.kind || (dim.measured ? "MEASURED" : "DOCUMENTED"));
      set("verification", saved?.verification || "UNVERIFIED");
      set("source", saved?.source || "");
      set("rationale", saved?.rationale || UNKNOWN_REASON);
      set("next_action", saved?.action || UNKNOWN_ACTION);
      card.querySelector(".dimension-status").textContent = saved?.status || "UNKNOWN";
      card.querySelector('[data-field="status"]').addEventListener("change", event => {
        const next = event.target.value;
        card.open = true;
        card.querySelector(".dimension-status").textContent = next;
        const rationale = card.querySelector('[data-field="rationale"]');
        const action = card.querySelector('[data-field="next_action"]');
        if (next !== "UNKNOWN") {
          if (rationale.value === UNKNOWN_REASON) rationale.value = "";
          if (action.value === UNKNOWN_ACTION) action.value = "";
        } else {
          if (!rationale.value.trim()) rationale.value = UNKNOWN_REASON;
          if (!action.value.trim()) action.value = UNKNOWN_ACTION;
        }
      });
    });
  }

  let blockerCounter = 0;
  function addAssessmentBlocker() {
    blockerCounter += 1;
    const wrapper = document.createElement("div");
    wrapper.className = "assessment-blocker";
    wrapper.dataset.blockerId = `blocker-${blockerCounter}`;
    wrapper.innerHTML = `<div class="assessment-blocker-head"><strong>Open blocker ${blockerCounter}</strong><button type="button" class="mini-button" data-remove-blocker>Remove</button></div>
      <div class="assessment-form-grid">
        <label>Severity<select data-field="severity"><option value="AUTHORIZATION">AUTHORIZATION → HOLD</option><option value="REMEDIABLE">REMEDIABLE → REWORK</option><option value="TERMINAL">TERMINAL → NO_GO</option></select></label>
        <label>Fictional blocker description<textarea data-field="summary" minlength="12" maxlength="1200" required rows="2"></textarea></label>
      </div>
      <label>Required next action<textarea data-field="next_action" minlength="10" maxlength="1200" required rows="2"></textarea></label>`;
    wrapper.querySelector("[data-remove-blocker]").addEventListener("click", () => wrapper.remove());
    $("assessment-blockers").append(wrapper);
  }

  function openAssessmentWorkshop() {
    const form = $("assessment-form");
    form.reset();
    blockerCounter = 0;
    $("assessment-blockers").replaceChildren();
    if (state.record) {
      form.elements.title.value = `Fictional assessment — ${state.record.title}`.slice(0,120);
      form.elements.client_id.value = state.record.client_id;
      form.elements.case_id.value = state.record.case_id;
      form.elements.accountable_owner.value = state.record.business_owner;
      form.elements.non_ai_alternative.value = state.record.non_ai_alternative;
      form.elements.risk_tier.value = state.record.risk_tier;
    }
    $("assessment-checks").replaceChildren();
    renderAssessmentChecks();
    openModal("assessment-dialog");
  }

  function renderAssessmentHistory() {
    const records = state.customAssessments;
    const target = $("assessment-history");
    target.innerHTML = records.length ? `<div class="assessment-history-grid">${records.map(a => `<article class="saved-assessment">
        <div class="adoption-top"><span class="eyebrow muted">${escape(a.risk_tier)} · FICTIONAL</span><span class="adoption-state ${escape(a.recommended_state.toLowerCase().replaceAll("_", "-"))}">${escape(a.recommended_state)}</span></div>
        <h4>${escape(a.title)}</h4><p>${escape(a.client_id)} · ${escape(a.case_id)}</p>
        <div class="saved-assessment-foot"><small>${escape(a.created_at.replace("T", " "))} UTC</small><button type="button" class="button small outline" data-assessment-report="${escape(a.assessment_id)}">View executive brief ↗</button></div>
      </article>`).join("")}</div>` : '<div class="empty-state">No custom fictional assessments have been saved. Create one to see evidence-linked recommendations here.</div>';
    target.querySelectorAll("[data-assessment-report]").forEach(button => button.addEventListener("click", () => showAssessmentReport(button.dataset.assessmentReport)));
  }

  async function loadAssessmentHistory() {
    state.customAssessments = await api("/api/adoption/assessments");
    renderAssessmentHistory();
  }

  async function showAssessmentReport(assessmentId) {
    try {
      state.reportText = await api(`/api/adoption/assessments/${encodeURIComponent(assessmentId)}/report`);
      state.reportFileName = `synthetic-${assessmentId}-adoption-brief.md`;
      $("report-kind-label").textContent = "FROZEN / SYNTHETIC ADOPTION BRIEF";
      $("report-title").textContent = "Adoption decision brief";
      $("report-content").textContent = state.reportText;
      openModal("report-dialog");
    } catch(error) { toast(error.message, true); }
  }

  async function onAssessmentSubmit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const button = $("assessment-submit");
    const evidence = [];
    const checks = [...$("assessment-checks").querySelectorAll(".assessment-dimension")].map(card => {
      const read = key => card.querySelector(`[data-field="${key}"]`).value.trim();
      const ids = [];
      if (read("source")) {
        const id = `ev-${card.dataset.dimension.toLowerCase().replaceAll("_", "-")}`;
        ids.push(id);
        evidence.push({id,kind:read("kind"),verification:read("verification"),synthetic:true,source:read("source")});
      }
      return {dimension:card.dataset.dimension,status:read("status"),evidence_ids:ids,
        rationale:read("rationale"),next_action:read("next_action")};
    });
    const blockers = [...$("assessment-blockers").querySelectorAll(".assessment-blocker")].map(card => {
      const read = key => card.querySelector(`[data-field="${key}"]`).value.trim();
      return {id:card.dataset.blockerId,severity:read("severity"),status:"OPEN",
        summary:read("summary"),next_action:read("next_action")};
    });
    const payload = {
      synthetic:true,confirmed_fictional:form.elements.confirmed_fictional.checked,
      title:form.elements.title.value.trim(),client_id:form.elements.client_id.value.trim(),
      case_id:form.elements.case_id.value.trim(),risk_tier:form.elements.risk_tier.value,
      accountable_owner:form.elements.accountable_owner.value.trim(),
      non_ai_alternative:form.elements.non_ai_alternative.value.trim(),evidence,checks,blockers
    };
    button.disabled = true;
    try {
      const stored = await api("/api/adoption/assessments", {method:"POST",body:JSON.stringify(payload)});
      closeModal("assessment-dialog");
      await loadAssessmentHistory();
      toast(`Synthetic ${stored.recommendation.recommended_state} advisory saved. No approval recorded.`);
      await showAssessmentReport(stored.assessment_id);
    } catch(error) {toast(error.message,true);}
    finally {button.disabled=false;}
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
      state.reportFileName = `synthetic-${state.record.case_id}-executive-brief.md`;
      $("report-kind-label").textContent = "DETERMINISTIC SYNTHETIC REPORT";
      $("report-title").textContent = "Executive opportunity brief";
      $("report-content").textContent = state.reportText;
      openModal("report-dialog");
    } catch (error) { toast(error.message, true); }
  }
  function downloadReport() {
    if (!state.reportText || !state.reportFileName) return;
    const url = URL.createObjectURL(new Blob([state.reportText], {type:"text/markdown;charset=utf-8"}));
    const a = document.createElement("a");a.href = url;a.download = state.reportFileName;a.click();setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  async function start() {
    document.querySelectorAll("[data-close]").forEach(button => button.addEventListener("click", () => closeModal(button.dataset.close)));
    $("evidence-button").addEventListener("click", () => {$("evidence-form").reset();openModal("evidence-dialog");});
    $("decision-button").addEventListener("click", openDecision);
    $("report-button").addEventListener("click", openReport);
    $("download-report").addEventListener("click", downloadReport);
    $("evidence-form").addEventListener("submit", onEvidenceSubmit);
    $("eval-run-button").addEventListener("click", runEvaluation);
    $("assessment-create-button").addEventListener("click", openAssessmentWorkshop);
    $("assessment-form").elements.risk_tier.addEventListener("change", renderAssessmentChecks);
    $("assessment-add-blocker").addEventListener("click", addAssessmentBlocker);
    // Native validation must be able to focus a required field inside a closed <details>.
    $("assessment-form").addEventListener("invalid", event => {
      const hiddenDimension = event.target.closest(".assessment-dimension");
      if (hiddenDimension) hiddenDimension.open = true;
    }, true);
    $("assessment-form").addEventListener("submit", onAssessmentSubmit);
    $("review-form").addEventListener("submit", onReviewSubmit);
    $("decision-form").addEventListener("submit", onDecisionSubmit);
    try {
      state.clients = await api("/api/clients");
      if (!state.clients.length) throw new Error("No synthetic clients are available.");
      await selectClient(state.clients[0].client_id);
      try { state.adoption = await api("/api/adoption/scenarios"); renderAdoption(state.adoption); }
      catch(error) { $("adoption-results").textContent = `Could not load simulated recommendations: ${error.message}`; }
      try {await loadAssessmentHistory();}
      catch(error) {$("assessment-history").textContent = `Could not load saved assessments: ${error.message}`;}
      try { renderEvaluation(await api("/api/evaluations/latest")); } catch(_) { /* fresh local database */ }
    } catch(error) {toast(`Could not load the Studio: ${error.message}`, true);}
  }
  start();
})();
