import { describe, expect, it } from "vitest";
import { hypotheses } from "../src/lib/game/case";
import { validateTimeline } from "../src/lib/game/engine";

describe("hidden timeline invariants", () => {
  it.each([Number.NaN, Number.POSITIVE_INFINITY, -1, 10.5, 11])(
    "rejects malformed minute %s without throwing",
    (minute) => {
      const input = structuredClone(hypotheses[0].events);
      input[0].minute = minute;
      const before = structuredClone(input);
      expect(() => validateTimeline(input)).not.toThrow();
      expect(validateTimeline(input).valid).toBe(false);
      expect(input).toEqual(before);
    },
  );

  it("requires the exact minute set and returns unique reasons", () => {
    const input = structuredClone(hypotheses[0].events);
    input[10].minute = 9;
    const result = validateTimeline(input);
    expect(result.valid).toBe(false);
    expect(new Set(result.reasons).size).toBe(result.reasons.length);
  });

  it.each(["action", "claim"] as const)("rejects blank %s text", (field) => {
    const input = structuredClone(hypotheses[0].events);
    input[3][field] = "   ";
    expect(validateTimeline(input).valid).toBe(false);
  });

  it("does not mutate nested events and preserves authored validity", () => {
    for (const hypothesis of hypotheses) {
      const input = structuredClone(hypothesis.events).reverse();
      const before = structuredClone(input);
      expect(validateTimeline(input)).toEqual({ valid: true, reasons: [] });
      expect(input).toEqual(before);
    }
  });
});
