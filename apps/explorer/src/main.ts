import "./style.css";

import { calibrationChart, kernelChart, leaderboardChart } from "./charts";
import { cohortLabel, decimal, modelLabel, percent, shortHash, signed, titleCase } from "./format";
import type { Results, SubgroupRow } from "./types";

const appElement = document.querySelector<HTMLDivElement>("#app");

if (!appElement) {
  throw new Error("Application root not found");
}
const app: HTMLDivElement = appElement;

async function loadResults(): Promise<Results> {
  const response = await fetch(`${import.meta.env.BASE_URL}results.json`);
  if (!response.ok) {
    throw new Error(`Could not load the benchmark artefact (${response.status})`);
  }
  const data = (await response.json()) as Results;
  if (data.schema_version !== 1 || !data.artefact_sha256 || data.leaderboard.length < 2) {
    throw new Error("The benchmark artefact failed its public schema check");
  }
  return data;
}

function render(results: Results): void {
  const best = results.leaderboard[0];
  const quantum = results.leaderboard.find((row) => row.model === "bagged_quantum_kernel_svc");
  const matched = results.leaderboard.find((row) => row.model === "rbf_svc_4d");
  if (!quantum || !matched || !results.primary_comparison) {
    throw new Error("Primary comparison evidence is incomplete");
  }
  const external = results.transportability.filter((row) => row.train_cohort !== row.test_cohort);
  const externalRange = {
    minimum: Math.min(...external.map((row) => row.roc_auc)),
    maximum: Math.max(...external.map((row) => row.roc_auc)),
  };
  app.innerHTML = `
    <header class="site-header">
      <a class="brand" href="#top" aria-label="Quantum Heart Evidence Explorer home">
        <span class="brand-mark" aria-hidden="true">QH</span>
        <span><strong>Quantum Heart</strong><small>Evidence Explorer</small></span>
      </a>
      <nav aria-label="Primary navigation">
        <a href="#benchmark">Benchmark</a>
        <a href="#kernel">Kernel</a>
        <a href="#cohorts">Cohorts</a>
        <a href="#governance">Governance</a>
      </nav>
      <div class="header-actions">
        <a class="source-link" href="https://github.com/JithuVathiath/quantum-heart-disease-ensemble">Source ↗</a>
        <button class="help-button" type="button" aria-label="Open instructions">?</button>
      </div>
    </header>

    <main id="main-content">
      <section class="hero" id="top">
        <div class="hero-copy">
          <p class="eyebrow">Reproducible Quantum Machine Learning</p>
          <h1>One Published Result.<br/>Four Cohorts.<br/><em>A Harder Question.</em></h1>
          <p class="hero-intro">Does a quantum-enhanced ensemble remain convincing when leakage controls, uncertainty, compute matching, and hospital shift are made visible?</p>
          <div class="hero-actions">
            <a class="button primary" href="#benchmark">Inspect the Evidence</a>
            <a class="button secondary" href="https://doi.org/${results.publication_context.doi}">Read the IEEE Paper ↗</a>
          </div>
        </div>
        <article class="claim-card" aria-label="Published and reproduced result boundary">
          <div class="claim-label"><span></span>Evidence Boundary</div>
          <div class="claim-row published">
            <span>2025 paper</span>
            <strong>${percent(results.publication_context.reported_accuracy, 2)}</strong>
            <small>reported accuracy</small>
          </div>
          <div class="boundary-line"><span>not directly comparable</span></div>
          <div class="claim-row reproduced">
            <span>New benchmark</span>
            <strong>${decimal(quantum.roc_auc)}</strong>
            <small>bagged quantum ROC AUC</small>
          </div>
          <p>Different validation evidence is intentionally kept separate. No reproduction claim is made.</p>
        </article>
      </section>

      <section class="evidence-strip" aria-label="Key findings">
        <article><span>Strongest Model</span><strong>${modelLabel(best.model)}</strong><small>${decimal(best.roc_auc)} ROC AUC</small></article>
        <article><span>Matched Quantum Delta</span><strong class="negative">${signed(results.primary_comparison.estimate)}</strong><small>ROC AUC vs ${modelLabel(matched.model)}</small></article>
        <article><span>Study Scale</span><strong>${results.dataset.total_rows}</strong><small>records across ${results.dataset.cohorts.length} cohorts</small></article>
        <article><span>Traceability</span><strong>${results.experiment.folds} folds</strong><small>manifest ${shortHash(results.experiment.fingerprint)}</small></article>
      </section>

      <section class="section benchmark-section" id="benchmark">
        <div class="section-heading">
          <div><p class="eyebrow">01 · Comparative Evidence</p><h2>The leaderboard is an uncertainty chart,<br/>not a victory lap.</h2></div>
          <p>Every point is an out-of-fold estimate. Horizontal lines show 95% bootstrap intervals. Quantum models use a four-component representation; the matched RBF-SVC makes that feature budget explicit.</p>
        </div>
        <div class="chart-card">
          <div class="card-head"><div><span>Primary Metric</span><h3>ROC AUC by Model</h3></div><div class="legend"><span class="classical-dot"></span>Classical <span class="quantum-dot"></span>Quantum</div></div>
          ${leaderboardChart(results.leaderboard)}
        </div>
        <div class="analysis-grid">
          <article class="finding-card critical">
            <span class="finding-number">Finding 01</span>
            <h3>No Quantum Advantage Under This Protocol</h3>
            <p>The bagged quantum-kernel model trails the compute-matched RBF-SVC by <strong>${Math.abs(results.primary_comparison.estimate).toFixed(3)} ROC AUC</strong>. Its 95% paired interval remains below zero.</p>
          </article>
          <article class="finding-card">
            <span class="finding-number">Finding 02</span>
            <h3>Simplicity Holds Up</h3>
            <p>${modelLabel(best.model)} leads at ${decimal(best.roc_auc)} ROC AUC, with balanced accuracy of ${decimal(best.balanced_accuracy)} and a Brier score of ${decimal(best.brier)}.</p>
          </article>
          <article class="finding-card">
            <span class="finding-number">Finding 03</span>
            <h3>Calibration Still Matters</h3>
            <p>Ranking quality and probability quality differ. Inspect reliability bins rather than treating every score as a calibrated clinical risk.</p>
          </article>
        </div>
        <div class="interactive-card">
          <div class="card-head"><div><span>Reliability View</span><h3>Calibration Explorer</h3></div><label>Model<select id="calibration-model">${results.leaderboard.map((row) => `<option value="${row.model}">${modelLabel(row.model)}</option>`).join("")}</select></label></div>
          <div id="calibration-visual"></div>
          <p class="chart-note">The diagonal represents perfect agreement between predicted probability and observed frequency. Circle tooltips show bin support.</p>
        </div>
      </section>

      <section class="section kernel-section" id="kernel">
        <div class="section-heading light">
          <div><p class="eyebrow">02 · Inside the Kernel</p><h2>Look beyond the word “quantum.”</h2></div>
          <p>The ideal statevector simulator creates a fidelity kernel from a ${results.experiment.quantum_features}-qubit feature map. Kernel diagnostics reveal whether its geometry aligns with the observed labels.</p>
        </div>
        <div class="kernel-layout">
          <article class="circuit-card">
            <div class="card-head"><div><span>Feature Map</span><h3>ZZ Entangling Circuit</h3></div><span class="verified-chip">Qiskit ${results.environment.qiskit}</span></div>
            <div class="circuit" aria-label="Stylised four-qubit ZZ feature map">
              ${[0, 1, 2, 3].map((qubit) => `<div class="wire"><b>q${qubit}</b><span class="gate">H</span><i></i><span class="gate angle">RZ</span><i></i><span class="entangle">●</span><i></i><span class="gate angle">RZ</span></div>`).join("")}
            </div>
            <p>Inputs are reduced inside each training fold, scaled to rotation angles, and evaluated with Qiskit's deterministic fidelity statevector kernel.</p>
          </article>
          <article class="kernel-stat-card"><span>Mean Target Alignment</span><strong>${decimal(results.quantum_diagnostics.reduce((sum, row) => sum + row.kernel_target_alignment, 0) / results.quantum_diagnostics.length)}</strong><p>Low alignment helps explain weak class separation under this feature map.</p></article>
          <article class="kernel-stat-card"><span>Mean Kernel Time</span><strong>${decimal(results.quantum_diagnostics.reduce((sum, row) => sum + row.kernel_seconds, 0) / results.quantum_diagnostics.length, 2)}s</strong><p>Ideal statevector computation only; this is not quantum-hardware runtime.</p></article>
        </div>
        <div class="kernel-chart-card"><div><span>Geometry Diagnostic</span><h3>Effective Rank Across Folds</h3><p>A broad spectrum is not automatically predictive. Rank must be read alongside target alignment and external performance.</p></div>${kernelChart(results.quantum_diagnostics)}</div>
      </section>

      <section class="section cohort-section" id="cohorts">
        <div class="section-heading">
          <div><p class="eyebrow">03 · Dataset Shift</p><h2>A model crosses a hospital boundary.<br/>Its assumptions travel with it.</h2></div>
          <p>The original UCI collection combines historically different cohorts. Missingness and target prevalence change sharply, making external transfer a central validity test.</p>
        </div>
        <div class="cohort-cards">
          ${results.dataset.cohorts.map((cohort) => `<article><div><span>${cohortLabel(cohort.cohort)}</span><strong>${cohort.rows}</strong></div><div class="cohort-bar"><i style="width:${cohort.positive_rate * 100}%"></i></div><p>${percent(cohort.positive_rate)} positive · ${cohort.missing_cells} missing cells</p></article>`).join("")}
        </div>
        <div class="matrix-card">
          <div class="card-head"><div><span>Transportability Stress Test</span><h3>Train Here, Test There</h3></div><label>Model<select id="transport-model"><option value="logistic_regression">Logistic Regression</option><option value="rbf_svc">RBF-SVC</option></select></label></div>
          <div id="transport-matrix"></div>
          <p class="chart-note">Diagonal cells are apparent in-cohort fit and are shaded separately. External cells show cross-hospital ROC AUC, ranging from ${decimal(externalRange.minimum)} to ${decimal(externalRange.maximum)} in this run.</p>
        </div>
        <div class="subgroup-card">
          <div class="card-head"><div><span>Descriptive Audit</span><h3>Subgroup Stability</h3></div><label>Model<select id="subgroup-model">${results.leaderboard.filter((row) => row.model !== "dummy_prior").map((row) => `<option value="${row.model}">${modelLabel(row.model)}</option>`).join("")}</select></label></div>
          <div id="subgroup-table"></div>
        </div>
      </section>

      <section class="section governance-section" id="governance">
        <div class="section-heading light">
          <div><p class="eyebrow">04 · Research Governance</p><h2>The most professional result<br/>can be “not demonstrated.”</h2></div>
          <p>This explorer makes provenance, uncertainty, limitations, and the paper-versus-reproduction boundary first-class outputs.</p>
        </div>
        <div class="governance-grid">
          <article><span>Data</span><h3>Licensed and Fingerprinted</h3><p>UCI DOI ${results.dataset.dataset_doi} · ${results.dataset.licence}. Raw records are excluded from the public repository.</p></article>
          <article><span>Protocol</span><h3>Leakage-Safe by Construction</h3><p>Imputation, encoding, scaling, feature reduction, and calibration are fitted inside training folds.</p></article>
          <article><span>Claims</span><h3>Historical ≠ Reproduced</h3><p>The paper's reported ${percent(results.publication_context.reported_accuracy, 2)} accuracy remains historical context until its exact original protocol is recovered.</p></article>
          <article><span>Use</span><h3>Not a Medical Device</h3><p>No individual prediction interface is provided. This project cannot diagnose disease or guide treatment.</p></article>
        </div>
        <details class="limitations"><summary>Read All ${results.limitations.length} Limitations <span>+</span></summary><ol>${results.limitations.map((item) => `<li>${item}</li>`).join("")}</ol></details>
        <div class="manifest-card"><div><span>Reproducibility Manifest</span><strong>${shortHash(results.artefact_sha256)}</strong></div><dl>${Object.entries(results.environment).map(([key, value]) => `<div><dt>${titleCase(key)}</dt><dd>${value}</dd></div>`).join("")}</dl><p>Experiment <code>${results.experiment.experiment_id}</code> · seed <code>${results.experiment.seed}</code> · generated ${new Date(results.generated_at).toLocaleDateString("en-GB", { dateStyle: "long" })}</p></div>
      </section>
    </main>
    <footer><div class="brand"><span class="brand-mark" aria-hidden="true">QH</span><span><strong>Quantum Heart</strong><small>Evidence, not diagnosis.</small></span></div><p>Research and education only · Jithu Vathiath Biju · 2026</p></footer>
    <dialog class="guide-dialog" aria-labelledby="guide-title">
      <button class="dialog-close" type="button" aria-label="Close instructions">×</button>
      <p class="eyebrow">Explorer Guide</p><h2 id="guide-title">How to Read the Evidence</h2>
      <ol><li><strong>Start with the boundary.</strong><span>The paper's reported accuracy and the new benchmark use different evidence and are not merged.</span></li><li><strong>Compare intervals.</strong><span>Use uncertainty ranges, not only leaderboard order.</span></li><li><strong>Inspect the kernel.</strong><span>Target alignment and effective rank help explain the quantum result.</span></li><li><strong>Cross a cohort.</strong><span>The transport matrix exposes how performance changes between hospitals.</span></li><li><strong>Read the limitations.</strong><span>No result in this explorer supports clinical deployment.</span></li></ol>
      <button class="button primary dialog-done" type="button">Explore the Benchmark</button>
    </dialog>
  `;
  bindInteractions(results);
}

function bindInteractions(results: Results): void {
  const calibrationSelect = document.querySelector<HTMLSelectElement>("#calibration-model");
  const calibrationVisual = document.querySelector<HTMLDivElement>("#calibration-visual");
  const transportSelect = document.querySelector<HTMLSelectElement>("#transport-model");
  const transportVisual = document.querySelector<HTMLDivElement>("#transport-matrix");
  const subgroupSelect = document.querySelector<HTMLSelectElement>("#subgroup-model");
  const subgroupVisual = document.querySelector<HTMLDivElement>("#subgroup-table");
  if (!calibrationSelect || !calibrationVisual || !transportSelect || !transportVisual || !subgroupSelect || !subgroupVisual) {
    throw new Error("Interactive evidence controls are incomplete");
  }

  const renderCalibration = () => {
    const model = calibrationSelect.value;
    calibrationVisual.innerHTML = calibrationChart(results.calibration[model], modelLabel(model));
  };
  const renderTransport = () => {
    transportVisual.innerHTML = transportMatrix(results, transportSelect.value);
  };
  const renderSubgroups = () => {
    subgroupVisual.innerHTML = subgroupTable(
      results.subgroup_metrics.filter((row) => row.model === subgroupSelect.value),
    );
  };
  calibrationSelect.addEventListener("change", renderCalibration);
  transportSelect.addEventListener("change", renderTransport);
  subgroupSelect.addEventListener("change", renderSubgroups);
  renderCalibration();
  renderTransport();
  renderSubgroups();

  const dialog = document.querySelector<HTMLDialogElement>(".guide-dialog");
  const open = document.querySelector<HTMLButtonElement>(".help-button");
  const close = document.querySelector<HTMLButtonElement>(".dialog-close");
  const done = document.querySelector<HTMLButtonElement>(".dialog-done");
  if (!dialog || !open || !close || !done) throw new Error("Guide controls are incomplete");
  open.addEventListener("click", () => dialog.showModal());
  close.addEventListener("click", () => dialog.close());
  done.addEventListener("click", () => {
    dialog.close();
    document.querySelector("#benchmark")?.scrollIntoView({ behavior: "smooth" });
  });
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
}

function transportMatrix(results: Results, model: string): string {
  const cohorts = results.dataset.cohorts.map((item) => item.cohort);
  const selected = results.transportability.filter((row) => row.model === model);
  const cells = cohorts.flatMap((train) => cohorts.map((test) => selected.find((row) => row.train_cohort === train && row.test_cohort === test)));
  return `<div class="matrix" style="--columns:${cohorts.length}"><span></span>${cohorts.map((name) => `<b>${cohortLabel(name)}</b>`).join("")}${cohorts.map((train, index) => `<b>${cohortLabel(train)}</b>${cells.slice(index * cohorts.length, (index + 1) * cohorts.length).map((cell) => cell ? `<span class="matrix-cell ${cell.train_cohort === cell.test_cohort ? "diagonal" : "external"}" style="--strength:${Math.max(0, (cell.roc_auc - 0.45) / 0.55)}"><strong>${decimal(cell.roc_auc)}</strong><small>${cell.train_cohort === cell.test_cohort ? "apparent fit" : "external"}</small></span>` : `<span>—</span>`).join("")}`).join("")}</div>`;
}

function subgroupTable(rows: SubgroupRow[]): string {
  return `<div class="table-wrap"><table><thead><tr><th>Group</th><th>Support</th><th>ROC AUC</th><th>Balanced Accuracy</th><th>Sensitivity</th><th>Specificity</th></tr></thead><tbody>${rows.map((row) => `<tr><td>${titleCase(row.group)}</td><td>${row.rows} (${row.positive_rows} positive)</td>${row.status === "suppressed" ? `<td colspan="4"><span class="suppressed">Suppressed · insufficient support</span></td>` : `<td>${decimal(row.roc_auc ?? 0)}</td><td>${decimal(row.balanced_accuracy ?? 0)}</td><td>${decimal(row.sensitivity ?? 0)}</td><td>${decimal(row.specificity ?? 0)}</td>`}</tr>`).join("")}</tbody></table></div>`;
}

loadResults().then(render).catch((error: unknown) => {
  const message = error instanceof Error ? error.message : "Unknown loading error";
  app.innerHTML = `<main class="error-shell"><span class="brand-mark">QH</span><h1>Evidence unavailable</h1><p>${message}</p><p>Run the benchmark and sync its public artefact before building the explorer.</p></main>`;
});
