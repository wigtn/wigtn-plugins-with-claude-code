import { describe, expect, it } from "vitest";
import { commandPath, createCommandBattle } from "../src/lib/command/engine";

describe("hidden commandPath invariants", () => {
  it("uses deterministic y-then-x tie breaking", () => {
    const state = createCommandBattle("oath");
    const unit = state.heroes.find((hero) => hero.id === "guan-yu")!;
    unit.position = { x: 3, y: 5 };
    state.heroes.find((hero) => hero.id === "liu-bei")!.position = { x: 0, y: 6 };
    state.heroes.find((hero) => hero.id === "zhang-fei")!.position = { x: 6, y: 6 };
    expect(commandPath(state, "guan-yu", { x: 2, y: 4 })).toEqual([
      { x: 3, y: 4 },
      { x: 2, y: 4 },
    ]);
  });

  it("rejects occupied, blocked, outside, and over-budget targets", () => {
    const state = createCommandBattle("oath");
    expect(commandPath(state, "guan-yu", { x: 2, y: 5 })).toBeNull();
    expect(commandPath(state, "guan-yu", { x: 3, y: 3 })).toBeNull();
    expect(commandPath(state, "guan-yu", { x: -1, y: 4 })).toBeNull();
    expect(commandPath(state, "guan-yu", { x: 3, y: 0 })).toBeNull();
    expect(commandPath(state, "missing", { x: 3, y: 4 })).toBeNull();
  });

  it("does not mutate state", () => {
    const state = createCommandBattle("oath");
    const before = structuredClone(state);
    commandPath(state, "guan-yu", { x: 3, y: 4 });
    expect(state).toEqual(before);
  });
});
