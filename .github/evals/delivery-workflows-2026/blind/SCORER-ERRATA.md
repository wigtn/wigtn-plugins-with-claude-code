# Blind scorer erratum

All eight judge calls completed successfully. The frozen scorer then globbed
every `*.json` file in each judge directory, which unintentionally included its
own `*.meta.json` runtime records. Those records do not contain candidate
scores, so aggregation stopped with `KeyError: candidates`.

The repaired scorer skips files ending in `.meta.json`. Judge outputs, blind
mapping, prompts, patches, and scores are unchanged. The original scorer is
preserved as `score.frozen-meta-glob.py`; its SHA-256 matches the pre-run
manifest.
