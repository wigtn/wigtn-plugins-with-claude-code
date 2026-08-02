import assert from "node:assert/strict";
import test from "node:test";
import { buildUsageUrl, normalizeUsageBaseUrl } from "../lib/utils/usage-url.ts";

test("normalizes roots and nested prefixes", () => {
  assert.equal(normalizeUsageBaseUrl("https://api.test/"), "https://api.test");
  assert.equal(normalizeUsageBaseUrl("http://localhost:3000/root//"), "http://localhost:3000/root");
  assert.equal(buildUsageUrl("https://api.test", "/api/usage/stream"), "https://api.test/api/usage/stream");
  assert.equal(buildUsageUrl("https://api.test/root", "api/usage/stream"), "https://api.test/root/api/usage/stream");
});

test("rejects ambiguous or unsafe bases without throwing", () => {
  for (const value of [
    "ftp://api.test",
    "//api.test",
    "https://user@api.test",
    "https://api.test?a=1",
    "https://api.test#frag",
    "not a url",
    "%",
  ]) {
    assert.doesNotThrow(() => normalizeUsageBaseUrl(value));
    assert.equal(normalizeUsageBaseUrl(value), null, value);
    assert.equal(buildUsageUrl(value, "/x"), null, value);
  }
});
