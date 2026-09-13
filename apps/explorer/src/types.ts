export type Interval = {
  estimate: number;
  lower: number;
  upper: number;
};

export type LeaderboardRow = {
  model: string;
  track: "classical" | "quantum";
  roc_auc: number;
  roc_auc_interval: Interval;
  balanced_accuracy: number;
  accuracy: number;
  sensitivity: number;
  specificity: number;
  brier: number;
  ece: number;
  runtime_seconds: number;
  false_negative: number;
  false_positive: number;
};

export type CohortProfile = {
  cohort: string;
  rows: number;
  positive_rows: number;
  positive_rate: number;
  duplicate_rows: number;
  missing_cells: number;
  missing_by_feature: Record<string, number>;
};

export type SubgroupRow = {
  model: string;
  group: string;
  rows: number;
  positive_rows: number;
  status: "reported" | "suppressed";
  roc_auc?: number;
  balanced_accuracy?: number;
  sensitivity?: number;
  specificity?: number;
};

export type CalibrationBin = {
  bin: number;
  rows: number;
  mean_probability: number;
  observed_rate: number;
};

export type TransportRow = {
  model: string;
  train_cohort: string;
  test_cohort: string;
  train_rows: number;
  test_rows: number;
  roc_auc: number;
  fit_seconds: number;
  validation_type?: "resubstitution" | "external";
};

export type QuantumDiagnostic = {
  fold: number;
  qubits: number;
  feature_map_reps: number;
  kernel_seconds: number;
  kernel_target_alignment: number;
  effective_rank: number;
  largest_eigenvalue: number;
  smallest_eigenvalue: number;
  condition_proxy: number;
};

export type Results = {
  schema_version: number;
  generated_at: string;
  code_revision: string;
  artefact_sha256: string;
  publication_context: {
    paper_title: string;
    doi: string;
    reported_accuracy: number;
    status: string;
  };
  experiment: {
    experiment_id: string;
    fingerprint: string;
    folds: number;
    seed: number;
    quantum_features: number;
    bagging_estimators: number;
  };
  dataset: {
    dataset_doi: string;
    licence: string;
    total_rows: number;
    feature_count: number;
    cohorts: CohortProfile[];
  };
  environment: Record<string, string>;
  leaderboard: LeaderboardRow[];
  primary_comparison: {
    estimate: number;
    lower: number;
    upper: number;
    probability_first_better: number;
  } | null;
  calibration: Record<string, CalibrationBin[]>;
  subgroup_metrics: SubgroupRow[];
  transportability: TransportRow[];
  quantum_diagnostics: QuantumDiagnostic[];
  limitations: string[];
};
