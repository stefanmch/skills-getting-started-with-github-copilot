// Global references
const activitiesList = document.getElementById("activities-list");
const activitySelect = document.getElementById("activity");
const signupForm = document.getElementById("signup-form");
const messageDiv = document.getElementById("message");

// Function to fetch activities from API
async function fetchActivities() {
  try {
    const response = await fetch("/activities");
    const activities = await response.json();

    // Clear loading message and dropdown
    activitiesList.innerHTML = "";
    activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

    // Populate activities list
    Object.entries(activities).forEach(([name, details]) => {
      const activityCard = document.createElement("div");
      activityCard.className = "activity-card";

      const spotsLeft = details.max_participants - details.participants.length;

      // Participants list HTML
      let participantsHTML = "";
      if (details.participants.length > 0) {
        participantsHTML = `
          <div class="participants-section">
            <strong>Participants:</strong>
            <ul>
              ${details.participants.map(email => `
                <li>
                  ${email}
                  <span class="delete-participant" 
                        data-activity="${name}" 
                        data-email="${email}">✕</span>
                </li>
              `).join("")}
            </ul>
          </div>
        `;
      } else {
        participantsHTML = `
          <div class="participants-section">
            <strong>Participants:</strong>
            <p class="no-participants">No participants yet.</p>
          </div>
        `;
      }

      activityCard.innerHTML = `
        <h4>${name}</h4>
        <p>${details.description}</p>
        <p><strong>Schedule:</strong> ${details.schedule}</p>
        <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        ${participantsHTML}
      `;

      activitiesList.appendChild(activityCard);

      // Add option to select dropdown
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      activitySelect.appendChild(option);
    });
  } catch (error) {
    activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
    console.error("Error fetching activities:", error);
  }
}

// Function to handle participant deletion
async function handleDeleteParticipant(event) {
  if (!event.target.matches('.delete-participant')) return;
  
  const activity = event.target.dataset.activity;
  const email = event.target.dataset.email;
  
  try {
    const response = await fetch(
      `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
      {
        method: "DELETE",
      }
    );

    const result = await response.json();

    if (response.ok) {
      // Refresh activities to show updated participant list
      await fetchActivities();
      messageDiv.textContent = result.message || "Successfully unregistered from activity";
      messageDiv.className = "success";
    } else {
      messageDiv.textContent = result.detail || "Failed to unregister";
      messageDiv.className = "error";
    }

    messageDiv.classList.remove("hidden");

    // Hide message after 5 seconds
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  } catch (error) {
    // Even if JSON parsing failed, the operation might have succeeded
    // Refresh the activities list to be sure
    await fetchActivities();
    messageDiv.textContent = "Action completed, but there was a response error";
    messageDiv.className = "info";
    messageDiv.classList.remove("hidden");
    console.error("Error handling response:", error);
  }
}

// Add event listener for delete buttons using event delegation
activitiesList.addEventListener('click', handleDeleteParticipant);

document.addEventListener("DOMContentLoaded", () => {

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
        // Refresh activities to show updated participant list
        await fetchActivities();
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
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
