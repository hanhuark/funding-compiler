const fundingGrid = document.querySelector("#funding-grid");
const facultyGrid = document.querySelector("#faculty-grid");
const fundingSearch = document.querySelector("#funding-search");
const facultySearch = document.querySelector("#faculty-search");
const fundingCategory = document.querySelector("#funding-category");
const facultyKind = document.querySelector("#faculty-kind");

const state = {
  funding: [],
  faculty: [],
};

async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Could not load ${path}`);
  }
  return response.json();
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

async function init() {
  const [funding, faculty] = await Promise.all([
    loadJson("data/funding_sources.json"),
    loadJson("data/faculty_sources.json"),
  ]);
  state.funding = funding.sources;
  state.faculty = faculty.sources;

  document.querySelector("#funding-count").textContent = state.funding.length;
  document.querySelector("#faculty-count").textContent = state.faculty.length;
  document.querySelector("#lab-count").textContent = state.faculty.filter((item) => item.kind === "lab website").length;

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
