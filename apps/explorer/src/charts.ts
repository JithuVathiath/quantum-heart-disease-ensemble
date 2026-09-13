import type { CalibrationBin, LeaderboardRow, QuantumDiagnostic } from "./types";
import { decimal, modelLabel } from "./format";

function escape(value: string): string {
  return value.replace(/[&<>'"]/g, (character) => {
    const entities: Record<string, string> = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "'": "&#39;",
      '"': "&quot;",
    };
    return entities[character];
  });
}

export function leaderboardChart(rows: LeaderboardRow[]): string {
  const width = 920;
  const rowHeight = 58;
  const labelWidth = 244;
  const plotWidth = 610;
  const height = rows.length * rowHeight + 78;
  const minimum = 0.45;
  const maximum = 1;
  const x = (value: number) => labelWidth + ((value - minimum) / (maximum - minimum)) * plotWidth;
  const ticks = [0.5, 0.6, 0.7, 0.8, 0.9, 1];
  return `<svg class="leaderboard-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="Model ROC AUC with 95 percent confidence intervals">
    ${ticks
      .map(
        (tick) => `<g class="axis-tick"><line x1="${x(tick)}" y1="26" x2="${x(tick)}" y2="${height - 34}"/><text x="${x(tick)}" y="${height - 10}">${tick.toFixed(1)}</text></g>`,
      )
      .join("")}
    ${rows
      .map((row, index) => {
        const y = 48 + index * rowHeight;
        const colour = row.track === "quantum" ? "var(--coral)" : "var(--teal)";
        return `<g class="model-row">
          <text class="model-label" x="0" y="${y + 5}">${escape(modelLabel(row.model))}</text>
          <line class="interval" x1="${x(row.roc_auc_interval.lower)}" y1="${y}" x2="${x(row.roc_auc_interval.upper)}" y2="${y}"/>
          <line class="interval-cap" x1="${x(row.roc_auc_interval.lower)}" y1="${y - 7}" x2="${x(row.roc_auc_interval.lower)}" y2="${y + 7}"/>
          <line class="interval-cap" x1="${x(row.roc_auc_interval.upper)}" y1="${y - 7}" x2="${x(row.roc_auc_interval.upper)}" y2="${y + 7}"/>
          <circle cx="${x(row.roc_auc)}" cy="${y}" r="8" fill="${colour}"/>
          <text class="score-label" x="${Math.min(x(row.roc_auc_interval.upper) + 13, width - 42)}" y="${y + 5}">${decimal(row.roc_auc)}</text>
        </g>`;
      })
      .join("")}
  </svg>`;
}

export function calibrationChart(bins: CalibrationBin[], label: string): string {
  const width = 600;
  const height = 350;
  const pad = 46;
  const x = (value: number) => pad + value * (width - pad * 2);
  const y = (value: number) => height - pad - value * (height - pad * 2);
  const points = bins.map((bin) => `${x(bin.mean_probability)},${y(bin.observed_rate)}`).join(" ");
  return `<svg class="calibration-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="Calibration curve for ${escape(label)}">
    <line class="calibration-grid" x1="${pad}" y1="${y(0)}" x2="${x(1)}" y2="${y(1)}"/>
    <text x="${x(0.5)}" y="${height - 7}" text-anchor="middle">Mean predicted probability</text>
    <text x="14" y="${y(0.5)}" text-anchor="middle" transform="rotate(-90 14 ${y(0.5)})">Observed rate</text>
    <polyline class="calibration-line" points="${points}"/>
    ${bins
      .map(
        (bin) => `<g><circle class="calibration-point" cx="${x(bin.mean_probability)}" cy="${y(bin.observed_rate)}" r="7"><title>${bin.rows} rows · predicted ${decimal(bin.mean_probability)} · observed ${decimal(bin.observed_rate)}</title></circle></g>`,
      )
      .join("")}
  </svg>`;
}

export function kernelChart(rows: QuantumDiagnostic[]): string {
  const width = 620;
  const height = 300;
  const pad = 46;
  const maxRank = Math.max(...rows.map((row) => row.effective_rank)) * 1.12;
  const barWidth = (width - pad * 2) / rows.length - 18;
  return `<svg class="kernel-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="Effective quantum kernel rank by validation fold">
    ${rows
      .map((row, index) => {
        const available = (width - pad * 2) / rows.length;
        const x = pad + index * available + 9;
        const barHeight = (row.effective_rank / maxRank) * (height - pad * 2);
        return `<g><rect x="${x}" y="${height - pad - barHeight}" width="${barWidth}" height="${barHeight}" rx="7"/><text x="${x + barWidth / 2}" y="${height - 19}" text-anchor="middle">F${row.fold + 1}</text><text class="bar-value" x="${x + barWidth / 2}" y="${height - pad - barHeight - 9}" text-anchor="middle">${row.effective_rank.toFixed(1)}</text></g>`;
      })
      .join("")}
  </svg>`;
}

