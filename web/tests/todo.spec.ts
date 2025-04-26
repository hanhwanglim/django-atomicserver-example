import { expect, test, Page } from "@playwright/test";

const API_URL = process.env.API_URL || "http://localhost:8000";

/**
 * Helper function to add a new task to the list via the UI.
 * @param page The Playwright Page object.
 * @param taskName The name of the task to add.
 */
async function addTask(page: Page, taskName: string) {
  const taskInput = page.locator("#task-input");
  const taskForm = page.locator("#task-form");
  await taskInput.fill(taskName);
  await taskForm.press("Enter");
}

/**
 * Test suite for the To-Do List Application.
 * Covers adding tasks, toggling completion, and handling multiple tasks,
 * using atomic database contexts for test isolation.
 */
test.describe("To-Do List App", () => {
  test.beforeEach(async ({ page }) => {
    // Begin an atomic context
    await page.request.get(`${API_URL}/atomic/begin/`);
    await page.goto("/");
  });

  test.afterEach(async ({ page }) => {
    // Rollback the atomic context
    // Notice that this resets the count of the task items despite us creating many tasks
    await page.request.get(`${API_URL}/atomic/rollback/`);
  });

  test("should add a new task", async ({ page }) => {
    const taskList = page.locator("#task-list");

    await addTask(page, "Buy groceries");

    await expect(taskList).toContainText("Buy groceries");

    const tasks = await page.locator("#task-list li").count();
    expect(tasks).toBe(1);
  });

  test("should toggle task completion", async ({ page }) => {
    const taskList = page.locator("#task-list");

    await addTask(page, "Complete homework");

    const taskItem = taskList.locator("text=Complete homework");
    await expect(taskItem).toBeVisible();

    await taskItem.click();
    await expect(taskItem).toHaveCSS(
      "text-decoration",
      "line-through solid rgb(0, 0, 0)",
    );

    const tasks = await page.locator("#task-list li").count();
    expect(tasks).toBe(1);
  });

  test("should handle multiple tasks", async ({ page }) => {
    const taskList = page.locator("#task-list");

    await addTask(page, "Task 1");
    await addTask(page, "Task 2");
    await addTask(page, "Task 3");

    await expect(taskList).toContainText("Task 1");
    await expect(taskList).toContainText("Task 2");
    await expect(taskList).toContainText("Task 3");

    const task1 = taskList.locator("text=Task 1");
    await task1.click();
    await expect(task1).toHaveCSS(
      "text-decoration",
      "line-through solid rgb(0, 0, 0)",
    );

    const tasks = await page.locator("#task-list li").count();
    expect(tasks).toBe(3);
  });
});
