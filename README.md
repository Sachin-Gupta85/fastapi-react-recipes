# 🍳 fastapi-react-recipes — recipe box (React + FastAPI + MongoDB)

> Store recipes with ingredients, steps, cook time and ratings; search by ingredient and filter by cook time. **React** + **FastAPI** + **MongoDB**, pytest/vitest harness.

![React](https://img.shields.io/badge/React-18-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![MongoDB](https://img.shields.io/badge/MongoDB-7-47A248)
![Tests](https://img.shields.io/badge/tests-pytest%20%2B%20vitest-brightgreen)

## ✨ Features
- CRUD recipes; search by title (`?q=`), by `?ingredient=`, and `?max_minutes=`.
- Running **average rating** via atomic `$inc` of sum/count.
- Backend tested with in-memory Mongo (`mongomock`).

## 🚀 Run
```bash
docker compose up --build
cd client && npm install && npm run dev
```

## ✅ Test
```bash
./run_harness.sh                 # pytest + vitest
```

## 🔌 API
`GET /api/recipes?q=&ingredient=&max_minutes=` · `POST /api/recipes` ·
`GET|PUT /api/recipes/{id}` · `POST /api/recipes/{id}/rate` · `DELETE /api/recipes/{id}`

## 📝 License
MIT — see [LICENSE](LICENSE).
