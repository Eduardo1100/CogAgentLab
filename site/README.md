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
deploy the site or change any remote state. `SHOWCASE-LICENSING.md` defines the
narrow licensing boundary for this showcase without relicensing the existing
CogAgentLab codebase or historical material. Award and sponsor claims remain
outside the published page.

Deployment is defined in `.github/workflows/showcase-pages.yml`. GitHub Pages
must be configured to use GitHub Actions before the workflow can deploy.
