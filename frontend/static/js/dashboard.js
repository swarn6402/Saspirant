let userId = null;
let currentPage = 1;
const perPage = 20;
let currentFilters = {};
let cachedAlerts = [];
let trendChart = null;
let categoryChart = null;

// Get user ID from URL
const urlParams = new URLSearchParams(window.location.search);
const userIdFromUrl = urlParams.get("user_id");
console.log("Dashboard page loaded. User ID from URL:", userIdFromUrl);

if (!userIdFromUrl) {
  console.error("No user_id in URL!");
  alert("Error: No user ID provided");
}

function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  const colorClass = type === "success"
    ? "border-emerald-200 bg-emerald-50 text-emerald-700"
    : "border-rose-200 bg-rose-50 text-rose-700";
  toast.className = `pointer-events-auto rounded-xl border px-4 py-3 text-sm shadow ${colorClass}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = "0"; }, 2500);
  setTimeout(() => toast.remove(), 3000);
}

function showError(message) {
  showToast(message, "error");
}

function getUserId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("user_id") || localStorage.getItem("user_id");
}

function apiHeaders() {
  return { "X-User-Id": String(userId) };
}

function setDateTime() {
  const target = document.getElementById("currentDateTime");
  const now = new Date();
  target.textContent = now.toLocaleString(undefined, {
    weekday: "short",
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function showAlertsSkeleton() {
  const list = document.getElementById("alertsList");
  list.innerHTML = Array.from({ length: 4 }).map(() =>
    `<div class="skeleton rounded-xl border border-slate-200 bg-slate-100 p-4"><div class="h-4 w-1/3 rounded bg-slate-200"></div><div class="mt-3 h-3 w-2/3 rounded bg-slate-200"></div><div class="mt-2 h-3 w-1/2 rounded bg-slate-200"></div></div>`
  ).join("");
}

function updateUserProfile(user) {
  if (!user) return;
  document.getElementById("userName").textContent = user.name || "User";
  document.getElementById("userEmail").textContent = user.email || "";
  const initials = (user.name || "U")
    .split(" ")
    .map((x) => x[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  document.getElementById("userAvatar").textContent = initials;
  document.getElementById("prefLink").href = `/templates/preferences.html?user_id=${userId}`;
}

function updateStatsCards(stats, alerts) {
  document.getElementById("totalAlertsStat").textContent = stats.total_alerts_received ?? 0;
  document.getElementById("weekAlertsStat").textContent = `+${stats.alerts_this_week ?? 0} this week`;
  document.getElementById("websitesStat").textContent = stats.monitored_urls ?? 0;

  const upcoming = alerts
    .filter((a) => a.last_date_to_apply)
    .sort((a, b) => new Date(a.last_date_to_apply) - new Date(b.last_date_to_apply))[0];
  if (upcoming) {
    const d = new Date(upcoming.last_date_to_apply);
    document.getElementById("nextDeadlineDate").textContent = d.toLocaleDateString(undefined, { day: "2-digit", month: "long", year: "numeric" });
    document.getElementById("nextDeadlineJob").textContent = upcoming.job_title;
  } else {
    document.getElementById("nextDeadlineDate").textContent = "Not available";
    document.getElementById("nextDeadlineJob").textContent = "No upcoming deadlines";
  }

  const matched = alerts.filter((a) => a.email_status === "sent").length;
  const rate = alerts.length > 0 ? Math.round((matched / alerts.length) * 100) : 0;
  document.getElementById("matchRateStat").textContent = `${rate}%`;
}

function urgencyBadge(lastDate) {
  if (!lastDate) return `<span class="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">No deadline</span>`;
  const days = Math.ceil((new Date(lastDate) - new Date()) / (1000 * 60 * 60 * 24));
  if (days < 3) return `<span class="rounded-full bg-rose-100 px-2 py-1 text-xs font-semibold text-rose-700">${Math.max(days, 0)}d left</span>`;
  if (days <= 7) return `<span class="rounded-full bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-700">${days}d left</span>`;
  return `<span class="rounded-full bg-emerald-100 px-2 py-1 text-xs font-semibold text-emerald-700">${days}d left</span>`;
}

function timeAgo(isoDate) {
  if (!isoDate) return "Unknown";
  const diffMs = Date.now() - new Date(isoDate).getTime();
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  if (hours < 1) return "just now";
  if (hours < 24) return `${hours} hours ago`;
  const days = Math.floor(hours / 24);
  return `${days} days ago`;
}

function displayAlerts(alerts) {
  const list = document.getElementById("alertsList");
  const empty = document.getElementById("alertsEmpty");
  list.innerHTML = "";

  if (!alerts || alerts.length === 0) {
    empty.classList.remove("hidden");
    return;
  }
  empty.classList.add("hidden");

  alerts.forEach((alert) => {
    const detailsId = `details-${alert.id}`;
    const card = document.createElement("article");
    card.className = "rounded-xl border border-slate-200 p-4 transition hover:shadow-sm";
    card.innerHTML = `
      <div class="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 class="text-lg font-semibold">${alert.job_title || "Untitled"}</h3>
          <p class="text-sm text-slate-600">${alert.organization || "Not specified"}</p>
        </div>
        ${urgencyBadge(alert.last_date_to_apply)}
      </div>
      <div class="mt-3 grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
        <p><span class="font-medium">Exam:</span> ${alert.exam_category || "Not specified"}</p>
        <p><span class="font-medium">Last Date:</span> ${alert.last_date_to_apply || "Not specified"}</p>
      </div>
      <p class="mt-2 text-xs text-slate-500">Alerted ${timeAgo(alert.sent_at)}</p>
      <div class="mt-3 flex flex-wrap gap-2">
        <button class="toggle-details rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold" data-target="${detailsId}">View Details</button>
        <a href="${alert.source_url || "#"}" target="_blank" rel="noreferrer" class="rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white">Apply Now</a>
        <button class="archive-btn rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold" data-id="${alert.id}">Archive</button>
        <button class="share-btn rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold" data-title="${encodeURIComponent(alert.job_title || "")}" data-url="${encodeURIComponent(alert.source_url || "")}">Share</button>
      </div>
      <div id="${detailsId}" class="mt-3 hidden rounded-lg bg-slate-50 p-3 text-sm text-slate-700">
        <p class="line-clamp-2">Full details are available in source notification. Open "Apply Now" for complete information.</p>
      </div>
    `;
    list.appendChild(card);
  });

  [...document.querySelectorAll(".toggle-details")].forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = document.getElementById(btn.dataset.target);
      target.classList.toggle("hidden");
      btn.textContent = target.classList.contains("hidden") ? "View Details" : "Hide Details";
    });
  });
  [...document.querySelectorAll(".archive-btn")].forEach((btn) => {
    btn.addEventListener("click", () => archiveAlert(Number(btn.dataset.id)));
  });
  [...document.querySelectorAll(".share-btn")].forEach((btn) => {
    btn.addEventListener("click", async () => {
      const title = decodeURIComponent(btn.dataset.title);
      const url = decodeURIComponent(btn.dataset.url);
      const text = `${title} - ${url}`;
      if (navigator.share) {
        try { await navigator.share({ title, text, url }); } catch {}
      } else {
        await navigator.clipboard.writeText(text);
        showToast("Alert link copied to clipboard.");
      }
    });
  });
}

function setupPagination(total, page, perPageValue) {
  const totalPages = Math.max(1, Math.ceil(total / perPageValue));
  document.getElementById("paginationText").textContent = `Page ${page} of ${totalPages} (${total} total)`;
  document.getElementById("prevPageBtn").disabled = page <= 1;
  document.getElementById("nextPageBtn").disabled = page >= totalPages;
}

async function loadMonitoredUrls() {
  const grid = document.getElementById("websitesGrid");
  grid.innerHTML = `<div class="skeleton h-24 rounded-xl bg-slate-100"></div><div class="skeleton h-24 rounded-xl bg-slate-100"></div>`;
  try {
    const response = await fetch(`${API_BASE_URL}/api/preferences/${userId}/urls`, { headers: apiHeaders() });
    const data = await response.json();
    const urls = data.urls || [];
    if (urls.length === 0) {
      grid.innerHTML = `<div class="rounded-xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">No websites added yet. Go to Preferences to add monitored URLs.</div>`;
      return;
    }
    grid.innerHTML = "";
    urls.forEach((item) => {
      const host = (() => { try { return new URL(item.url).hostname; } catch { return "site"; } })();
      const card = document.createElement("article");
      card.className = "rounded-xl border border-slate-200 p-4";
      card.innerHTML = `
        <div class="flex items-start justify-between gap-2">
          <div>
            <p class="font-semibold">${item.website_name || host}</p>
            <p class="mt-1 truncate text-xs text-slate-500">${item.url}</p>
            <p class="mt-1 text-xs text-slate-500">Last scraped: ${item.last_scraped_at ? timeAgo(item.last_scraped_at) : "Never"}</p>
          </div>
          <span class="h-2.5 w-2.5 rounded-full ${item.is_active ? "bg-emerald-500" : "bg-slate-400"}"></span>
        </div>
        <div class="mt-3 flex flex-wrap gap-2">
          <button id="scrape-btn-${item.id}" class="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white">Test Scrape</button>
          <a href="/templates/preferences.html?user_id=${userId}" class="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold">Edit</a>
          <button class="remove-url rounded-lg border border-rose-300 px-3 py-1.5 text-xs font-semibold text-rose-700" data-id="${item.id}">Remove</button>
        </div>
        <p class="mt-2 text-xs text-slate-500">5 new notifications this week</p>
      `;
      grid.appendChild(card);
    });
    urls.forEach((item) => {
      document
        .getElementById(`scrape-btn-${item.id}`)
        .addEventListener("click", () => triggerManualScrape(item.id, userId));
    });
    [...document.querySelectorAll(".remove-url")].forEach((btn) => {
      btn.addEventListener("click", () => removeMonitoredUrl(Number(btn.dataset.id)));
    });
  } catch {
    grid.innerHTML = `<div class="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">Failed to load monitored websites.</div>`;
  }
}

async function loadActivity() {
  const timeline = document.getElementById("activityTimeline");
  timeline.innerHTML = `<div class="skeleton h-16 rounded-lg bg-slate-100"></div><div class="skeleton h-16 rounded-lg bg-slate-100"></div>`;
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/${userId}/activity`, { headers: apiHeaders() });
    const data = await response.json();
    const items = [];

    (data.emails_sent || []).forEach((row) => {
      items.push({ icon: "🔔", text: `New alert sent: ${row.job_title}`, at: row.sent_at });
    });
    (data.scraping_runs || []).forEach((row) => {
      items.push({ icon: "🕷️", text: `Scraped ${row.url} - ${row.result}`, at: row.scraped_at });
    });
    (data.errors_warnings || []).forEach((row) => {
      items.push({ icon: "⚠️", text: row.message || "Warning", at: row.timestamp });
    });

    items.sort((a, b) => new Date(b.at || 0) - new Date(a.at || 0));
    const top = items.slice(0, 8);
    if (top.length === 0) {
      timeline.innerHTML = `<p class="text-sm text-slate-500">No recent activity yet.</p>`;
      return;
    }
    timeline.innerHTML = "";
    top.forEach((item) => {
      const row = document.createElement("div");
      row.className = "relative";
      row.innerHTML = `
        <span class="absolute -left-[28px] top-1 inline-flex h-5 w-5 items-center justify-center rounded-full bg-blue-100 text-xs">${item.icon}</span>
        <p class="text-sm font-medium">${item.text}</p>
        <p class="text-xs text-slate-500">${timeAgo(item.at)}</p>
      `;
      timeline.appendChild(row);
    });
  } catch {
    timeline.innerHTML = `<p class="text-sm text-rose-600">Failed to load activity.</p>`;
  }
}

function buildCharts(alerts) {
  const byDay = {};
  const byCategory = {};
  alerts.forEach((a) => {
    const d = a.sent_at ? new Date(a.sent_at).toISOString().slice(0, 10) : "Unknown";
    byDay[d] = (byDay[d] || 0) + 1;
    const c = a.exam_category || "Unknown";
    byCategory[c] = (byCategory[c] || 0) + 1;
  });

  const trendCtx = document.getElementById("alertsTrendChart");
  const pieCtx = document.getElementById("categoryPieChart");
  if (trendChart) trendChart.destroy();
  if (categoryChart) categoryChart.destroy();

  trendChart = new Chart(trendCtx, {
    type: "line",
    data: { labels: Object.keys(byDay), datasets: [{ label: "Alerts", data: Object.values(byDay), borderColor: "#2563eb", backgroundColor: "rgba(37,99,235,.2)" }] },
    options: { responsive: true, plugins: { legend: { display: false } } },
  });
  categoryChart = new Chart(pieCtx, {
    type: "doughnut",
    data: { labels: Object.keys(byCategory), datasets: [{ data: Object.values(byCategory), backgroundColor: ["#2563eb", "#7c3aed", "#0d9488", "#ea580c", "#dc2626", "#64748b"] }] },
    options: { responsive: true },
  });
}

function fillCategoryFilter(categories) {
  const filter = document.getElementById("categoryFilter");
  const current = filter.value;
  filter.innerHTML = `<option value="">All categories</option>`;
  categories.forEach((c) => {
    const opt = document.createElement("option");
    opt.value = c;
    opt.textContent = c;
    filter.appendChild(opt);
  });
  filter.value = current;
}

function applyClientSort(alerts) {
  const sort = document.getElementById("sortFilter").value;
  const sorted = [...alerts];
  if (sort === "deadline") {
    sorted.sort((a, b) => new Date(a.last_date_to_apply || "2100-01-01") - new Date(b.last_date_to_apply || "2100-01-01"));
  } else if (sort === "relevance") {
    sorted.sort((a, b) => (b.email_status === "sent") - (a.email_status === "sent"));
  } else {
    sorted.sort((a, b) => new Date(b.sent_at || 0) - new Date(a.sent_at || 0));
  }
  return sorted;
}

async function loadRecentAlerts(id, filters = {}) {
  showAlertsSkeleton();
  const query = new URLSearchParams({
    page: String(currentPage),
    per_page: String(perPage),
    ...filters,
  });
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/${id}/alerts?${query.toString()}`, { headers: apiHeaders() });
    const data = await response.json();
    let alerts = data.alerts || [];
    alerts = applyClientSort(alerts);
    displayAlerts(alerts);
    setupPagination(data.total || 0, data.page || 1, data.per_page || perPage);
    document.getElementById("newAlertBadge").textContent = String(data.total || 0);
    cachedAlerts = alerts;
  } catch {
    showToast("Failed to load alerts.", "error");
  }
}

async function removeMonitoredUrl(urlId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/preferences/${userId}/urls/${urlId}`, {
      method: "DELETE",
      headers: apiHeaders(),
    });
    const data = await response.json();
    if (!response.ok) {
      showToast(data.error || "Failed to remove URL.", "error");
      return;
    }
    showToast("Website removed.");
    loadMonitoredUrls();
  } catch {
    showToast("Failed to remove URL.", "error");
  }
}

async function triggerManualScrape(urlId, currentUserId) {
  console.log(`Triggering manual scrape for URL ID: ${urlId}`);

  const button = document.getElementById(`scrape-btn-${urlId}`);
  if (button) {
    button.disabled = true;
    button.textContent = "Testing...";
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/${currentUserId}/trigger-scrape/${urlId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    console.log("Scrape response status:", response.status);
    const data = await response.json();
    console.log("Scrape result:", data);

    if (response.ok) {
      alert(`Scrape completed! Found ${data.notifications_found} notifications`);
      await loadDashboard(currentUserId);
    } else {
      alert("Scrape failed: " + (data.error || "Unknown error"));
    }
  } catch (error) {
    console.error("Scrape error:", error);
    alert("Scrape failed: " + error.message);
  } finally {
    if (button) {
      button.disabled = false;
      button.textContent = "Test Scrape";
    }
  }
}

async function triggerScrape(id, urlId) {
  const button = document.getElementById(`scrape-btn-${urlId}`);
  button.disabled = true;
  button.textContent = "Scraping...";
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/${id}/trigger-scrape/${urlId}`, {
      method: "POST",
      headers: apiHeaders(),
    });
    const data = await response.json();
    showToast(`Found ${data.notifications_found ?? 0} notifications!`);
    await loadDashboard(id);
  } catch {
    showToast("Scrape failed.", "error");
  } finally {
    button.disabled = false;
    button.textContent = "Scrape Now";
  }
}

async function archiveAlert(alertId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/${userId}/alert/${alertId}`, {
      method: "DELETE",
      headers: apiHeaders(),
    });
    const data = await response.json();
    if (!response.ok) {
      showToast(data.error || "Archive failed.", "error");
      return;
    }
    showToast("Alert archived.");
    loadRecentAlerts(userId, currentFilters);
  } catch {
    showToast("Archive failed.", "error");
  }
}

async function loadDashboard(id) {
  console.log("Loading dashboard for user:", id);

  try {
    console.log("Fetching summary from:", `${API_BASE_URL}/api/dashboard/${id}/summary`);

    const summaryResponse = await fetch(`${API_BASE_URL}/api/dashboard/${id}/summary`, {
      headers: apiHeaders(),
    });
    console.log("Summary response status:", summaryResponse.status);

    if (!summaryResponse.ok) {
      const errorText = await summaryResponse.text();
      console.error("Summary fetch failed:", errorText);
      throw new Error(`Failed to load summary: ${summaryResponse.status}`);
    }
    const summary = await summaryResponse.json();
    console.log("Summary data received:", summary);

    updateUserProfile(summary.user);
    updateStatsCards(summary.stats || {}, summary.recent_alerts || []);
    fillCategoryFilter(summary.stats?.active_preferences || []);
    buildCharts(summary.recent_alerts || []);

    await Promise.all([
      loadRecentAlerts(id, currentFilters),
      loadMonitoredUrls(),
      loadActivity(),
    ]);
  } catch (error) {
    console.error("Dashboard load error:", error);
    console.error("Error details:", error.message);
    showError("Dashboard load failed: " + error.message);
  }
}

function setupFilters() {
  const searchInput = document.getElementById("searchInput");
  const categoryFilter = document.getElementById("categoryFilter");
  const sortFilter = document.getElementById("sortFilter");

  const apply = () => {
    currentPage = 1;
    const category = categoryFilter.value;
    const search = searchInput.value.trim().toLowerCase();
    currentFilters = {};
    if (category) currentFilters.exam_category = category;

    loadRecentAlerts(userId, currentFilters).then(() => {
      if (!search) return;
      const filtered = cachedAlerts.filter((a) => (a.job_title || "").toLowerCase().includes(search));
      displayAlerts(filtered);
      document.getElementById("paginationText").textContent = `Filtered: ${filtered.length} results`;
    });
  };

  searchInput.addEventListener("input", apply);
  categoryFilter.addEventListener("change", apply);
  sortFilter.addEventListener("change", () => {
    displayAlerts(applyClientSort(cachedAlerts));
  });
}

function setupPaginationHandlers() {
  document.getElementById("prevPageBtn").addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage -= 1;
      loadRecentAlerts(userId, currentFilters);
    }
  });
  document.getElementById("nextPageBtn").addEventListener("click", () => {
    currentPage += 1;
    loadRecentAlerts(userId, currentFilters);
  });
}

function setupKeyboardShortcuts() {
  document.addEventListener("keydown", (event) => {
    if (event.target && ["INPUT", "TEXTAREA", "SELECT"].includes(event.target.tagName)) return;
    const key = event.key.toLowerCase();
    if (key === "r") {
      loadDashboard(userId);
      showToast("Dashboard refreshed.");
    }
    if (key === "n") {
      window.scrollTo({ top: document.getElementById("alertsSection").offsetTop - 20, behavior: "smooth" });
    }
  });
}

function init() {
  userId = getUserId();
  if (!userId) {
    showToast("Missing user ID. Please login again.", "error");
    return;
  }
  localStorage.setItem("user_id", String(userId));
  setDateTime();
  setInterval(setDateTime, 60000);

  setupFilters();
  setupPaginationHandlers();
  setupKeyboardShortcuts();

  loadDashboard(userId);
  setInterval(() => {
    loadDashboard(userId);
  }, 5 * 60 * 1000);
}

init();

