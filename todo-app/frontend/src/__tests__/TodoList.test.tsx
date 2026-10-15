import { fireEvent, render, screen } from "@testing-library/react";
import TodoList from "../components/TodoList";

const todos = [
  { id: 1, title: "buy milk", done: false },
  { id: 2, title: "write notes", done: true },
];

test("shows empty state", () => {
  render(<TodoList todos={[]} onToggle={() => {}} onDelete={() => {}} />);
  expect(screen.getByText("No todos yet.")).toBeInTheDocument();
});

test("renders todos and fires callbacks", () => {
  const onToggle = vi.fn();
  const onDelete = vi.fn();
  render(<TodoList todos={todos} onToggle={onToggle} onDelete={onDelete} />);

  fireEvent.click(screen.getByLabelText("buy milk"));
  expect(onToggle).toHaveBeenCalledWith(todos[0]);

  fireEvent.click(screen.getAllByText("Delete")[1]);
  expect(onDelete).toHaveBeenCalledWith(2);
});
