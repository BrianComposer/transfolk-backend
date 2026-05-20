# TransFolk Backend

`transfolk-backend` is the FastAPI server application for TransFolk symbolic folk melody generation. It exposes HTTP endpoints for model discovery, prompt-based generation, file-conditioned generation and generated output serving.

This repository is part of the TransFolk ecosystem and depends on `transfolk-core`, which contains the reusable symbolic music processing, tokenization, transformer modelling, training and generation logic.

---

## Author
Brian Martínez-Rodríguez

GitHub: https://github.com/BrianComposer

Email: info@brianmartinez.music

Web: www.brianmartinez.music

---

## Role in the TransFolk ecosystem

The recommended TransFolk architecture is split into independent repositories:

```text
transfolk-core
    reusable Python library for symbolic music processing, tokenization,
    models, training, generation and evaluation

transfolk-backend
    FastAPI backend for loading released models and serving generation endpoints

transfolk-frontend
    web interface for rendering scores, playback and user interaction

teimus
    independent research project for religious/profane folk melody classification
```

Dependency direction:

```text
transfolk-backend  ->  transfolk-core
transfolk-frontend ->  transfolk-backend
teimus             ->  transfolk-core
```

`transfolk-backend` should not contain duplicated tokenizer, model, training or generation code. Those components belong to `transfolk-core`.

---

## Repository structure

```text
transfolk-backend/
├── data/
├── data_tokenized/
├── db/
├── db_admin/
├── experiments/
├── models/
├── models_classifier/
├── outputs/
├── scripts/
├── src/
│   └── transfolk_backend/
│       ├── routes/
│       ├── services/
│       ├── __init__.py
│       ├── app.py
│       ├── config.py
│       └── main.py
├── .gitignore
├── pyproject.toml
└── README.md
```

---

## Main directories

| Directory | Purpose |
|---|---|
| `src/transfolk_backend/` | Importable backend package. Contains the FastAPI app, routes, services and backend configuration. |
| `routes/` | API route modules, such as model listing, generation and health checks. |
| `services/` | Backend service layer, including model registry, pipeline cache and generation orchestration. |
| `scripts/` | Operational scripts for local use, training, generation, preprocessing or maintenance. |
| `models/released/` | Local or production mount point for released model metadata and final inference artifacts. |
| `outputs/` | Generated files produced by the API. In production this should be writable storage. |
| `data/` | Local corpus data. This is not required in production. |
| `data_tokenized/` | Local tokenized corpus data. This is not required in production. |
| `experiments/` | Local experiment results, metrics, figures and logs. This is not required in production. |
| `db/` | Database-related utilities or configuration registry components, if used by the backend. |
| `db_admin/` | Optional local database administration tool. This may later become a separate repository. |
| `models_classifier/` | Temporary migration directory for classifier artifacts. TEIMUS-specific models should eventually live in the TEIMUS repository. |

---

## Installation for local development

Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Upgrade packaging tools:

```powershell
python -m pip install --upgrade pip setuptools wheel
```

Install `transfolk-core` from the local sibling repository:

```powershell
pip install -e ..\transfolk-core
```

Install the backend in editable mode:

```powershell
pip install -e .
```

For development tools:

```powershell
pip install -e ".[dev]"
```

Check that the backend package is importable:

```powershell
python -c "import transfolk_backend; print('transfolk-backend ok')"
```

---

## Running the API locally

The preferred entry point is the FastAPI app inside the package:

```powershell
uvicorn transfolk_backend.app:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

If the project uses `main.py` as the actual FastAPI entry point, run:

```powershell
uvicorn transfolk_backend.main:app --reload
```

The final repository should standardize on one main entry point. The recommended one is:

```text
transfolk_backend.app:app
```

---

## Production deployment model

The production backend should contain only what is needed for inference:

```text
backend code
transfolk-core dependency
released model metadata
released model weights
vocabulary files
writable output directory
```

The production server should not contain:

```text
full corpora
training datasets
tokenized corpora
experiment folders
paper figures
training logs
intermediate checkpoints
```

Recommended production layout:

```text
/app
├── src/transfolk_backend/
├── models/released/
└── outputs/
```

Model weights may be provided through:

```text
manual upload
persistent server volume
GitHub Releases
Hugging Face Hub
Zenodo
external storage
```

Large model files should not be committed directly to Git.

---

## Local data and experiments

The following directories are intended for local development or research workflows:

```text
data/
data_tokenized/
experiments/
outputs/
models/
models_classifier/
```

Their heavy contents are ignored by Git. The repository may keep lightweight `README.md` or `.gitkeep` files to preserve the directory structure.

---

## Environment variables

The backend should avoid hard-coded absolute paths. In local and production environments, paths should be configurable through environment variables or configuration files.

Recommended variables:

```text
TRANSFOLK_ENV=development
TRANSFOLK_MODELS_DIR=./models/released
TRANSFOLK_OUTPUTS_DIR=./outputs
TRANSFOLK_DATA_DIR=./data
```

In production:

```text
TRANSFOLK_ENV=production
TRANSFOLK_MODELS_DIR=/app/models/released
TRANSFOLK_OUTPUTS_DIR=/app/outputs
```

The backend should use these paths when available and fall back to project-relative paths for local development.

---

## Import conventions

Backend code should import reusable TransFolk functionality from `transfolk-core`:

```python
from transfolk_core.config.resolver import PathResolver
from transfolk_core.pipeline.pipeline import GenerationPipeline
from transfolk_core.tokenization.tokenizer import MoMeTTokenizer
```

Backend-specific components should use the `transfolk_backend` namespace:

```python
from transfolk_backend.services.model_registry import ModelRegistry
from transfolk_backend.services.pipeline_cache import PipelineCache
```

Legacy imports from the old monolithic project should be removed progressively:

```python
from transfolk_config ...
from transfolk_tokenization ...
from transfolk_preprocesing ...
from transfolk_features ...
from transfolk_metrics ...
from transfolk_patterns ...
from transfolk ...
```

---

## Development checklist

Before working on routes or generation endpoints, check:

```powershell
python -c "import transfolk_backend; print('backend import ok')"
python -c "import transfolk_core; print('core import ok')"
pip check
```

Then start the API:

```powershell
uvicorn transfolk_backend.app:app --reload
```

After the API starts, check:

```text
http://127.0.0.1:8000/docs
```

The first milestone is to make the API documentation page load correctly. The second milestone is to make `/models` work. The third milestone is to make `/generate` and `/generate_from_prompt` work using the new `transfolk-core` imports.

---

## Notes on TEIMUS

TEIMUS should be kept as an independent repository. Classifier-specific code, religious/profane labels, classifier models, ablation studies, interpretability outputs and TEIMUS experiment results should not remain in `transfolk-backend`.

During migration, `models_classifier/` may temporarily remain here, but the final target should be:

```text
teimus/
├── src/teimus/
├── models/
├── experiments/
└── outputs/
```

---

## License

This project is distributed under the license specified in the `LICENSE` file.
