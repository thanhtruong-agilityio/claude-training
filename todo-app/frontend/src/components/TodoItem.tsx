import type { Todo } from "../types";

interface Props {
  todo: Todo;
  onToggle: (todo: Todo) => void;
  onDelete: (id: number) => void;
}

export default function TodoItem({ todo, onToggle, onDelete }: Props) {
  return (
    <li>
      <label>
        <input
          type="checkbox"
          checked={todo.done}
          onChange={() => onToggle(todo)}
        />
        <span style={{ textDecoration: todo.done ? "line-through" : "none" }}>
          {todo.title}
        </span>
      </label>
      <button onClick={() => onDelete(todo.id)}>Delete</button>
    </li>
  );
}
