from flask import Flask, jsonify
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

@app.route("/api/websim_events", methods=["GET"])
def websim_events():
    # ---- TIMING ----
    # Example: event starts ~6h from now, lasts 15m. Tweak as you wish
    now = datetime.now(timezone.utc).replace(microsecond=0)
    start = now + timedelta(hours=6)
    end   = start + timedelta(minutes=15)

    payload = {
        "version": now.strftime("%Y-%m-%d"),
        "events": [
            {
                "id": "wle-rift",
                "start": start.isoformat().replace("+00:00", "Z"),
                "end":   end.isoformat().replace("+00:00", "Z"),
                "runInPage": True,  # we’ll touch page-level styles; run in page context
                # --- LIVE CODE: rift -> grow -> explode -> console "Get ready..." + Exit (refresh) ---
                "code": """
function(ctx){
  // Guard: don't duplicate if user re-enters during live
  if (document.getElementById('wle-rift-root')) return;

  const root = document.createElement('div');
  root.id = 'wle-rift-root';
  root.style.cssText = `
    position: fixed; inset: 0; z-index: 2147483647;
    background: radial-gradient(closest-side, rgba(0,0,0,0.10), rgba(0,0,0,0.55));
    pointer-events: auto;
  `;
  document.body.appendChild(root);

  // Inject styles & keyframes
  const style = document.createElement('style');
  style.textContent = `
    @keyframes wle-crack-draw { from { stroke-dashoffset: 600; } to { stroke-dashoffset: 0; } }
    @keyframes wle-grow {
      0% { transform: translate(-50%, -50%) scale(1); }
      100% { transform: translate(-50%, -50%) scale(12); }
    }
    @keyframes wle-shake {
      0% { transform: translate(-50%, -50%) translate(0,0); }
      25% { transform: translate(-50%, -50%) translate(1px,-1px); }
      50% { transform: translate(-50%, -50%) translate(-1px,1px); }
      75% { transform: translate(-50%, -50%) translate(1px,1px); }
      100% { transform: translate(-50%, -50%) translate(0,0); }
    }
    .wle-center { position:absolute; left:50%; top:50%; transform: translate(-50%,-50%); }
    .wle-crack-glow {
      position:absolute; left:50%; top:50%; transform: translate(-50%,-50%);
      width: 140px; height: 140px; border-radius: 50%;
      background: radial-gradient(circle, rgba(0,255,255,0.35) 0%, rgba(0,0,0,0) 70%);
      filter: blur(8px);
      pointer-events:none;
    }
    .wle-console {
      position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
      background: #0b0d12;
      animation: fadeIn .25s ease-out both;
    }
    .wle-console-panel {
      width: min(680px, 90vw);
      border-radius: 12px; border: 1px solid #18202f;
      background: #0f1420; box-shadow: 0 20px 80px rgba(0,0,0,.6);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      color: #b6ffb6;
      overflow: hidden;
    }
    .wle-console-header {
      padding: 10px 14px;
      background: linear-gradient(180deg, #121a2b 0%, #0f1420 100%);
      border-bottom:1px solid #18202f; color:#8bd48b; font-weight:700; letter-spacing:.02em;
    }
    .wle-console-body { padding: 16px 14px; }
    .wle-console-body .prompt { color:#62c462; }
    .wle-console-body .cursor { display:inline-block; width: 8px; background:#62c462; animation: blink 1s step-end infinite; }
    .wle-exit {
      margin: 14px; padding:8px 12px; border-radius:10px; border:1px solid #233149;
      background:#121a2b; color:#cfe3ff; font-weight:600; cursor:pointer;
    }
    .wle-exit:hover { background:#162038; }
    @keyframes blink { 50% { opacity: 0; } }
    @keyframes fadeIn { from { opacity: 0 } to { opacity: 1 } }
  `;
  document.head.appendChild(style);

  // Central crack SVG
  const center = document.createElement('div');
  center.className = 'wle-center';
  root.appendChild(center);

  const svgNS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(svgNS, 'svg');
  svg.setAttribute('width', '300');
  svg.setAttribute('height', '300');
  svg.setAttribute('viewBox', '0 0 300 300');
  svg.style.cssText = 'overflow: visible; filter: drop-shadow(0 0 18px rgba(0,255,255,.6));';
  center.appendChild(svg);

  // Make multiple crack rays from center (150,150)
  function rayPath(angleDeg, segments=6, segLen=18, jag=10){
    const rad = angleDeg * Math.PI/180;
    let x = 150, y = 150;
    const pts = [[x,y]];
    for (let i=0;i<segments;i++){
      const jitter = (Math.random()-0.5)*jag;
      x += Math.cos(rad) * (segLen + (Math.random()*4-2));
      y += Math.sin(rad) * (segLen + (Math.random()*4-2));
      x += Math.cos(rad + Math.PI/2) * jitter;
      y += Math.sin(rad + Math.PI/2) * jitter;
      pts.push([x,y]);
    }
    return 'M ' + pts.map(p => p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' L ');
  }

  const rays = [];
  const rayCount = 14;
  for (let i=0;i<rayCount;i++){
    const angle = (360/rayCount)*i + (Math.random()*10-5);
    const path = document.createElementNS(svgNS, 'path');
    path.setAttribute('d', rayPath(angle, 7, 22, 16));
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', i%2 ? '#ccffff' : '#66ffff');
    path.setAttribute('stroke-width', i%3 ? '2.2' : '3.2');
    path.setAttribute('stroke-linecap', 'round');
    path.setAttribute('stroke-dasharray', '600');
    path.setAttribute('stroke-dashoffset', '600');
    path.style.animation = `wle-crack-draw ${0.7 + Math.random()*0.3}s ease-out forwards`;
    svg.appendChild(path);
    rays.push(path);
  }

  // Glow
  const glow = document.createElement('div');
  glow.className = 'wle-crack-glow';
  root.appendChild(glow);

  // Subtle center shake for suspense
  const shakeInterval = setInterval(() => {
    center.style.animation = 'wle-shake 0.24s linear';
    setTimeout(()=>{ center.style.animation = ''; }, 240);
  }, 320);

  // After crack draws, grow big, darken bg, then "explode"
  setTimeout(() => {
    center.style.transition = 'transform 1.2s cubic-bezier(.2,.8,.2,1)';
    center.style.transform = 'translate(-50%,-50%) scale(10)';
    root.style.transition = 'background 1s ease-out';
    root.style.background = 'radial-gradient(closest-side, rgba(0,0,0,0.35), rgba(0,0,0,0.95))';
  }, 900);

  // Explosion flash
  setTimeout(() => {
    clearInterval(shakeInterval);
    const flash = document.createElement('div');
    flash.style.cssText = 'position:absolute;inset:0;background:white;opacity:1;pointer-events:none;filter:blur(2px);';
    root.appendChild(flash);
    setTimeout(()=>{ flash.style.transition = 'opacity 220ms ease-out'; flash.style.opacity = '0'; }, 40);
    setTimeout(()=>{ flash.remove(); svg.remove(); glow.remove(); center.remove(); }, 260);
  }, 2200);

  // Console-like "Get ready..." with Exit
  setTimeout(() => {
    const screen = document.createElement('div');
    screen.className = 'wle-console';
    screen.innerHTML = `
      <div class="wle-console-panel">
        <div class="wle-console-header">WLE • Live Boot</div>
        <div class="wle-console-body">
          <div><span class="prompt">$</span> Initializing sequence<span class="cursor">&nbsp;</span></div>
          <div style="margin-top:10px;color:#9fe09f;">Get ready...</div>
        </div>
        <div style="display:flex;justify-content:flex-end;">
          <button class="wle-exit" id="wle-exit">Exit</button>
        </div>
      </div>
    `;
    root.appendChild(screen);
    const exitBtn = screen.querySelector('#wle-exit');
    exitBtn.addEventListener('click', () => {
      try { document.getElementById('wle-rift-root')?.remove(); } catch(e){}
      location.reload();
    }, { once:true });
  }, 2500);
}
                """,
                # --- Optional custom REPLAY code (same behavior here) ---
                "replayCode": """
function(ctx){
  // Run the same effect during replay
  (function(){ /* invoke live code */ })();
  // For simplicity, reuse main code by re-calling if needed:
  // But most userscripts call replay separately. We'll just call the same:
  const f = """ + "function(ctx){ /* placeholder; actual main code is executed by the userscript using replayCode or code */ }" + """
}
                """,
                # --- BUILD-UP: subtle shake/glow at T-5 ---
                "buildup": [
                    {
                        "label": "Rift Warmup (T-5)",
                        "minutesBeforeStart": 5,
                        "code": """
function(ctx){
  if (document.getElementById('wle-rift-warmup')) return;
  const warm = document.createElement('div');
  warm.id = 'wle-rift-warmup';
  warm.style.cssText = 'position:fixed;inset:0;z-index:2147483000;pointer-events:none;';
  document.body.appendChild(warm);

  const s = document.createElement('style');
  s.textContent = `
    @keyframes wle-warm-shake {
      0% { transform: translate(0,0); } 25% { transform: translate(1px,-1px); }
      50% { transform: translate(-1px,1px); } 75% { transform: translate(1px,1px); }
      100% { transform: translate(0,0); }
    }
  `;
  document.head.appendChild(s);

  const glow = document.createElement('div');
  glow.style.cssText = 'position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:120px;height:120px;border-radius:50%;background:radial-gradient(circle, rgba(0,255,255,0.18) 0%, rgba(0,0,0,0) 70%);filter:blur(8px);';
  warm.appendChild(glow);

  // Gentle camera shake hint every ~2s
  const tick = setInterval(() => {
    warm.style.animation = 'wle-warm-shake 0.28s linear';
    setTimeout(()=>{ warm.style.animation = ''; }, 280);
  }, 2000);

  // Auto-remove warmup shortly after live would take over (safety)
  setTimeout(() => { clearInterval(tick); warm.remove(); }, 6 * 60 * 1000);
}
                        """
                    }
                ]
            }
        ]
    }
    return jsonify(payload)
