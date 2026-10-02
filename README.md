# Unit converter website

Simple self-hosted unit converting website

## Why?

So, basically, i been *really* bored recently, a decided "hey, a want to try all that webdev stuff"
even throu i never did something like that before, and, well, i did, normally for that type of task people use
frameworks such as Flask or Django, but where the sport in it? So, for the sake of sport, i decided
to make it on pure python, like no JS, no extra framework and nominal almount of CSS styling, and for that
exact reason i also decided to create server side render (SSR) of pages instead of just creating more of those pages,
overall it’s been… not that bad actually, in sense of developing experiense, i might do something similar in the future
but with frameworks.

> [!WARNING]
> This probally shoud be obvious, but this project is not a production-ready, it’s
> lack many safety features, such as any form of defense against DoS and DDoS attack, doesn’t
> use HTTPS porotocol and some other things that i didn’t mention here, so don’t use it for production


## Features
-- No extra liblary (pure python)
-- server-side rendering (SSR)
-- stateless (no cookies, no database, no sessions, etc)
-- input validation, included edge-case scenarios

## Tech Stack
-- Python (3.11+)
-- http.server

## Quick Start
Run project directly using "uv" or python:
<!-- TODO -->
<!-- add real project name -->
```bash
git clone [https://github.com/blobaRealOne/projectname]
python main.py
```
then just input "http://localhost:8000" in you browser and call it a day
