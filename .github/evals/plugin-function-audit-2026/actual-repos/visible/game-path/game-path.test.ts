import { describe, expect, it } from "vitest";
import { commandPath, createCommandBattle } from "../src/lib/command/engine";

describe("commandPath issue acceptance", () => {
  it("returns a deterministic shortest path without the start", () => {
    const state = createCommandBattle("oath");
    const before = structuredClone(state);
    expect(commandPath(state, "guan-yu", { x: 3, y: 4 })).toEqual([{ x: 3, y: 4 }]);
    expect(state).toEqual(before);
  });

  it("rejects blocked destinations", () => {
    const state = createCommandBattle("oath");
    expect(commandPath(state, "guan-yu", { x: 3, y: 3 })).toBeNull();
  });
});
