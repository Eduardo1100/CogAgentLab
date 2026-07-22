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
CogAgentLab codebase or historical material. The award certificate is not
bundled; sponsorship and contribution chronology are labeled owner-attested on
the published page.

Deployment is defined in `.github/workflows/showcase-pages.yml`. GitHub Pages
must be configured to use GitHub Actions before the workflow can deploy.

The architecture schematics are original, responsive reconstructions rather
than embedded slide images. The historical runtime figure is grounded in the
same-day source and preserved chat traces; the current figure is grounded in an
immutable CogAgentLab source snapshot. Their manifests live in
`evidence/architecture_2025/` and `evidence/current_architecture_2026/`.
The editable PPTX is not bundled, but all 17 slides remain included as
full-resolution renderings. The six-name summit credit line is preserved as
hackathon-team context rather than treated as an implementation contribution
map.
