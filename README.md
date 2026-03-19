[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-FF5E5B?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/ysuleyman)
[![Swagger](https://img.shields.io/badge/OpenAPI-Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://hadislam.org/docs)
[![ReDoc](https://img.shields.io/badge/OpenAPI-ReDoc-8A2BE2?style=for-the-badge&logo=redoc&logoColor=white)](https://hadislam.org/redoc)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

<img src="./static/hadith.svg" width="100%" />

**TL;DR** Check out the [swagger](https://hadislam.org/docs) documentation and test it. It's completely free.

⚠️ The API is currently under development therefore endpoints may vary ⚠️

# 🌙 Hadith REST API

Free and Open Source Multilingual (arabic (+diacritics), english, bengali, indonesian, french, turkish, tamil, russian) REST API for most popular hadith editions including :

- Forty Hadith of Shah Waliullah Dehlawi
- Muwatta Malik
- Sahih al Bukhari
- Sahih Muslim
- Sunan Abu Dawud
- Sunan an Nasai
- Jami At Tirmidhi
- Forty Hadith of an-Nawawi
- Sunan Ibn Majah
- Forty Hadith Qudsi

Not all editions support all of those languages but english and arabic are present for all.

The API is available here : [hadislam.org/](https://hadislam.org/)

**Quick summary**

Open-source REST API developed with [FastAPI](https://fastapi.tiangolo.com/) for structured access to:

- The most popular editions
- Related books (_i.e_ a big chapter of an edition)
- Language-aware hadith
- Grade for hadith

## Features

- FastAPI-based REST API
- OpenAPI docs (`/docs`) and ReDoc (`/redoc`)
- Pagination support for list endpoints
- Optional language filtering

## API

### Endpoints

#### Root

- `GET /` — API metadata and docs links

#### Edition

- `GET /editions/` — List all editions
- `GET /editions/{slug}` — Get one edition by its hyphen separated latinized english name (i.e _slug_)

#### Book

- `GET /books/` — List books
- `GET /books/{book_id}` — Get one book by his unique id
- `GET /editions/{slug}/books` — List edition's books
- `GET /editions/{slug}/books/{book_index}` — Get an edition's book at position `book_index`

#### Hadith

- `/hadiths` — List hadiths
- `/hadiths/{hadith_id}` — Get one book by his unique id
- `/editions/{slug}/hadiths` — List edition's hadiths
- `/editions/{slug}/hadiths/{hadith_index}.{hadith_index_minor}` — Get one minor (that is a sub hadith of a hadith) hadith by his numerical position inside the edition
- `/editions/{slug}/hadiths/{hadith_index}` — Get one hadith (including his sub-hadith) by his numerical position inside the edition
- `/editions/{slug}/books/{book_index}/hadiths` — List hadiths of an edition's book
  `/editions/{slug}/books/{book_index}/hadiths/{book_hadith_index}` — Get one hadith (including his sub-hadith) by his relative numerical position inside the book

#### Search

- `/search/{}`

## Quick Start

### Requirements

- Python `>=3.12`
- `uv` package manager
- `pre-commit`

### Install

```bash
uv sync
```

### Run (development)

```bash
uv run fastapi run src/main.py --reload
```

### Run tests

```bash
uv run pytest tests -v --durations=0 --cov --cov-report=term-missing
```

### Run checks

**Type**

```
uv run ty check .
```

**Format**

```
uv run ruff check .
```

### Run format

```
uv run ruff format .
```

## 📜 License

This project is licensed under the MIT License. See `LICENSE`.

## 💬 Feedback

Have suggestions, feedback, or need support? Open an issue or start a discussion — we’d love to hear from you.

## 🤝 Contributing

We welcome all kinds of contributions! Here's how you can help :

**✅ Improve the Dataset**

_to be written_

**♥️ Financial support**

If you want to support me financially you can [buy me a coffee](https://ko-fi.com/ysuleyman) it will certainly motivate me on continously improving the REST API. May Allah rewards you !

**📬 A quick thank-you**

If this project helped you, you can send me a message (a comment) on Ko-fi.  
You don’t have to donate — even a simple message of support or a quick “thank you” means a lot and keeps me motivated to continue improving this project.

👉 Write a comment [here](https://ko-fi.com/post/Supporting-the-Esmaul-Husna-REST-API-Z8Z01MKPMF) at the very bottom of the article.

Your encouragement truly makes a difference 🙌
Feel free to send a message — your encouragement keeps this project alive!
