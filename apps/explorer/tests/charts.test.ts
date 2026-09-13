import { describe, expect, it } from "vitest";

import { calibrationChart, kernelChart, leaderboardChart } from "../src/charts";
import type { LeaderboardRow } from "../src/types";

const row: LeaderboardRow = {
  model: "logistic_regression",
  track: "classical",
  roc_auc: 0.89,
  roc_auc_interval: { estimate: 0.89, lower: 0.84, upper: 0.93 },
  balanced_accuracy: 0.81,
  accuracy: 0.81,
  sensitivity: 0.78,
  specificity: 0.84,
  brier: 0.13,
  ece: 0.05,
  runtime_seconds: 0.04,
  false_negative: 31,
  false_positive: 26,
};

describe("accessible SVG charts", () => {
  it("renders leaderboard intervals and labels", () => {
    const chart = leaderboardChart([row]);
    expect(chart).toContain("95 percent confidence intervals");
    expect(chart).toContain("Logistic Regression");
    expect(chart).toContain("0.890");
  });

  it("renders calibration support and kernel folds", () => {
    expect(
      calibrationChart([{ bin: 1, rows: 20, mean_probability: 0.2, observed_rate: 0.25 }], "Model"),
    ).toContain("20 rows");
    expect(
      kernelChart([
        {
          fold: 0,
          qubits: 4,
          feature_map_reps: 2,
          kernel_seconds: 0.3,
          kernel_target_alignment: 0.05,
          effective_rank: 89,
          largest_eigenvalue: 20,
          smallest_eigenvalue: 0.001,
          condition_proxy: 20000,
        },
      ]),
    ).toContain("F1");
  });
});

