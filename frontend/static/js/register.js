const form = document.getElementById("registrationForm");
const nameInput = document.getElementById("name");
const emailInput = document.getElementById("email");
const dobInput = document.getElementById("dob");
const qualificationInput = document.getElementById("qualification");
const submitBtn = document.getElementById("submitBtn");
const submitSpinner = document.getElementById("submitSpinner");
const submitText = document.getElementById("submitText");
const inlineSuccess = document.getElementById("inlineSuccess");

const errorEls = {
  name: document.getElementById("nameError"),
  email: document.getElementById("emailError"),
  dob: document.getElementById("dobError"),
  qualification: document.getElementById("qualificationError"),
};

function showFieldError(field, message) {
  if (errorEls[field]) {
    errorEls[field].textContent = message || "";
  }
}

function showToast(message, type = "error") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  const colorClass = type === "success"
    ? "border-emerald-200 bg-emerald-50 text-emerald-700"
    : "border-red-200 bg-red-50 text-red-700";

  toast.className = `fade-in pointer-events-auto rounded-xl border px-4 py-3 text-sm shadow ${colorClass}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(-6px)";
  }, 2400);
  setTimeout(() => toast.remove(), 2800);
}

function showError(message) {
  showToast(message, "error");
}

function isValidEmail(value) {
  const emailPattern = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
  return emailPattern.test(value);
}

function calculateAge(dobString) {
  const dob = new Date(dobString);
  if (Number.isNaN(dob.getTime())) return null;

  const today = new Date();
  let age = today.getFullYear() - dob.getFullYear();
  const monthDiff = today.getMonth() - dob.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
    age -= 1;
  }
  return age;
}

function validateForm() {
  let valid = true;

  const name = nameInput.value.trim();
  const email = emailInput.value.trim();
  const dob = dobInput.value;
  const qualification = qualificationInput.value;

  if (!name) {
    showFieldError("name", "Full Name is required");
    valid = false;
  } else {
    showFieldError("name", "");
  }

  if (!email) {
    showFieldError("email", "Email is required");
    valid = false;
  } else if (!isValidEmail(email)) {
    showFieldError("email", "Please enter a valid email address");
    valid = false;
  } else {
    showFieldError("email", "");
  }

  if (!dob) {
    showFieldError("dob", "Date of Birth is required");
    valid = false;
  } else {
    const age = calculateAge(dob);
    if (age === null) {
      showFieldError("dob", "Please enter a valid date");
      valid = false;
    } else if (age < 15) {
      showFieldError("dob", "You must be at least 15 years old");
      valid = false;
    } else {
      showFieldError("dob", "");
    }
  }

  if (!qualification) {
    showFieldError("qualification", "Please select a qualification");
    valid = false;
  } else {
    showFieldError("qualification", "");
  }

  submitBtn.disabled = !valid;
  return valid;
}

function setSubmitting(isSubmitting) {
  submitBtn.disabled = isSubmitting || !validateForm();
  submitSpinner.classList.toggle("hidden", !isSubmitting);
  submitText.textContent = isSubmitting ? "Creating Account..." : "Create Account";
}

async function handleRegistration(event) {
  event.preventDefault();

  if (!validateForm()) {
    showToast("Please fix the highlighted errors.");
    return;
  }

  const formData = {
    name: nameInput.value.trim(),
    email: emailInput.value.trim(),
    date_of_birth: dobInput.value,
    highest_qualification: qualificationInput.value,
  };

  setSubmitting(true);
  try {
    console.log("Attempting registration with data:", formData);
    console.log("Sending to:", `${API_BASE_URL}/api/auth/register`);

    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });

    let data = null;
    try {
      data = await response.json();
    } catch (parseError) {
      console.error("Failed to parse JSON response:", parseError);
      data = { error: "Invalid server response format" };
    }

    console.log("Registration response status:", response.status);
    console.log("Registration response body:", data);

    if (response.ok) {
      localStorage.setItem("user_id", data.user_id);
      inlineSuccess.classList.remove("hidden");
      inlineSuccess.textContent = "Account created successfully. Redirecting to preferences...";
      showToast("Registration successful.", "success");
      setTimeout(() => {
        window.location.href = `/templates/preferences.html?user_id=${data.user_id}`;
      }, 1200);
    } else {
      console.error("Server error response:", data);
      showError(data.error || "Registration failed");
    }
  } catch (error) {
    console.error("Registration error:", error);
    console.error("Error details:", error.message);
    showError("Registration failed. Please try again. Error: " + error.message);
  } finally {
    setSubmitting(false);
  }
}

form.addEventListener("submit", handleRegistration);
[nameInput, emailInput, dobInput, qualificationInput].forEach((el) => {
  el.addEventListener("input", validateForm);
  el.addEventListener("change", validateForm);
});

validateForm();
