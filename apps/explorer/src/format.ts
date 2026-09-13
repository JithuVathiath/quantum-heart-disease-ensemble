export const MODEL_LABELS: Record<string, string> = {
  logistic_regression: "Logistic Regression",
  extra_trees: "Extra Trees",
  rbf_svc: "RBF-SVC · Full",
  rbf_svc_4d: "RBF-SVC · Four Features",
  hist_gradient_boosting: "Gradient Boosting",
  quantum_kernel_svc: "Quantum-Kernel SVC",
  bagged_quantum_kernel_svc: "Bagged Quantum-Kernel SVC",
  dummy_prior: "Prior-Only Baseline",
};

export const COHORT_LABELS: Record<string, string> = {
  cleveland: "Cleveland",
  hungarian: "Hungarian",
  switzerland: "Switzerland",
  "long-beach-va": "Long Beach VA",
};

export function modelLabel(value: string): string {
  return MODEL_LABELS[value] ?? titleCase(value);
}

export function cohortLabel(value: string): string {
  return COHORT_LABELS[value] ?? titleCase(value);
}

export function titleCase(value: string): string {
  return value
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function percent(value: number, digits = 1): string {
  return `${(value * 100).toFixed(digits)}%`;
}

export function decimal(value: number, digits = 3): string {
  return value.toFixed(digits);
}

export function signed(value: number, digits = 3): string {
  return `${value >= 0 ? "+" : ""}${value.toFixed(digits)}`;
}

export function shortHash(value: string): string {
  return value.slice(0, 12);
}
