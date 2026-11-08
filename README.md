# Unit converter website

Simple self-hosted unit converting website.

Project idea based from [roadmap.sh](https://roadmap.sh/projects/unit-converter).

> [!WARNING]
> This probably should be obvious, but this project is not production-ready.

## Features
- No extra libraries (pure Python)
- Server-side rendering (SSR)
- Stateless (no cookies, no database, no sessions, no accounts, etc.)
- Input validation, including edge-case scenarios
- Test coverage

## Tech Stack
- Python 3.15+
- http.server

## Installation

Clone the repository:

```bash
git clone https://github.com/blobaRealOne/unit-converter-website.git
cd unit-converter-website
```

## Usage

**Using uv:**

```bash
uv run main.py
```

**Using Python:**

```bash
python main.py
```

Then open http://localhost:8000 in your browser.
