import { describe, expect, it } from "vitest";

import { cohortLabel, modelLabel, percent, shortHash, signed, titleCase } from "../src/format";

describe("display formatting", () => {
  it("uses deliberate labels for model and cohort identifiers", () => {
    expect(modelLabel("bagged_quantum_kernel_svc")).toBe("Bagged Quantum-Kernel SVC");
    expect(cohortLabel("long-beach-va")).toBe("Long Beach VA");
  });

  it("formats evidence without hiding direction", () => {
    expect(percent(0.9016, 2)).toBe("90.16%");
    expect(signed(-0.194)).toBe("-0.194");
    expect(signed(0.02)).toBe("+0.020");
  });

  it("creates readable fallbacks and safe short hashes", () => {
    expect(titleCase("age_60_or_over")).toBe("Age 60 Or Over");
    expect(shortHash("1234567890abcdef")).toBe("1234567890ab");
  });
});

