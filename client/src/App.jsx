import React, { useEffect, useState } from "react";
import { listRecipes, createRecipe, rateRecipe, deleteRecipe } from "./api.js";

export default function App() {
  const [recipes, setRecipes] = useState([]);
  const [ingredient, setIngredient] = useState("");
  const [title, setTitle] = useState("");
  const [ingredients, setIngredients] = useState("");
  const [minutes, setMinutes] = useState(15);

  async function refresh(ing = ingredient) { setRecipes(await listRecipes("", ing)); }
  useEffect(() => { refresh(""); }, []);

  async function onAdd(e) {
    e.preventDefault();
    if (!title.trim()) return;
    await createRecipe({
      title: title.trim(),
      ingredients: ingredients.split(",").map((s) => s.trim()).filter(Boolean),
      steps: [], minutes: Number(minutes) || 0, tags: [],
    });
    setTitle(""); setIngredients(""); refresh();
  }

  return (
    <main style={{ maxWidth: 680, margin: "2rem auto", fontFamily: "system-ui" }}>
      <h1>🍳 Recipes</h1>
      <form onSubmit={onAdd} style={{ display: "grid", gap: 8, marginBottom: 16 }}>
        <input aria-label="title" placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
        <input aria-label="ingredients" placeholder="Ingredients (comma-separated)" value={ingredients} onChange={(e) => setIngredients(e.target.value)} />
        <input aria-label="minutes" type="number" value={minutes} onChange={(e) => setMinutes(e.target.value)} />
        <button type="submit">Add recipe</button>
      </form>
      <input aria-label="filter-ingredient" placeholder="Filter by ingredient…" value={ingredient}
        onChange={(e) => { setIngredient(e.target.value); refresh(e.target.value); }} style={{ width: "100%", marginBottom: 12 }} />
      <ul style={{ listStyle: "none", padding: 0 }}>
        {recipes.map((r) => (
          <li key={r.id} style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12, marginBottom: 8 }}>
            <strong>{r.title}</strong> <small>⏱ {r.minutes}m · ⭐ {r.avg_rating ?? "—"}</small>
            <div><small>{r.ingredients.join(", ")}</small></div>
            <button onClick={async () => { await rateRecipe(r.id, 5); refresh(); }}>Rate 5★</button>
            <button onClick={async () => { await deleteRecipe(r.id); refresh(); }} style={{ float: "right" }}>Delete</button>
          </li>
        ))}
      </ul>
    </main>
  );
}
