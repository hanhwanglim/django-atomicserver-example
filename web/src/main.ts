const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const apiBase = `${API_URL}/tasks/`;

interface Task {
  id: number;
  title: string;
  completed: boolean;
}

// --- DOM Elements ---
const taskForm = document.getElementById("task-form") as HTMLFormElement | null;
const taskInput = document.getElementById("task-input") as HTMLInputElement | null;
const taskList = document.getElementById("task-list") as HTMLUListElement | null;

// --- Core Functions ---

/**
 * Fetches tasks from the API and renders them.
 */
async function fetchAndRenderTasks() {
  if (!taskList) {
    console.error("Task list element not found.");
    return;
  }
  try {
    const response = await fetch(apiBase);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const tasks: Task[] = await response.json();
    renderTasks(tasks);
  } catch (error) {
    console.error("Failed to fetch tasks:", error);
    taskList.innerHTML = "<li>Error loading tasks. Please try again later.</li>";
  }
}

/**
 * Renders a list of tasks in the task list element.
 * @param tasks - Array of Task objects to render.
 */
function renderTasks(tasks: Task[]) {
  if (!taskList) return; // Should have been caught earlier, but good practice
  taskList.innerHTML = ""; // Clear existing tasks
  tasks.forEach((task) => {
    const taskElement = createTaskElement(task);
    taskList.appendChild(taskElement);
  });
}

/**
 * Creates an LI element for a single task.
 * @param task - The task object.
 * @returns The HTMLLIElement for the task.
 */
function createTaskElement(task: Task): HTMLLIElement {
  const li = document.createElement("li");
  li.textContent = task.title;
  li.dataset.taskId = task.id.toString(); // Store ID for potential future use (e.g., delete)
  if (task.completed) {
    li.style.textDecoration = "line-through";
    li.classList.add("completed"); // Add class for styling
  }
  li.addEventListener("click", () => handleToggleTask(task));
  // Add delete button
  const deleteButton = document.createElement("button");
  deleteButton.textContent = "Delete";
  deleteButton.classList.add("delete-button"); // Add class for styling
  deleteButton.addEventListener("click", (event) => {
    event.stopPropagation(); // Prevent toggle when clicking delete
    handleDeleteTask(task.id);
  });
  li.appendChild(deleteButton);


  return li;
}


/**
 * Handles the submission of the new task form.
 * @param event - The form submission event.
 */
async function handleAddTaskSubmit(event: Event) {
  event.preventDefault();
  if (!taskInput || !taskInput.value.trim()) {
    console.warn("Task input is empty or not found.");
    return; // Don't add empty tasks
  }

  const taskTitle = taskInput.value.trim();

  try {
    const response = await fetch(apiBase, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: taskTitle }),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    taskInput.value = ""; // Clear input field
    // Instead of fetching all tasks, we could potentially add the new task directly
    // to the UI for optimistic update, then confirm with fetchAndRenderTasks if needed.
    await fetchAndRenderTasks(); // Refresh list after adding
  } catch (error) {
    console.error("Failed to add task:", error);
    alert("Failed to add task. Please try again.");
  }
}

/**
 * Handles toggling the completion status of a task.
 * @param task - The task object to toggle.
 */
async function handleToggleTask(task: Task) {
  try {
    const response = await fetch(`${apiBase}${task.id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed: !task.completed }),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    // Instead of fetching all, we could find the specific LI and update its style/class.
    await fetchAndRenderTasks(); // Refresh list after toggling
  } catch (error) {
    console.error("Failed to toggle task:", error);
    alert("Failed to update task status. Please try again.");
  }
}


async function handleDeleteTask(taskId: number) {
  // Confirmation dialog
  if (!confirm("Are you sure you want to delete this task?")) {
    return;
  }

  try {
    const response = await fetch(`${apiBase}${taskId}/`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      // Handle specific errors if the API provides details
      if (response.status === 404) {
        throw new Error(`Task with ID ${taskId} not found.`);
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Option 1: Optimistic UI update (remove element immediately)
    const taskElement = taskList?.querySelector(`li[data-task-id="${taskId}"]`);
    taskElement?.remove();

    // Option 2: Refetch the entire list (simpler, but less performant)
    // await fetchAndRenderTasks();

    console.log(`Task ${taskId} deleted successfully.`);

  } catch (error) {
    console.error(`Failed to delete task ${taskId}:`, error);
    alert(`Failed to delete task. ${error instanceof Error ? error.message : 'Please try again.'}`);
    // Optional: If optimistic update failed, refetch to ensure consistency
    // await fetchAndRenderTasks();
  }
}


// --- Initialization ---

// Check required elements and attach event listeners
if (taskForm && taskInput && taskList) {
  taskForm.addEventListener("submit", handleAddTaskSubmit);
  // Initial fetch of tasks when the page loads
  fetchAndRenderTasks();
} else {
  console.error("Required DOM elements (form, input, or list) not found. App initialization failed.");
  // Optionally, display a user-friendly message in the UI
  const body = document.querySelector('body');
  if (body) {
    const errorMsg = document.createElement('p');
    errorMsg.textContent = "Error: Could not initialize the task application. Essential elements are missing.";
    errorMsg.style.color = 'red';
    body.prepend(errorMsg);
  }
}
