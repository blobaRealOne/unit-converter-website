# Unit converter website

Simple self-hosted unit converting website

## Why?

So, basically, I've been *really* bored recently, and decided "hey, I want to try all that webdev stuff"
even though I never did something like that before, and, well, I did. Normally for that type of task people use
frameworks such as Flask or Django, but where's the sport in it? So, for the sake of sport, I decided
to make it in pure Python, like no JS, no extra frameworks and a nominal amount of CSS styling. For that
exact reason I also decided to create server-side rendering (SSR) of pages instead of just creating more of those pages.
Overall it’s been… not that bad actually, in sense of developing experience. I might do something similar in the future
but with frameworks and stuff.

> [!WARNING]
> This probably should be obvious, but this project is not production-ready. It
> lacks many safety features, such as any form of defense against DoS and DDoS attacks, doesn’t
> use HTTPS protocol and some other things that I didn’t mention here, so don’t use it for production.


## Features
- No extra libraries (pure Python)
- Server-side rendering (SSR)
- Stateless (no cookies, no database, no sessions, no accounts, etc.)
- Input validation, including edge-case scenarios

## Tech Stack
- Python (3.14+)
- http.server

## Quick Start
Run project directly using "uv" or Python:
```bash
git clone https://github.com/blobaRealOne/unit-converter-website.git
cd unit-converter-website
```

for python:

```bash
python main.py
```

for uv:

```bash
uv run main.py
```

then just input "http://localhost:8000" in your browser and there you have it
