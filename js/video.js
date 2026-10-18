window.Video = {

  hud:true,

  init(){

    resizeHud();

    window.addEventListener(
      "resize",
      resizeHud
    );

    drawHud();

  }

};

async function toggleCameraView(){

  try{

    const stream =
      await navigator
      .mediaDevices
      .getUserMedia({

        video:true

      });

    const video =
      document.getElementById(
        "liveVideo"
      );

    video.srcObject =
      stream;

    video.style.display =
      "block";

    logEvent(
      "Camera Activated"
    );

  }

  catch(err){

    printCli(
      "Camera Error"
    );

  }

}

function toggleHud(){

  Video.hud =
    !Video.hud;

}

function resizeHud(){

  const canvas =
    document.getElementById(
      "hudCanvas"
    );

  if(!canvas) return;

  canvas.width =
    canvas.offsetWidth;

  canvas.height =
    canvas.offsetHeight;

}

function drawHud(){

  const canvas =
    document.getElementById(
      "hudCanvas"
    );

  if(!canvas){

    requestAnimationFrame(
      drawHud
    );

    return;

  }

  const ctx =
    canvas.getContext("2d");

  ctx.clearRect(
    0,
    0,
    canvas.width,
    canvas.height
  );

  if(Video.hud){

    ctx.strokeStyle =
      "#00ffff";

    ctx.lineWidth=2;

    ctx.strokeRect(
      200,
      120,
      120,
      150
    );

    ctx.fillStyle =
      "#00ff88";

    ctx.font =
      "16px Arial";

    ctx.fillText(
      "MAX-SIM ACTIVE",
      25,
      30
    );

  }

  requestAnimationFrame(
    drawHud
  );

}

function loadView(view){

  const video =
    document.getElementById(
      "simVideo"
    );

  video.src =
    "/videos/" +
    view +
    ".mp4";

  video.play();

}

function focusVideo(){

  document
  .querySelector(
    ".video-module"
  )
  .scrollIntoView({

    behavior:"smooth"

  });

}

function connectWebSocket(url){

  try{

    const ws =
      new WebSocket(url);

    ws.onopen=()=>{

      logEvent(
       "WS CONNECTED"
      );

    };

    ws.onmessage=(e)=>{

      logEvent(
       e.data
      );

    };

    ws.onerror=()=>{

      logEvent(
       "WS ERROR"
      );

    };

  }

  catch(err){

    logEvent(
      "WS FAILED"
    );

  }

}
