# Evidence Matrix Rules

- `Satisfied`: all material behavior is present and evidence directly supports it.
- `Partially satisfied`: a meaningful subset exists but a required path, state, or verification is missing.
- `Not satisfied`: evidence shows required behavior is absent or contradictory.
- `Not verifiable`: available artifacts cannot support a reliable conclusion.

Prefer evidence in this order: executed behavior or test, implementation at a precise file/line, generated artifact, then documented intent. Documentation alone does not prove runtime behavior.
