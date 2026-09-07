# Contributing

Liu Xi Growth Analytics Portfolio welcomes changes that improve analytical correctness, reproducibility, accessibility, or documentation without weakening the public-data boundary.

## Local quality gate

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m ruff format --check .
python -m pytest
```

When adding or changing an analytical method:

1. document the estimand, formula, assumptions and claim boundary;
2. add a numerical gold case or invariant test;
3. keep metric logic separate from presentation components;
4. validate request data at the API boundary;
5. use only synthetic, normalized or appropriately licensed public data;
6. update the metric dictionary, methodology or decision guide when behavior changes.

Do not commit generated databases, credentials, production exports, confidential internal identifiers, or screenshots containing private data. A change that adds a business claim must also add or update its evidence and boundary test.
