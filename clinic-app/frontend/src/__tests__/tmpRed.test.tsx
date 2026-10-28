import { expect, test } from "vitest";

test("deliberate failure for ci proof", () => {
  expect(1).toBe(2);
});
