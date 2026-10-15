import { useEffect, useState } from "react";
import * as api from "./api";
import TodoForm from "./components/TodoForm";
import TodoList from "./components/TodoList";
import type { Todo } from "./types";

export default function App() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listTodos().then(setTodos).catch((e: Error) => setError(e.message));
  }, []);

  const add = async (title: string) => {
    const todo = await api.createTodo(title);
    setTodos((prev) => [...prev, todo]);
  };

  const toggle = async (todo: Todo) => {
    const updated = await api.updateTodo(todo.id, { done: !todo.done });
    setTodos((prev) => prev.map((t) => (t.id === todo.id ? updated : t)));
  };

  const remove = async (id: number) => {
    await api.deleteTodo(id);
    setTodos((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <main>
      <h1>Todos</h1>
      {error && <p role="alert">{error}</p>}
      <TodoForm onAdd={add} />
      <TodoList todos={todos} onToggle={toggle} onDelete={remove} />
    </main>
  );
}
