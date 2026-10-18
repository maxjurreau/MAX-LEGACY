window.Umbrella = {

  nodes: [

    "IDENTITY",

    "SIMULATION",

    "NARRATIVE",

    "OUTPUT"

  ],

  init(){

    const container =
      document.getElementById(
        "umbrella"
      );

    container.innerHTML = "";

    this.nodes.forEach(name=>{

      const div =
        document.createElement(
          "div"
        );

      div.className =
        "node";

      div.innerText =
        name;

      div.onclick=()=>{

        logEvent(
          "NODE: " +
          name
        );

      };

      container.appendChild(
        div
      );

    });

  }

};
