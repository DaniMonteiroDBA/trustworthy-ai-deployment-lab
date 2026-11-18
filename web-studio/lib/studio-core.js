/*
 * Hosted synthetic-only API engine. The Python implementation remains the reference.
 * This engine is intentionally pure per request: the caller loads an authenticated
 * user's latest D1 snapshot and appends the next immutable version after a write.
 * A self-entered reviewer name never constitutes an authenticated human approval.
 */
export function createStudioCore(snapshot, fixtures) {
  "use strict";
  const STAGES = ["DISCOVER", "ASSESS", "PRIORITIZE", "ARCHITECT",
                  "VALIDATE", "ADOPT", "MEASURE_IMPROVE"];
  const now = () => new Date().toISOString();
  const id = prefix => prefix + "-" + crypto.randomUUID();
  const copy = value => JSON.parse(JSON.stringify(value));
  const seed = () => ({
    clients: [
      {client_id:"civicdata-demo",name:"CivicData",sector:"Public sector",description:"A fictional public-sector organization considering trustworthy policy-based services.",initials:"CD",synthetic:1},
      {client_id:"fintrust-demo",name:"FinTrust",sector:"Financial services",description:"A fictional financial institution evaluating safe policy answers and approval requests.",initials:"FT",synthetic:1},
      {client_id:"retailflow-demo",name:"RetailFlow",sector:"Retail",description:"A fictional retailer exploring operational discrepancy investigation and recommendations.",initials:"RF",synthetic:1}
    ],
    cases: [
      {case_id:"fintrust-policy-action",client_id:"fintrust-demo",title:"Policy & Action Assistant",problem:"Employees need supported answers about purchasing policies and controlled exception requests.",business_owner:"Fictional procurement sponsor",success_metric:"Evidence-backed answer rate (not yet measured)",non_ai_alternative:"Rule-based decision tree and searchable policy portal",risk_tier:"HIGH"},
      {case_id:"retailflow-discrepancy",client_id:"retailflow-demo",title:"Operational Discrepancy Investigation",problem:"Regional teams want to investigate inconsistent inventory and operational records.",business_owner:"Fictional operations director",success_metric:"Time to explain a discrepancy (not yet measured)",non_ai_alternative:"Existing analytics dashboard with rule-based exception reports",risk_tier:"MEDIUM"},
      {case_id:"civicdata-policy",client_id:"civicdata-demo",title:"Public Service Policy Navigator",problem:"Teams need reliable policy references and must identify unsupported requests.",business_owner:"Fictional service manager",success_metric:"Supported response rate (not yet measured)",non_ai_alternative:"Curated policy search and human service workflow",risk_tier:"HIGH"}
    ],
    evidence: [
      {evidence_id:"e-sim-001",case_id:"fintrust-policy-action",evidence_class:"DECLARED",verification_status:"UNVERIFIED",source:"Synthetic stakeholder interview",summary:"Staff report difficulty locating applicable procurement rules.",created_at:"2026-11-17T00:00:00Z"},
      {evidence_id:"e-sim-002",case_id:"fintrust-policy-action",evidence_class:"DOCUMENTED",verification_status:"UNVERIFIED",source:"Synthetic policy placeholder",summary:"No reviewed policy corpus is available yet; technical validation is pending.",created_at:"2026-11-17T00:00:00Z"},
      {evidence_id:"e-sim-003",case_id:"retailflow-discrepancy",evidence_class:"DECLARED",verification_status:"UNVERIFIED",source:"Synthetic operations scenario",summary:"Regional teams suspect inconsistent inventory information; impact has not been quantified.",created_at:"2026-11-17T00:00:00Z"},
      {evidence_id:"e-sim-004",case_id:"civicdata-policy",evidence_class:"DOCUMENTED",verification_status:"UNVERIFIED",source:"Synthetic policy source description",summary:"The applicable policy versions and authority must still be established.",created_at:"2026-11-17T00:00:00Z"}
    ],
    decisions: [
      {decision_id:"d-fintrust-001",case_id:"fintrust-policy-action",stage:"DISCOVER",status:"IN_REVIEW",
       owner:"Fictional advisory reviewer",rationale:"Problem identified, but baseline and applicable policy are unverified.",
       evidence_ids:["e-sim-001","e-sim-002"],blockers:["No measured baseline","No validated policy corpus"],
       alternatives:["Rule-based decision tree","Searchable policy portal"],created_at:"2026-11-17T00:00:00Z"}
    ],
    invalidated: [],
    assessments: [],
    discoveries: [],
    evaluated: false
  });
  let db = snapshot && Array.isArray(snapshot.clients) && Array.isArray(snapshot.cases) ? copy(snapshot) : seed();
  const persist = () => {}; // Persistence is performed by the authenticated D1 route.
  const err = (status, detail) => { const error = new Error(detail); error.status = status; throw error; };

  const listClientCases = clientId => db.cases.filter(x => x.client_id === clientId).map(copy);
  function caseSnapshot(caseId) {
    const rec = db.cases.find(x => x.case_id === caseId);
    if (!rec) err(404, "Fictional use case not found");
    const client = db.clients.find(x => x.client_id === rec.client_id);
    const evidence = db.evidence.filter(x => x.case_id === caseId).map(copy);
    const decisions = db.decisions.filter(x => x.case_id === caseId).slice().reverse().map(copy);
    let unlocked = true;
    const stage_states = STAGES.map(stage => {
      const decision = decisions.find(d => d.stage === stage);
      let status = !unlocked ? "LOCKED" : decision ? decision.status : "NOT_STARTED";
      let invalidation_reason = null;
      if (status === "GO") {
        const refs = decision.evidence_ids.map(eid => evidence.find(e => e.evidence_id === eid)).filter(Boolean);
        const basis = refs.some(e => e.verification_status === "VERIFIED" &&
          ["DOCUMENTED","MEASURED"].includes(e.evidence_class));
        const measured = refs.some(e => e.verification_status === "VERIFIED" &&
          e.evidence_class === "MEASURED");
        if (db.invalidated.includes(decision.decision_id) || !basis ||
            (["VALIDATE","MEASURE_IMPROVE"].includes(stage) && !measured)) {
          status = "REWORK";
          invalidation_reason = "This recorded approval no longer has valid supporting evidence; it requires a new review.";
        }
      }
      const snapshot = {stage,status,decision:unlocked ? copy(decision || null) : null,invalidation_reason};
      unlocked = status === "GO";
      return snapshot;
    });
    return {...copy(rec),client_name:client.name,sector:client.sector,synthetic:1,
      evidence,decisions,stage_states};
  }

  function stageReport(caseId) {
    const rec = caseSnapshot(caseId);
    const lines = [
      "# " + rec.client_name + " — AI Opportunity Brief","",
      "> PRIVATE HOSTED DEMONSTRATION — SYNTHETIC RECORDS, NOT THE ORIGINAL PYTHON RUNTIME.","",
      "**Use case:** " + rec.title,
      "**Sector:** " + rec.sector,
      "**Fictional business owner:** " + rec.business_owner,
      "**Illustrative risk:** " + rec.risk_tier,"",
      "## Opportunity",rec.problem,"",
      "**Proposed success measure:** " + rec.success_metric,
      "**Non-AI alternative:** " + rec.non_ai_alternative,"",
      "## Decision journey",""
    ];
    rec.stage_states.forEach(s => {
      lines.push("### " + s.stage + " — " + s.status,"");
      if (!s.decision) {lines.push("No effective human review decision.","");return;}
      lines.push("**Recorded:** " + s.decision.status,
        "**Fictional reviewer:** " + s.decision.owner,
        "**Rationale:** " + s.decision.rationale,
        "**Open blockers:** " + (s.decision.blockers.join("; ") || "None recorded"));
      if (s.invalidation_reason) lines.push("**Evidence invalidation:** " + s.invalidation_reason);
      for (const eid of s.decision.evidence_ids) {
        const e = rec.evidence.find(x => x.evidence_id === eid);
        if (e) lines.push("- " + eid + " [" + e.evidence_class + ", " + e.verification_status + "]: " + e.summary);
      }
      lines.push("");
    });
    lines.push("## Limits","- Displayed reviewer names are self-entered; the server separately audits the signed-in account.",
      "- No genuine customer data or measurements exist.",
      "- Records are persisted as account-scoped snapshots, but are not independently verified.",
      "- A recorded GO is never a real authorization to deploy.");
    return lines.join("\n");
  }

  function evaluateAssessment(p) {
    const reasons = [];
    for (const b of p.blockers) if (b.status === "OPEN")
      reasons.push({state:b.severity === "TERMINAL" ? "NO_GO" : b.severity === "AUTHORIZATION" ? "HOLD" : "REWORK",
        detail:b.summary,next_action:b.next_action,dimension:"BLOCKER"});
    for (const c of p.checks) {
      const sources = (c.evidence_ids || []).map(eid => p.evidence.find(e => e.id === eid)).filter(Boolean);
      if (c.status === "FAIL") reasons.push({state:"NO_GO",detail:c.rationale,next_action:c.next_action,dimension:c.dimension});
      else if (c.status === "GAP") reasons.push({state:"REWORK",detail:c.rationale,next_action:c.next_action,dimension:c.dimension});
      else if (c.status === "UNKNOWN" || (c.status === "PASS" &&
        !sources.some(e => e.verification === "SIMULATED_VERIFIED" && ["DOCUMENTED","MEASURED"].includes(e.kind) &&
          (!["AI_EVALUATION","ECONOMICS"].includes(c.dimension) || e.kind === "MEASURED"))))
        reasons.push({state:"HOLD",detail:"No suitably simulated verified evidence for " + c.dimension,
          next_action:c.next_action,dimension:c.dimension});
    }
    const priority = ["NO_GO","HOLD","REWORK"];
    const recommended_state = priority.find(s => reasons.some(r => r.state === s)) || "GO";
    return {recommended_state,release_authorized:false,policy_version:"HOSTED_SYNTHETIC_1",
      rationale:reasons.length ? reasons.length + " simulated gap(s) or blocker(s) require human review." :
        "All fictional criteria were marked supported; this is not real deployment approval.",
      reasons};
  }

  function adoptionReport(rec) {
    const p = rec.scenario, v = rec.recommendation;
    return ["# Fictional AI Adoption Assessment","",
      "> HOSTED SYNTHETIC SIMULATION. NOT THE PYTHON ENGINE OR REAL CUSTOMER APPROVAL.","",
      "**Opportunity:** " + p.title,"**Client:** " + p.client_id,
      "**Risk:** " + p.risk_tier,"**Owner (fictional):** " + p.accountable_owner,
      "**Non-AI alternative:** " + p.non_ai_alternative,"",
      "## Advisory recommendation: " + v.recommended_state,"",v.rationale,"",
      "## Checks","",
      ...p.checks.map(c=>"- **"+c.dimension+" — "+c.status+"**: "+c.rationale+" | Next: "+c.next_action),
      "","## Gaps and blockers","",
      ...v.reasons.map(r=>"- "+r.state+": "+r.detail+" | Next: "+r.next_action),
      "","## Limits","- All declared verification is hypothetical.",
      "- No release or spending authorization is created.",
      "- Immutable account-scoped snapshots are retained in the hosted demonstration."].join("\n");
  }

  function evaluateDiscovery(p) {
    const issues=[];
    const mark=(state,why,action)=>issues.push({state,why,action});
    if (p.data_permission === "DENIED") mark("DO_NOT_PURSUE","Data-use permission denied","Stop the proposed path; redesign data rights.");
    if (p.data_quality === "UNUSABLE") mark("DO_NOT_PURSUE","Data are unsuitable","Stop until a valid data source is identified.");
    if (p.feasibility === "BLOCKED") mark("DO_NOT_PURSUE","Delivery is blocked","Redesign or discontinue.");
    if (p.value_status === "UNSUPPORTED") mark("DO_NOT_PURSUE","Business case unsupported","Reconsider the problem.");
    if (["UNKNOWN","RESTRICTED"].includes(p.data_permission)) mark("DISCOVERY_HOLD","Data-use rights are unresolved","Review permissions with a responsible owner.");
    if (p.baseline_status !== "SIMULATED_MEASURED" || !p.baseline_source)
      mark("DISCOVERY_HOLD","No fictional baseline source","Define a baseline and supporting source.");
    if (p.value_status === "UNKNOWN") mark("DISCOVERY_HOLD","Value hypothesis unverified","Investigate measurable business value.");
    if (p.alternative_status !== "COMPARED_SIMULATED" || !p.alternative_source)
      mark("DISCOVERY_HOLD","Non-AI alternative not compared","Compare with a feasible simpler method.");
    if (p.risk_tier === "HIGH" && p.independent_review !== "PLANNED_SIMULATED")
      mark("DISCOVERY_HOLD","High-risk review not planned","Name an independent reviewer and scope.");
    if (p.data_quality === "GAP") mark("REFINE_SCOPE","Correctable data fitness gap","Remediate the data dependency.");
    if (p.feasibility === "GAP") mark("REFINE_SCOPE","Delivery feasibility gap","Reduce or revise scope.");
    if (p.adoption_readiness === "GAP") mark("REFINE_SCOPE","Change-management gap","Plan engagement and training.");
    if (p.feasibility === "UNKNOWN" || p.adoption_readiness === "UNKNOWN" ||
        p.data_quality === "UNKNOWN") mark("DISCOVERY_HOLD","Readiness is unknown","Confirm the unknown conditions.");
    const order = ["DO_NOT_PURSUE","DISCOVERY_HOLD","REFINE_SCOPE"];
    const recommended_state = order.find(state=>issues.some(i=>i.state===state)) || "SHORTLIST_FOR_POV";
    return {recommended_state,release_authorized:false,issues,policy_version:"HOSTED_SYNTHETIC_1",
      rationale:issues.length ? "The recommendation reflects " + issues.length + " explicit simulated gap(s)." :
        "This fictional option may enter a human-approved POV selection; no pilot is authorized."};
  }
  function discoveryReport(rec) {
    const p=rec.input,v=rec.recommendation;
    const text=[
      "# Fictional AI Opportunity Discovery","",
      "> PRIVATE HOSTED DEMONSTRATION. Advisory categorization only; NOT authorization.","",
      "**Opportunity:** "+p.title,"**Client:** "+p.client_id,"**Sector:** "+p.sector,
      "**Owner (fictional):** "+p.business_owner,
      "**Affected users (fictional):** "+p.affected_users,
      "**Risk:** "+p.risk_tier,"",
      "## Business problem",p.problem,"",
      "**Current workflow:** "+p.current_workflow,
      "**Success hypothesis:** "+p.success_metric,
      "**Expected benefit (unmeasured):** "+p.expected_benefit,
      "**Non-AI alternative:** "+p.non_ai_alternative,"",
      "## Triage: "+v.recommended_state,"",v.rationale,"",
      ...v.issues.map(i=>"- "+i.state+": "+i.why+" — "+i.action),"",
      "## Conditional 30/60/90-day plan","",
      "### First 30 days — Establish evidence",
      "- Interview the fictional sponsor and affected users.",
      "- Validate baseline, data authority and non-AI comparison.",
      "- Assign an accountable reviewer to each material gap.","",
      "### Days 31–60 — Bound the evaluation",
      "- Only with explicit authorization, define the experiment and measurements.",
      "- Create test cases for quality, privacy, refusal and human intervention.",
      "- Stop if a terminal barrier remains.","",
      "### Days 61–90 — Decide and govern",
      "- Compare measured evidence to the non-AI baseline.",
      "- Document cost, safety and operating responsibilities.",
      "- Make a separate human GO/HOLD/NO_GO decision. No automatic rollout.","",
      "## Limits",
      "- This service stores only fictional, authenticated account-scoped records.",
      "- No real ROI, approval, model quality or organizational readiness was measured.",
      "- Even SHORTLIST_FOR_POV never authorizes a pilot or spending."
    ];
    return text.join("\n");
  }

  async function dispatch(path, method, p) {
    if (path === "/api/health" && method === "GET") return {status:"ok",mode:"synthetic_authenticated_d1",version:"1.1"};
    if (path === "/api/clients" && method === "GET") return db.clients.map(c=>({...copy(c),case_count:listClientCases(c.client_id).length}));
    if (path === "/api/adoption/scenarios" && method === "GET") {
      return copy(fixtures.scenarios);
    }
    if (path === "/api/adoption/assessments" && method === "GET") return db.assessments.map(a=>{
      const {scenario,recommendation,...meta}=a;return copy(meta);
    });
    if (path === "/api/adoption/assessments" && method === "POST") {
      if (!p.synthetic || !p.confirmed_fictional || !p.client_id?.endsWith("-demo"))
        err(422,"Only explicitly confirmed fictional demonstration entries are accepted.");
      if (!db.cases.some(c => c.case_id === p.case_id && c.client_id === p.client_id))
        err(422,"The fictional opportunity must belong to the selected client.");
      if (p.checks.length !== (p.risk_tier === "HIGH" ? 9 : 8)) err(422,"Complete every risk-profile dimension.");
      const scenario={...p};delete scenario.confirmed_fictional;
      const recommendation=evaluateAssessment(scenario);
      const rec={assessment_id:id("assessment-demo"),client_id:p.client_id,case_id:p.case_id,
        title:p.title,risk_tier:p.risk_tier,recommended_state:recommendation.recommended_state,
        created_at:now(),scenario,recommendation};
      db.assessments.unshift(rec);persist();return rec;
    }
    const assessmentReport=path.match(/^\/api\/adoption\/assessments\/([^/]+)\/report$/);
    if (assessmentReport && method === "GET") {
      const rec=db.assessments.find(a=>a.assessment_id===decodeURIComponent(assessmentReport[1]));
      return rec ? adoptionReport(rec) : err(404,"Synthetic assessment not found.");
    }
    if (path === "/api/discovery/assessments" && method === "GET")
      return db.discoveries.map(d=>{const {input,recommendation,...meta}=d;return copy(meta);});
    if (path === "/api/discovery/assessments" && method === "POST") {
      if (!p.synthetic || !p.confirmed_fictional || !p.client_id?.endsWith("-demo"))
        err(422,"Only explicitly confirmed fictional demonstration entries are accepted.");
      if (!db.cases.some(c => c.case_id === p.case_id && c.client_id === p.client_id))
        err(422,"The fictional opportunity must belong to the selected client.");
      const input={...p};delete input.confirmed_fictional;
      const recommendation=evaluateDiscovery(input);
      const rec={discovery_id:id("discovery-demo"),client_id:p.client_id,case_id:p.case_id,
        title:p.title,risk_tier:p.risk_tier,recommended_state:recommendation.recommended_state,
        created_at:now(),input,recommendation};
      db.discoveries.unshift(rec);persist();return rec;
    }
    const discoveryReportPath=path.match(/^\/api\/discovery\/assessments\/([^/]+)\/report$/);
    if (discoveryReportPath && method === "GET") {
      const rec=db.discoveries.find(d=>d.discovery_id===decodeURIComponent(discoveryReportPath[1]));
      return rec ? discoveryReport(rec) : err(404,"Fictional discovery not found.");
    }
    if (path === "/api/evaluations/latest" && method === "GET" && !db.evaluated)
      err(404,"No offline evaluation recorded for this authenticated account.");
    if ((path === "/api/evaluations/latest" && method === "GET") ||
        (path === "/api/evaluations/offline" && method === "POST")) {
      if (method === "POST"){db.evaluated=true;persist();}
      return {...copy(fixtures.offlineEvaluation),run_mode:"OFFLINE_DETERMINISTIC",synthetic_hosted_demo:true};
    }
    const clientPath=path.match(/^\/api\/clients\/([^/]+)$/);
    if (clientPath && method === "GET") {
      const key=decodeURIComponent(clientPath[1]);
      const client=db.clients.find(x=>x.client_id===key);
      return client ? {...copy(client),use_cases:listClientCases(key)} : err(404,"Synthetic client not found.");
    }
    const casePath=path.match(/^\/api\/cases\/([^/]+)$/);
    if (casePath && method === "GET") return caseSnapshot(decodeURIComponent(casePath[1]));
    const evidencePath=path.match(/^\/api\/cases\/([^/]+)\/evidence$/);
    if (evidencePath && method === "POST") {
      const caseId=decodeURIComponent(evidencePath[1]);
      caseSnapshot(caseId);
      if (!["DECLARED","DOCUMENTED","INFERRED"].includes(p.evidence_class) ||
          !p.source?.trim() || !p.summary?.trim()) err(422,"Source and summary are required.");
      const rec={evidence_id:id("e-demo"),case_id:caseId,evidence_class:p.evidence_class,
        verification_status:"UNVERIFIED",source:p.source.trim(),summary:p.summary.trim(),created_at:now()};
      db.evidence.push(rec);persist();return rec;
    }
    const reviewPath=path.match(/^\/api\/evidence\/([^/]+)\/review$/);
    if (reviewPath && method === "POST") {
      const rec=db.evidence.find(e=>e.evidence_id===decodeURIComponent(reviewPath[1]));
      if (!rec) err(404,"Evidence not found.");
      if (!["VERIFIED","REJECTED"].includes(p.status) || !p.reviewer?.trim() || !p.rationale?.trim())
        err(422,"Complete the fictional evidence review.");
      rec.verification_status=p.status;
      if (p.status==="REJECTED") {
        for(const d of db.decisions) if(d.case_id===rec.case_id && d.status==="GO" &&
          d.evidence_ids.includes(rec.evidence_id) && !db.invalidated.includes(d.decision_id))
          db.invalidated.push(d.decision_id);
      }
      persist();return copy(rec);
    }
    const decisionPath=path.match(/^\/api\/cases\/([^/]+)\/decisions$/);
    if (decisionPath && method==="POST") {
      const caseId=decodeURIComponent(decisionPath[1]);
      const record=caseSnapshot(caseId);
      const current=record.stage_states.find(s=>s.stage===p.stage);
      if (!current) err(422,"Unknown methodology stage.");
      if (current.status==="LOCKED") err(409,"Previous stage has not received a GO decision.");
      const refs=[...new Set(p.evidence_ids || [])];
      if (refs.some(eid=>!record.evidence.some(e=>e.evidence_id===eid)))
        err(422,"Evidence must belong to this fictional use case.");
      const blockers=(p.blockers||[]).filter(Boolean);
      if (p.status==="GO") {
        if (blockers.length) err(409,"Resolve blockers before a simulated GO.");
        const basis=record.evidence.some(e=>refs.includes(e.evidence_id) &&
          e.verification_status==="VERIFIED" && ["DOCUMENTED","MEASURED"].includes(e.evidence_class));
        if (!basis) err(409,"A simulated GO requires referenced, reviewed documentary evidence.");
        if (["VALIDATE","MEASURE_IMPROVE"].includes(p.stage) &&
          !record.evidence.some(e=>refs.includes(e.evidence_id) &&
            e.verification_status==="VERIFIED" && e.evidence_class==="MEASURED"))
          err(409,"This gate requires measured evidence. Browser preview has no such pipeline.");
      }
      const rec={decision_id:id("d-demo"),case_id:caseId,stage:p.stage,status:p.status,
        owner:p.owner,rationale:p.rationale,evidence_ids:refs,blockers,
        alternatives:(p.alternatives||[]).filter(Boolean),created_at:now()};
      db.decisions.push(rec);persist();return rec;
    }
    const reportPath=path.match(/^\/api\/cases\/([^/]+)\/executive-report$/);
    if (reportPath && method==="GET") return stageReport(decodeURIComponent(reportPath[1]));
    err(404,"This operation is not available in the hosted synthetic API.");
  }
  return {dispatch, snapshot:()=>copy(db)};
}
