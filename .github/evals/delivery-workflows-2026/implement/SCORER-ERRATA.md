# Implement scorer erratum

The frozen scorer identified a skill load only when a model log repeated the
literal sentence `This is an explicit-only delivery workflow`.

That marker was model-dependent. GPT-5.5 repeated it in 12/12 verified runs.
GPT-5.6 Sol repeated it in 5/12, but logged a read of
`skills/verified-delivery/references/delivery-evidence.md` in 12/12. Bare and
ordinary-treatment logs contained neither path in 0/24 runs.

The repaired scorer therefore treats either the skill file path or its required
reference path as the routing trace. No model call, fixture, patch, or functional
score was changed. The original scorer is preserved as
`score.frozen-routing-marker.py`; its SHA-256 matches the pre-run manifest.
