import assert from "node:assert/strict";
import test from "node:test";
import { getYouTubeId } from "../lib/utils/video.ts";

const id = "Z9-_aB3cD7e";

test("supports the complete accepted host/path matrix", () => {
  assert.equal(getYouTubeId(`https://m.youtube.com/watch?v=${id}#x`), id);
  assert.equal(getYouTubeId(`https://www.youtube.com/embed/${id}?rel=0`), id);
  assert.equal(getYouTubeId(`https://www.youtube-nocookie.com/embed/${id}`), id);
  assert.equal(getYouTubeId(`https://youtu.be/${id}`), id);
});

test("rejects authority, scheme, encoding, and shape attacks", () => {
  for (const value of [
    `http://youtube.com/watch?v=${id}`,
    `https://user:pass@youtube.com/watch?v=${id}`,
    `https://notyoutube.com/watch?v=${id}`,
    `https://youtube.com.evil.test/watch?v=${id}`,
    `//youtube.com/watch?v=${id}`,
    `https://youtube.com/watch?v=${id}extra`,
    `https://youtube.com/watch?v=%ZZ`,
    `https://youtu.be/${id}/extra`,
    `data:text/plain,${id}`,
  ]) {
    assert.equal(getYouTubeId(value), null, value);
  }
});

test("never throws for malformed values represented as strings", () => {
  for (const value of ["", "%", "https://", "\u0000", "not a url"]) {
    assert.doesNotThrow(() => getYouTubeId(value));
    assert.equal(getYouTubeId(value), null);
  }
});
