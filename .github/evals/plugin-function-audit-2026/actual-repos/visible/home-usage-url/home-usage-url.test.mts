import assert from "node:assert/strict";
import test from "node:test";
import { buildUsageUrl, normalizeUsageBaseUrl } from "../lib/utils/usage-url.ts";

test("normalizes and joins a pathname base", () => {
  assert.equal(normalizeUsageBaseUrl("https://api.test/root///"), "https://api.test/root");
  assert.equal(
    buildUsageUrl("https://api.test/root/", "///api/usage/totals"),
    "https://api.test/root/api/usage/totals",
  );
});

test("rejects authority and query ambiguity", () => {
  assert.equal(normalizeUsageBaseUrl("https://user@api.test"), null);
  assert.equal(normalizeUsageBaseUrl("https://api.test?x=1"), null);
  assert.equal(buildUsageUrl("file:///tmp/x", "/totals"), null);
});
