const BASE = import.meta.env?.VITE_API_URL || "";
async function req(path, opts) {
  const res = await fetch(`${BASE}/api${path}`, {
    headers: { "Content-Type": "application/json" }, ...opts });
  if (!res.ok) throw new Error(`${res.status}`);
  return res.status === 204 ? null : res.json();
}
export const listRecipes = (q = "", ingredient = "", maxMinutes = "") => {
  const p = new URLSearchParams();
  if (q) p.set("q", q);
  if (ingredient) p.set("ingredient", ingredient);
  if (maxMinutes) p.set("max_minutes", maxMinutes);
  const qs = p.toString();
  return req(`/recipes${qs ? `?${qs}` : ""}`);
};
export const createRecipe = (r) => req("/recipes", { method: "POST", body: JSON.stringify(r) });
export const rateRecipe = (id, rating) => req(`/recipes/${id}/rate`, { method: "POST", body: JSON.stringify({ rating }) });
export const deleteRecipe = (id) => req(`/recipes/${id}`, { method: "DELETE" });
