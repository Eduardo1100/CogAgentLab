# Local showcase preview

Build and verify the static project record with:

```bash
make showcase
make showcase-check
```

Preview locally:

```bash
python -m http.server --directory site/dist 8000
```

Then open `http://localhost:8000`.

`site/dist` is a deterministic, self-contained bundle. Building it does not
deploy the site or change any remote state. Publication remains blocked on owner
review of attribution, licensing, award evidence, and sponsor naming.
