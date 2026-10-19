# Home Assistant: a state engine for your house

A [Marp](https://marp.app/) talk template about Home Assistant as a state engine —
the states you can know about a house, how to infer the ones you cannot measure,
and the three ways to run it.

## Files

| Path | Purpose |
| --- | --- |
| `slides.md` | The deck. Marp frontmatter + Markdown, one `---` per slide. |
| `themes/hass.css` | Custom Marp theme (`theme: hass`). Reskin the deck here. |
| `assets/state-loop.svg` | Diagram: devices → integrations → state machine → automations. |
| `assets/recorder.svg` | Diagram: event bus → recorder → SQLite → history. |
| `assets/power-cycle.svg` | Chart: appliance power draw with start/finish thresholds. |
| `package.json` | Marp CLI scripts. |
| `.github/workflows/pages.yml` | CI: build the deck and publish it to the `html` branch. |

## Build

```bash
npm install
npm run preview   # live preview in a browser window
npm run build     # dist/slides.html + dist/assets/
npm run pdf       # dist/slides.pdf  (needs Chrome/Chromium)
npm run pptx      # dist/slides.pptx (static, one image per slide)
npm run png       # dist/slides.001.png, .002.png, ...
```

`dist/` is generated and gitignored. The HTML build copies `assets/` next to
the deck so the SVG diagrams resolve when the file is opened or served
directly. PDF and image exports run with `--allow-local-files` so the
diagrams are embedded.

Or without installing:

```bash
npx @marp-team/marp-cli --theme-set themes --preview slides.md
```

The preview script watches `slides.md` and `themes/hass.css`.

## Publish to GitHub Pages

`.github/workflows/pages.yml` builds the deck on every push to `main` and
force-pushes a single commit to the `html` branch. GitHub Pages serves that
branch. The workflow also adds `index.html` (a copy of `slides.html`) and
`.nojekyll` so the site root and all SVG assets work unchanged.

One-time setup:

1. Push this repo to GitHub, including `package-lock.json`.
2. Let the workflow run once (**Actions → Publish slides**), or run it manually
   with **Run workflow**. This creates the `html` branch.
3. **Settings → Pages → Build and deployment**:
   - Source: **Deploy from a branch**
   - Branch: **`html`**, folder **`/ (root)`**
   - Save.

Every later push to `main` rebuilds and redeploys. The deck is then at
`https://<owner>.github.io/<repo>/` (for this repo:
`https://jduckles.github.io/talkhass/`).

Notes:

- The workflow needs `contents: write`, which is declared in the file. If your
  organization restricts `GITHUB_TOKEN` permissions, enable write access under
  **Settings → Actions → General → Workflow permissions**.
- PDF and PPTX are not built in CI: they need a local Chrome/Chromium. Run
  `npm run pdf` or `npm run pptx` and commit/attach the output if you want
  downloadable slides.
- `force_orphan: true` keeps the `html` branch to one commit per deploy, so it
  never accumulates build history.

## Editing

- **Slide breaks** are `---` lines outside code fences.
- **Per-slide directives** go in HTML comments before the slide content:
  `<!-- _class: lead -->`, `<!-- _paginate: false -->`, `<!-- _footer: '' -->`.
- **Speaker notes** are HTML comments after the slide content. They do not render
  in the HTML/PDF/PPTX output but are available in Marp's presenter view.
- **Layouts** use plain HTML (`<div class="columns">`, `.callout`, `.pill`,
  `.big`, `.muted`, `.small`). HTML is enabled by default in Marp CLI.
- **Math** works via Marp's built-in KaTeX (`$…$`, `$$…$$`) if you add it.

## Theme

`themes/hass.css` imports Marp's `default` theme and overrides it. All colours
are custom properties declared on `section`:

```css
--ink: #10202b;        /* body text */
--muted: #5a6f7e;      /* secondary text */
--paper: #f6f9fb;      /* slide background */
--panel: #e9f1f6;      /* tables, section slides */
--accent: #03a9f4;     /* Home Assistant blue */
--accent-deep: #0277bd;
--warm: #e65100;       /* warnings */
```

Change those five values and the whole deck follows. Slide classes:

- `lead` — dark title/closing slides
- `section` — tinted chapter dividers
- helper classes in the theme: `.columns`, `.callout`, `.callout.warn`,
  `.callout.quiet`, `.pill`, `.big`, `.small`, `.tiny`, `.muted`, `.center`,
  `.quote`

## Notes on accuracy

Entity IDs, service names, and config keys use the current Home Assistant
syntax (`triggers` / `conditions` / `actions`, `action:` instead of `service:`).
The recorder schema shown (`states` joined to `states_meta`) is the modern
schema; very old databases stored `entity_id` directly on `states`.

The deck deliberately avoids version numbers and prices so it stays true for
longer. Add them locally if the talk needs them.
