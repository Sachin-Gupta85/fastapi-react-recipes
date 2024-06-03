import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "./App.jsx";

describe("Recipes App", () => {
  beforeEach(() => vi.restoreAllMocks());
  it("lists a recipe with time and rating", async () => {
    globalThis.fetch = vi.fn(() => Promise.resolve({
      ok: true, status: 200,
      json: async () => [{ id: "1", title: "Omelette", minutes: 8, avg_rating: 4.5, ingredients: ["egg"], tags: [] }],
    }));
    render(<App />);
    await waitFor(() => expect(screen.getByText("Omelette")).toBeInTheDocument());
    expect(screen.getByText(/8m/)).toBeInTheDocument();
  });
});
