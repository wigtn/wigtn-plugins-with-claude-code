import { describe, expect, it } from "vitest";
import { hypotheses } from "../src/lib/game/case";
import { validateTimeline } from "../src/lib/game/engine";

describe("timeline issue acceptance", () => {
  it("keeps authored events valid and does not mutate order", () => {
    const input = structuredClone(hypotheses[0].events).reverse();
    const before = structuredClone(input);
    expect(validateTimeline(input).valid).toBe(true);
    expect(input).toEqual(before);
  });

  it("rejects a fractional minute without throwing", () => {
    const input = structuredClone(hypotheses[0].events);
    input[0].minute = 0.5;
    expect(() => validateTimeline(input)).not.toThrow();
    expect(validateTimeline(input).valid).toBe(false);
  });
});
