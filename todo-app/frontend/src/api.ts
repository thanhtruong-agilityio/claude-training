import type { Todo } from "./types";

const BASE = "/api/todos";

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export const listTodos = () => request<Todo[]>(BASE);

export const createTodo = (title: string) =>
  request<Todo>(BASE, { method: "POST", body: JSON.stringify({ title }) });

export const updateTodo = (id: number, patch: Partial<Omit<Todo, "id">>) =>
  request<Todo>(`${BASE}/${id}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });

export const deleteTodo = (id: number) =>
  request<unknown>(`${BASE}/${id}`, { method: "DELETE" });
