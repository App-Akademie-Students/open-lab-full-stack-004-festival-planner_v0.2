async function loadStages() {
  const response = await fetch("/api/stages");
  const stages = await response.json();
  const select = document.getElementById("stage-filter");
  for (const stage of stages) {
    const option = document.createElement("option");
    option.value = stage;
    option.textContent = stage;
    select.appendChild(option);
  }
  select.addEventListener("change", () => loadProgram(select.value));
}

async function loadProgram(stage = "") {
  const url = stage ? `/api/program?stage=${encodeURIComponent(stage)}` : "/api/program";
  const response = await fetch(url);
  const data = await response.json();
  renderNow(data.now);
  renderProgram(data.items);
}

function renderNow(now) {
  document.getElementById("now-hint").textContent = `Festivalzeit: ${formatTime(now)} Uhr`;
}

function renderProgram(items) {
  const list = document.getElementById("program-list");
  const emptyHint = document.getElementById("empty-hint");

  list.innerHTML = "";
  emptyHint.hidden = items.length > 0;

  for (const item of items) {
    list.appendChild(renderItem(item));
  }
}

function renderItem(item) {
  const li = document.createElement("li");
  li.className = "program-item";
  if (item.status) {
    li.classList.add(`status-${item.status}`);
  }

  const time = document.createElement("span");
  time.className = "time";
  time.textContent = `${formatTime(item.starts_at)}–${formatTime(item.ends_at)}`;

  const title = document.createElement("span");
  title.className = "title";
  title.textContent = item.title;

  const stage = document.createElement("span");
  stage.className = "stage";
  stage.textContent = item.stage;

  li.append(time, title, stage);
  return li;
}

function formatTime(isoString) {
  return isoString.slice(11, 16);
}

loadStages();
loadProgram();
