document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Helper to show status message
  function showMessage(text, isError = false) {
    messageDiv.textContent = text;
    messageDiv.className = isError ? "error" : "success";
    messageDiv.classList.remove("hidden");
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  // Function to unregister a participant
  async function unregisterParticipant(activityName, email) {
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );
      const result = await response.json();

      if (response.ok) {
        showMessage(result.message || `Unregistered ${email} from ${activityName}`);
        fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred unregistering participant", true);
      }
    } catch (error) {
      showMessage("Failed to unregister participant. Please try again.", true);
      console.error("Error unregistering participant:", error);
    }
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Preserve current selection if dropdown already populated
      const currentSelected = activitySelect.value;
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Build participants list HTML
        let participantsHtml = "";
        if (details.participants && details.participants.length > 0) {
          const participantsListItems = details.participants
            .map(
              (email) =>
                `<li>
                  <span>${email}</span>
                  <button type="button" class="delete-btn" title="Unregister participant" data-activity="${name}" data-email="${email}">🗑️</button>
                </li>`
            )
            .join("");
          participantsHtml = `
            <div class="participants-section">
              <h5>Signed-up Participants (${details.participants.length}):</h5>
              <ul class="participants-list">
                ${participantsListItems}
              </ul>
            </div>
          `;
        } else {
          participantsHtml = `
            <div class="participants-section">
              <h5>Signed-up Participants (0):</h5>
              <p class="no-participants">No participants signed up yet.</p>
            </div>
          `;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHtml}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      if (currentSelected) {
        activitySelect.value = currentSelected;
      }
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle participant deletion using event delegation
  activitiesList.addEventListener("click", async (event) => {
    const deleteButton = event.target.closest(".delete-btn");
    if (!deleteButton) return;

    const activityName = deleteButton.dataset.activity;
    const email = deleteButton.dataset.email;

    if (activityName && email) {
      await unregisterParticipant(activityName, email);
    }
  });

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message);
        signupForm.reset();
        await fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", true);
      }
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
