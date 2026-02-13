const EXAM_CATEGORIES = [
  { key: "UPSC", label: "UPSC", desc: "Civil Services" },
  { key: "SSC", label: "SSC", desc: "Staff Selection Commission" },
  { key: "Banking", label: "Banking", desc: "IBPS, SBI, RBI" },
  { key: "Railways", label: "Railways", desc: "RRB NTPC, Group D, etc." },
  { key: "State PSCs", label: "State PSCs", desc: "All states" },
  { key: "University", label: "University Exams", desc: "Semester exams, admissions, results" },
  { key: "Defence", label: "Defence", desc: "NDA, CDS, AFCAT" },
  { key: "Teaching", label: "Teaching", desc: "CTET, State TETs, UGC NET" },
  { key: "Engineering", label: "Engineering", desc: "GATE, ESE" },
  { key: "Medical", label: "Medical", desc: "NEET PG, AIIMS" },
  { key: "Law", label: "Law", desc: "CLAT, Judicial Services" },
  { key: "Police", label: "Police", desc: "UPSC, State Police Recruitment" },
  { key: "Others", label: "Others", desc: "Custom" },
];

const LOCATION_OPTIONS = [
  "All India", "Delhi", "Maharashtra", "Karnataka", "Tamil Nadu", "Uttar Pradesh",
  "Madhya Pradesh", "Rajasthan", "Bihar", "West Bengal", "Gujarat", "Punjab", "Haryana",
  "Kerala", "Telangana", "Andhra Pradesh", "Odisha", "Assam", "Uttarakhand", "Jharkhand",
];

const SUGGESTED_URLS = {
  "UPSC": [{ name: "UPSC Official", url: "https://upsc.gov.in/examinations/active" }],
  "SSC": [{ name: "SSC Official", url: "https://ssc.gov.in/" }],
  "Banking": [{ name: "IBPS", url: "https://www.ibps.in/" }, { name: "SBI Careers", url: "https://sbi.co.in/web/careers" }],
  "Railways": [{ name: "Railway Recruitment", url: "https://www.rrbcdg.gov.in/" }],
  "State PSCs": [{ name: "MPPSC", url: "https://www.mppsc.mp.gov.in/" }, { name: "UPPSC", url: "https://uppsc.up.nic.in/" }],
  "University": [{ name: "MAKAUT Exam", url: "https://www.makautexam.net/" }, { name: "Delhi University Notices", url: "https://du.ac.in/index.php?page=notices" }],
  "Defence": [{ name: "Indian Army", url: "https://joinindianarmy.nic.in/" }],
  "Teaching": [{ name: "UGC NET", url: "https://ugcnet.nta.ac.in/" }],
  "Engineering": [{ name: "GATE", url: "https://gate2026.iitr.ac.in/" }],
  "Medical": [{ name: "NTA NEET", url: "https://neet.nta.nic.in/" }],
  "Law": [{ name: "CLAT", url: "https://consortiumofnlus.ac.in/" }],
  "Police": [{ name: "Police Recruitment", url: "https://www.ncs.gov.in/" }],
};

let userId = null;
let selectedCategories = new Set();
let selectedLocations = new Set();
let monitoredUrls = [];

const examContainer = document.getElementById("examCategories");
const locationsSelect = document.getElementById("locationsSelect");
const locationChips = document.getElementById("locationChips");
const suggestedUrlsContainer = document.getElementById("suggestedUrls");
const urlCards = document.getElementById("urlCards");
const saveBtn = document.getElementById("savePreferencesBtn");
const saveSpinner = document.getElementById("saveSpinner");
const saveBtnText = document.getElementById("saveBtnText");
const saveMessage = document.getElementById("saveMessage");
const draftStatus = document.getElementById("draftStatus");

function showToast(message, type = "error") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  const colorClass = type === "success"
    ? "border-emerald-200 bg-emerald-50 text-emerald-700"
    : "border-red-200 bg-red-50 text-red-700";
  toast.className = `fade-in pointer-events-auto rounded-xl border px-4 py-3 text-sm shadow ${colorClass}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = "0"; }, 2600);
  setTimeout(() => toast.remove(), 3000);
}

function getUserId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("user_id") || localStorage.getItem("user_id");
}

function createExamCards() {
  examContainer.innerHTML = "";
  EXAM_CATEGORIES.forEach((item) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "exam-card rounded-2xl border border-slate-300 bg-white p-4 text-left transition hover:border-blue-300";
    card.dataset.value = item.key;
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <p class="font-semibold">${item.label}</p>
        <span class="hidden rounded-full bg-blue-600 px-2 py-0.5 text-xs font-semibold text-white">Selected</span>
      </div>
      <p class="mt-1 text-xs text-slate-500">${item.desc}</p>
    `;
    card.addEventListener("click", () => {
      if (selectedCategories.has(item.key)) {
        selectedCategories.delete(item.key);
      } else {
        selectedCategories.add(item.key);
      }
      refreshCategoryUI();
      refreshSuggestedUrls();
    });
    examContainer.appendChild(card);
  });
}

function refreshCategoryUI() {
  [...examContainer.querySelectorAll(".exam-card")].forEach((card) => {
    const selected = selectedCategories.has(card.dataset.value);
    card.classList.toggle("selected", selected);
    const badge = card.querySelector("span");
    badge.classList.toggle("hidden", !selected);
  });
}

function initLocationOptions() {
  LOCATION_OPTIONS.forEach((loc) => {
    const option = document.createElement("option");
    option.value = loc;
    option.textContent = loc;
    locationsSelect.appendChild(option);
  });
}

function renderLocationChips() {
  locationChips.innerHTML = "";
  [...selectedLocations].forEach((location) => {
    const chip = document.createElement("span");
    chip.className = "inline-flex items-center gap-2 rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700";
    chip.innerHTML = `${location}<button type="button" class="font-bold" data-location="${location}">x</button>`;
    locationChips.appendChild(chip);
  });
  locationChips.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", () => {
      selectedLocations.delete(btn.dataset.location);
      renderLocationChips();
    });
  });
}

function refreshSuggestedUrls() {
  suggestedUrlsContainer.innerHTML = "";
  const suggestions = [];
  [...selectedCategories].forEach((category) => {
    (SUGGESTED_URLS[category] || []).forEach((entry) => suggestions.push(entry));
  });
  const unique = new Map();
  suggestions.forEach((x) => unique.set(x.url, x));

  if (unique.size === 0) {
    suggestedUrlsContainer.innerHTML = `<span class="text-xs text-slate-500">Select exam categories to get URL suggestions.</span>`;
    return;
  }

  [...unique.values()].forEach((item) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 transition hover:bg-blue-100";
    btn.textContent = `+ ${item.name}`;
    btn.addEventListener("click", () => {
      if (monitoredUrls.some((x) => x.url === item.url)) {
        showToast("URL already added.");
        return;
      }
      document.getElementById("url_input").value = item.url;
      document.getElementById("website_name").value = item.name;
      addUrl();
    });
    suggestedUrlsContainer.appendChild(btn);
  });
}

function validateForm() {
  let ok = true;
  document.getElementById("categoryError").textContent = "";
  document.getElementById("ageError").textContent = "";
  document.getElementById("urlError").textContent = "";

  if (selectedCategories.size < 1) {
    document.getElementById("categoryError").textContent = "Select at least one exam category.";
    ok = false;
  }

  const minAge = document.getElementById("min_age").value;
  const maxAge = document.getElementById("max_age").value;
  if (minAge && maxAge && Number(minAge) > Number(maxAge)) {
    document.getElementById("ageError").textContent = "Minimum age cannot be greater than maximum age.";
    ok = false;
  }

  if (monitoredUrls.length < 1) {
    document.getElementById("urlError").textContent = "Add at least one monitored URL.";
    ok = false;
  }

  return ok;
}

async function loadUserInfo() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/user/${userId}`);
    if (!response.ok) return;
    const data = await response.json();
    const name = data.name || "Aspirant";
    document.getElementById("welcomeText").textContent = `Welcome, ${name}!`;
  } catch (e) {
    // no-op for MVP
  }
}

async function loadPreferences(id) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/preferences/${id}`);
    if (!response.ok) return;
    const data = await response.json();
    selectExamCategories(data.exam_categories || []);
    setAgeRange(data.min_age, data.max_age);
    setLocations(data.preferred_locations || []);
  } catch (error) {
    showToast("Could not load preferences.");
  }
}

async function loadMonitoredUrls(id) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/preferences/${id}/urls`);
    if (!response.ok) return;
    const data = await response.json();
    monitoredUrls = (data.urls || []).map((x) => ({
      id: x.id,
      url: x.url,
      website_name: x.website_name || autoNameFromUrl(x.url),
      scraper_type: x.scraper_type || "html",
      last_scraped_at: x.last_scraped_at || null,
      is_active: x.is_active !== false,
    }));
    renderUrlCards();
  } catch (error) {
    showToast("Could not load monitored URLs.");
  }
}

function selectExamCategories(categories) {
  selectedCategories = new Set(categories);
  refreshCategoryUI();
  refreshSuggestedUrls();
}

function setAgeRange(minAge, maxAge) {
  document.getElementById("min_age").value = minAge ?? "";
  document.getElementById("max_age").value = maxAge ?? "";
}

function setLocations(locations) {
  selectedLocations = new Set(locations || []);
  renderLocationChips();
}

function autoNameFromUrl(url) {
  try {
    const parsed = new URL(url);
    return parsed.hostname.replace("www.", "");
  } catch {
    return "Custom Site";
  }
}

async function addUrl() {
  const urlInput = document.getElementById("url_input");
  const websiteInput = document.getElementById("website_name");
  const url = urlInput.value.trim();
  const websiteName = websiteInput.value.trim() || autoNameFromUrl(url);

  if (!url) {
    showToast("Enter a URL first.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/preferences/${userId}/urls`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: url,
        website_name: websiteName,
        scraper_type: "html",
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      showToast(data.error || "Failed to add URL.");
      return;
    }

    monitoredUrls.push({
      id: data.monitored_url.id,
      url: data.monitored_url.url,
      website_name: data.monitored_url.website_name || websiteName,
      scraper_type: data.monitored_url.scraper_type || "html",
      last_scraped_at: data.monitored_url.last_scraped_at || null,
      is_active: data.monitored_url.is_active !== false,
    });
    renderUrlCards();
    urlInput.value = "";
    websiteInput.value = "";
    showToast("URL added.", "success");
  } catch (error) {
    showToast("Failed to add URL.");
  }
}

async function removeUrl(urlId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/preferences/${userId}/urls/${urlId}`, { method: "DELETE" });
    const data = await response.json();
    if (!response.ok) {
      showToast(data.error || "Failed to remove URL.");
      return;
    }
    monitoredUrls = monitoredUrls.filter((x) => x.id !== urlId);
    renderUrlCards();
    showToast("URL removed.", "success");
  } catch (error) {
    showToast("Failed to remove URL.");
  }
}

async function testScrape(urlId) {
  showToast("Testing scrape...", "success");
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/${userId}/trigger-scrape/${urlId}`, {
      method: "POST",
      headers: { "X-User-Id": String(userId) },
    });
    const data = await response.json();
    if (!response.ok) {
      showToast(data.error || "Test scrape failed.");
      return;
    }
    showToast(`Found ${data.notifications_found} notifications!`, "success");
  } catch (error) {
    showToast("Test scrape failed.");
  }
}

function renderUrlCards() {
  urlCards.innerHTML = "";
  monitoredUrls.forEach((item) => {
    const card = document.createElement("article");
    card.className = "fade-in rounded-2xl border border-slate-200 bg-white p-4";
    card.innerHTML = `
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p class="font-semibold">${item.website_name || "Not specified"}</p>
          <p class="mt-1 break-all text-sm text-slate-600">${item.url}</p>
        </div>
        <div class="flex gap-2">
          <button type="button" class="test-btn rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-emerald-700" data-id="${item.id}">Test Scrape</button>
          <button type="button" class="remove-btn rounded-lg bg-rose-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-rose-700" data-id="${item.id}">Remove</button>
        </div>
      </div>
    `;
    urlCards.appendChild(card);
  });

  [...urlCards.querySelectorAll(".remove-btn")].forEach((btn) => {
    btn.addEventListener("click", () => removeUrl(Number(btn.dataset.id)));
  });
  [...urlCards.querySelectorAll(".test-btn")].forEach((btn) => {
    btn.addEventListener("click", () => testScrape(Number(btn.dataset.id)));
  });
}

function getSelectedCategories() {
  return [...selectedCategories];
}

function getSelectedLocations() {
  return [...selectedLocations];
}

async function savePreferences(id) {
  if (!validateForm()) return;
  setSaving(true);

  const minAge = document.getElementById("min_age").value;
  const maxAge = document.getElementById("max_age").value;
  const formData = {
    exam_categories: getSelectedCategories(),
    min_age: minAge === "" ? null : Number(minAge),
    max_age: maxAge === "" ? null : Number(maxAge),
    preferred_locations: getSelectedLocations(),
  };

  try {
    const response = await fetch(`${API_BASE_URL}/api/preferences/${id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    const data = await response.json();
    if (!response.ok) {
      showToast(data.error || "Failed to save preferences.");
      return;
    }

    saveMessage.textContent = "Preferences saved!";
    saveMessage.classList.remove("text-rose-600");
    saveMessage.classList.add("text-emerald-600");
    localStorage.removeItem(`preferences_draft_${id}`);
    setTimeout(() => {
      window.location.href = `/templates/dashboard.html?user_id=${id}`;
    }, 1500);
  } catch (error) {
    showToast("Failed to save preferences.");
  } finally {
    setSaving(false);
  }
}

function setSaving(isSaving) {
  saveBtn.disabled = isSaving;
  saveSpinner.classList.toggle("hidden", !isSaving);
  saveBtnText.textContent = isSaving ? "Saving..." : "Save Preferences";
}

function createDraftPayload() {
  return {
    exam_categories: getSelectedCategories(),
    min_age: document.getElementById("min_age").value || null,
    max_age: document.getElementById("max_age").value || null,
    preferred_locations: getSelectedLocations(),
  };
}

function restoreDraftIfAny(id) {
  const raw = localStorage.getItem(`preferences_draft_${id}`);
  if (!raw) return;
  try {
    const draft = JSON.parse(raw);
    if (Array.isArray(draft.exam_categories)) selectExamCategories(draft.exam_categories);
    setAgeRange(draft.min_age, draft.max_age);
    if (Array.isArray(draft.preferred_locations)) setLocations(draft.preferred_locations);
    draftStatus.textContent = "Draft restored from local autosave.";
  } catch {
    // ignore
  }
}

function setupAutosave() {
  setInterval(() => {
    if (!userId) return;
    const payload = createDraftPayload();
    localStorage.setItem(`preferences_draft_${userId}`, JSON.stringify(payload));
    draftStatus.textContent = `Draft saved at ${new Date().toLocaleTimeString()}`;
  }, 30000);
}

function setupHandlers() {
  document.getElementById("addLocationBtn").addEventListener("click", () => {
    const value = locationsSelect.value;
    if (!value) return;
    selectedLocations.add(value);
    renderLocationChips();
    locationsSelect.value = "";
  });

  document.getElementById("skipOptionalBtn").addEventListener("click", () => {
    setAgeRange("", "");
    selectedLocations.clear();
    renderLocationChips();
    showToast("Optional fields skipped.", "success");
  });

  document.getElementById("addUrlBtn").addEventListener("click", addUrl);
  saveBtn.addEventListener("click", () => savePreferences(userId));

  document.getElementById("toggleOptionalBtn").addEventListener("click", () => {
    const optional = document.getElementById("optionalSection");
    const btn = document.getElementById("toggleOptionalBtn");
    const hidden = optional.classList.toggle("hidden");
    btn.textContent = hidden ? "Expand" : "Collapse";
  });

  ["min_age", "max_age"].forEach((id) => {
    document.getElementById(id).addEventListener("input", validateForm);
  });
}

function setupOnboardingTip() {
  const tip = document.getElementById("onboardingTip");
  const key = "preferences_onboarding_seen";
  if (localStorage.getItem(key) === "1") {
    tip.classList.add("hidden");
    return;
  }
  tip.addEventListener("click", () => {
    tip.classList.add("hidden");
    localStorage.setItem(key, "1");
  });
}

async function init() {
  userId = getUserId();
  if (!userId) {
    showToast("User ID is missing. Please register or login first.");
    return;
  }
  localStorage.setItem("user_id", String(userId));

  createExamCards();
  initLocationOptions();
  setupHandlers();
  setupOnboardingTip();
  setupAutosave();
  await loadUserInfo();
  await loadPreferences(userId);
  await loadMonitoredUrls(userId);
  restoreDraftIfAny(userId);
  refreshSuggestedUrls();
  validateForm();
}

init();

