# Development

This repository contains two packages that share one name and are released
independently:

- **PyPI** `django-crudlink`: the Django app (`django_crudlink`)
- **npm** `django-crudlink`: the JavaScript package

## Project structure

```
.
├── django_crudlink/            # Django app → PyPI package
│   ├── __init__.py             # __version__ is read from the installed package metadata
│   ├── apps.py                 # CrudlinkConfig
│   └── static/django_crudlink/ # built JS/CSS for Django (gitignored, built by `npm run build:django`)
├── frontend/                   # JavaScript source → npm package (and Django static build)
├── .github/
│   ├── workflows/publish.yml       # py-v* release → PyPI
│   ├── workflows/publish-npm.yml   # npm-v* release → npm
│   └── dependabot.yml
├── pyproject.toml              # Python package config + PyPI version
├── package.json                # JS project config + npm version
├── package-lock.json
├── README.md                   # shown on both PyPI and npm
└── LICENSE
```

All JS tooling config (`package.json`, and later `vite.config.*`,
`tsconfig.json`, etc.) lives in the repository root. `frontend/` contains only
source code.

What goes into each package:

| Package | Contents | Controlled by |
| --- | --- | --- |
| PyPI wheel/sdist | `django_crudlink/` (including built static files), `README.md`, `LICENSE` | `[tool.uv.build-backend]` in `pyproject.toml` |
| npm tarball | paths listed in `files`, plus `package.json`, `README.md`, `LICENSE` | `files` in `package.json` |

## Setup

```bash
uv venv          # or use the existing venv/
uv pip install -e .
npm install
```

## Building locally

```bash
npm run build:django   # JS build for Django static files (once defined)
uv build               # → dist/*.whl, dist/*.tar.gz

npm run build:npm      # JS build for the npm package (once defined)
npm pack --dry-run     # list what would be published to npm
```

## Versioning

- The two packages have **independent versions**:
  - PyPI: `version` in `pyproject.toml`. This is the only place to change it, because `django_crudlink.__version__` is read from the installed metadata.
  - npm: `version` in `package.json` (and `package-lock.json`, which `npm version` updates).
- Follow [SemVer](https://semver.org/). While on `0.x`, a **minor** bump may break things and a **patch** bump is for fixes. Move to `1.0.0` once the API is stable.
- **A version can never be re-used.** PyPI and npm reject re-uploads of an existing version, even after it has been deleted. To fix a bad release, publish a new version.

### Bump commands

Python (PyPI):

```bash
uv version --short               # print current version
uv version --bump patch          # 0.0.1 → 0.0.2
uv version --bump minor          # 0.0.2 → 0.1.0
uv version --bump major          # 0.1.0 → 1.0.0
uv version 0.2.0b1               # set an explicit version (e.g. pre-release)
```

JavaScript (npm):

```bash
npm pkg get version                            # print current version
npm version patch --no-git-tag-version         # 0.0.1 → 0.0.2
npm version minor --no-git-tag-version
npm version major --no-git-tag-version
npm version 0.2.0-beta.1 --no-git-tag-version  # explicit version
```

Always pass `--no-git-tag-version`. Without it, npm creates its own commit and a
`vX.Y.Z` tag, which does not follow the tag naming below.

## Tag naming

| Tag | Publishes to | Workflow |
| --- | --- | --- |
| `py-vX.Y.Z` | PyPI | `.github/workflows/publish.yml` |
| `npm-vX.Y.Z` | npm | `.github/workflows/publish-npm.yml` |

- The tag version must equal the version in the package file. CI fails the release otherwise.
- Tags exist only on GitHub. PyPI and npm show the version from `pyproject.toml` / `package.json`, not the tag name.
- `v0.0.1` is the legacy tag of the first PyPI release, made before this scheme. Don't create new `v*` tags.

## Release checklist

1. Bump the version (see above).
2. Commit and push to `main`:
   ```bash
   git commit -am "Release py-v0.0.2"
   git push
   ```
3. Create a GitHub release, which triggers the publish workflow:
   ```bash
   gh release create py-v0.0.2 --generate-notes     # PyPI
   gh release create npm-v0.0.2 --generate-notes    # npm
   ```
   Or in the GitHub UI: Releases → Draft a new release → choose tag → create new tag on `main` → Publish release.
4. If the environment requires a reviewer: Actions → the run → Review deployments → Approve.
5. Check https://pypi.org/project/django-crudlink/ or https://www.npmjs.com/package/django-crudlink.

If the release was created with a wrong tag (so the tag check fails), delete the release
and the tag, fix the version, and create the release again:

```bash
gh release delete py-v0.0.2 --cleanup-tag
```
