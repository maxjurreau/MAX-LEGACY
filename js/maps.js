window.Maps = {

  active: "physics",

  list: [
    "physics",
    "compute",
    "simulation",
    "cognition",
    "markets"
  ],

  init() {

    const tabs =
      document.getElementById("mapTabs");

    const explorer =
      document.getElementById("maps-list");

    tabs.innerHTML = "";

    this.list.forEach(name => {

      const btn =
        document.createElement("button");

      btn.className = "map-tab";
      btn.innerText = name;

      btn.onclick = () => {
        selectMap(name);
      };

      tabs.appendChild(btn);

    });

    explorer.innerHTML =
      this.list.map(m =>
        `<div class="node">${m}</div>`
      ).join("");

    selectMap("physics");

  }

};

function selectMap(map){

  Maps.active = map;

  const el =
    document.getElementById(
      "maps-container"
    );

  el.innerHTML = `
    <h2>${map.toUpperCase()}</h2>

    <p>
      Portal Workspace:
      ${map}
    </p>
  `;

}

function exportMaps(){

  localStorage.setItem(
    "portal.maps",
    JSON.stringify(
      Maps.list
    )
  );

  alert("Maps exported");

}

function importMaps(){

  const data =
    localStorage.getItem(
      "portal.maps"
    );

  alert(
    data ||
    "No maps stored"
  );

}
