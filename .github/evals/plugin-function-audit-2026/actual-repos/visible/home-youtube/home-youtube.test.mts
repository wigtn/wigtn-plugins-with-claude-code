import assert from "node:assert/strict";
import test from "node:test";
import { getYouTubeId } from "../lib/utils/video.ts";

const id = "aB3_dE6-gH9";

test("accepts documented YouTube shapes", () => {
  assert.equal(getYouTubeId(`https://youtu.be/${id}?t=3`), id);
  assert.equal(getYouTubeId(`https://www.youtube.com/watch?v=${id}&t=3`), id);
  assert.equal(getYouTubeId(`https://youtube.com/shorts/${id}`), id);
});

test("rejects hostile hosts and invalid ids", () => {
  assert.equal(getYouTubeId(`https://youtube.com.evil.test/watch?v=${id}`), null);
  assert.equal(getYouTubeId("javascript:alert(1)"), null);
  assert.equal(getYouTubeId("https://youtu.be/short"), null);
});
