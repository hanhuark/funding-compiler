const fundingGrid = document.querySelector("#funding-grid");
const facultyGrid = document.querySelector("#faculty-grid");
const fundingSearch = document.querySelector("#funding-search");
const facultySearch = document.querySelector("#faculty-search");
const fundingCategory = document.querySelector("#funding-category");
const facultyKind = document.querySelector("#faculty-kind");

const state = {
  funding: [],
  faculty: [],
  screening: null,
};

async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Could not load ${path}`);
  }
  return response.json();
}

async function loadOptionalJson(path) {
  try {
    return await loadJson(path);
  } catch (error) {
    console.warn(error.message);
    return null;
  }
}

function normalize(value) {
  return String(value || "").toLowerCase();
}

function optionize(select, values, allLabel) {
  select.innerHTML = "";
  const all = document.createElement("option");
  all.value = "";
  all.textContent = allLabel;
  select.append(all);
  values.sort().forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.append(option);
  });
}

function fundingCard(source) {
  const card = document.createElement("article");
  card.className = "card";
  const categoryClass = source.category.replaceAll(" ", "-");
  card.innerHTML = `
    <header>
      <h3>${source.name}</h3>
      <span class="pill ${categoryClass}">${source.category}</span>
    </header>
    <p>${source.notes}</p>
    <div class="tags">
      ${source.focus_areas.slice(0, 5).map((tag) => `<span class="tag">${tag}</span>`).join("")}
    </div>
    <a class="card-link" href="${source.url}">Open source</a>
  `;
  return card;
}

function facultyCard(source) {
  const card = document.createElement("article");
  card.className = "card";
  const kindClass = source.kind.replaceAll(" ", "-");
  const owners = source.owners.length ? source.owners.join(", ") : "Department source";
  card.innerHTML = `
    <header>
      <h3>${source.name}</h3>
      <span class="pill ${kindClass}">${source.kind}</span>
    </header>
    <p>${owners}</p>
    <div class="tags">
      ${source.focus_areas.slice(0, 5).map((tag) => `<span class="tag">${tag}</span>`).join("")}
    </div>
    <a class="card-link" href="${source.url}">Open source</a>
  `;
  return card;
}

function renderFunding() {
  const query = normalize(fundingSearch.value);
  const category = fundingCategory.value;
  const records = state.funding.filter((source) => {
    const haystack = normalize([
      source.name,
      source.category,
      source.sponsor_type,
      source.opportunity_types.join(" "),
      source.focus_areas.join(" "),
      source.notes,
    ].join(" "));
    return (!category || source.category === category) && (!query || haystack.includes(query));
  });
  fundingGrid.replaceChildren(...records.map(fundingCard));
  if (!records.length) {
    fundingGrid.innerHTML = '<div class="empty">No funding sources match this filter.</div>';
  }
}

function renderFaculty() {
  const query = normalize(facultySearch.value);
  const kind = facultyKind.value;
  const records = state.faculty.filter((source) => {
    const haystack = normalize([
      source.name,
      source.kind,
      source.owners.join(" "),
      source.focus_areas.join(" "),
      source.notes,
    ].join(" "));
    return (!kind || source.kind === kind) && (!query || haystack.includes(query));
  });
  facultyGrid.replaceChildren(...records.map(facultyCard));
  if (!records.length) {
    facultyGrid.innerHTML = '<div class="empty">No faculty sources match this filter.</div>';
  }
}

function setText(selector, value) {
  const element = document.querySelector(selector);
  if (element && value !== undefined && value !== null && value !== "") {
    element.textContent = value;
  }
}

function renderScreeningSummary() {
  const summary = state.screening;
  if (!summary) {
    return;
  }

  setText("#screening-count", summary.opportunity_count);
  setText("#active-opportunity-count", summary.active_opportunity_count);
  setText("#alignment-count", summary.alignment_count);
  setText("#nearest-deadline-count", summary.nearest_deadline_days);
  setText("#past-deadline-count", summary.past_due_count);
  setText("#source-recheck-count", summary.source_recheck_count);
  setText("#urgent-action-count", summary.urgent_action_count);
  setText(
    "#screening-as-of",
    `Public sponsor pages checked on ${summary.snapshot_date}. Action status refreshed on ${summary.refreshed_on}.`,
  );
  const nearestCopy = summary.nearest_deadline_program
    ? `${summary.nearest_deadline_program} is the nearest active dated deadline (${summary.nearest_deadline_label}).`
    : "No active dated deadlines remain in this screening.";
  setText("#nearest-deadline-copy", nearestCopy);
  const sourceRecheckCopy = summary.oldest_verification_age_days == null
    ? `Recheck active opportunities without recorded sponsor-source verification before outreach.`
    : `Oldest active source check is ${summary.oldest_verification_age_days} days old; recheck items older than ${summary.verification_stale_after_days} days.`;
  setText("#source-recheck-copy", sourceRecheckCopy);
}

async function init() {
  const [funding, faculty, screening] = await Promise.all([
    loadJson("data/funding_sources.json"),
    loadJson("data/faculty_sources.json"),
    loadOptionalJson("data/screening_summary.json"),
  ]);
  state.funding = funding.sources;
  state.faculty = faculty.sources;
  state.screening = screening;

  document.querySelector("#funding-count").textContent = state.funding.length;
  document.querySelector("#faculty-count").textContent = state.faculty.length;
  document.querySelector("#lab-count").textContent = state.faculty.filter((item) => item.kind === "lab website").length;
  renderScreeningSummary();

  optionize(fundingCategory, [...new Set(state.funding.map((source) => source.category))], "All categories");
  optionize(facultyKind, [...new Set(state.faculty.map((source) => source.kind))], "All kinds");

  fundingSearch.addEventListener("input", renderFunding);
  fundingCategory.addEventListener("change", renderFunding);
  facultySearch.addEventListener("input", renderFaculty);
  facultyKind.addEventListener("change", renderFaculty);

  renderFunding();
  renderFaculty();
}

init().catch((error) => {
  document.querySelector("main").insertAdjacentHTML(
    "afterbegin",
    `<div class="empty">Could not load dashboard data: ${error.message}</div>`,
  );
});
