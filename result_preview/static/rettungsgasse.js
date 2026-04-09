/**
 * rettungsgasse.js
 *
 * Usage:
 *   renderRettungsgasse(containerId, rows)
 *
 * rows = output of to_rettungswagen(grid), e.g.:
 *   [[1,2], [0,3], [null,2], [1,null]]
 *
 * Each entry is [g_pos, l_pos] (0-3 or null if car absent).
 * rows[0] = row farthest from ambulance (top = closest to lion).
 * rows[N-1] = row nearest to ambulance (bottom).
 *
 * Can be called multiple times with the same containerId to update in place.
 * Can be called with different containerIds for multiple independent instances.
 */

(function () {
  const ROW_H = 72, CAR_W = 48, CAR_H = 58, SHOULDER_W = 80, ROAD_W = 160;
  const LION_H = 68, AMB_H = 60;

  // x-position (left edge) for each column index 0-3
  const POS_X = [
    SHOULDER_W / 2 - CAR_W / 2,                        // 0: left shoulder
    SHOULDER_W + ROAD_W / 4 - CAR_W / 2,               // 1: left lane
    SHOULDER_W + (3 * ROAD_W) / 4 - CAR_W / 2,         // 2: right lane
    SHOULDER_W + ROAD_W + SHOULDER_W / 2 - CAR_W / 2,  // 3: right shoulder
  ];

  // Track siren timers per instance
  const sirenTimers = {};

  /** Inject shared CSS once into the document head. */
  function injectStyles() {
    if (document.getElementById('rg-styles')) return;
    const style = document.createElement('style');
    style.id = 'rg-styles';
    style.textContent = `
      .rg-scene{display:flex;flex-direction:column;align-items:center;padding:12px 0 16px;max-width:390px;margin:0 auto;user-select:none;}
      .rg-road-wrap{position:relative;width:${ROAD_W + SHOULDER_W * 2}px;}
      .rg-shoulder-l,.rg-shoulder-r{position:absolute;top:0;bottom:0;width:${SHOULDER_W}px;background:#8ac08a;}
      .rg-shoulder-l{left:0;}.rg-shoulder-r{right:0;}
      .rg-road-bg{position:absolute;left:${SHOULDER_W}px;top:0;bottom:0;width:${ROAD_W}px;background:#4a4a4a;}
      .rg-road-edge-l{position:absolute;left:${SHOULDER_W}px;top:0;bottom:0;width:3px;background:#e0e0e0;}
      .rg-road-edge-r{position:absolute;right:${SHOULDER_W}px;top:0;bottom:0;width:3px;background:#e0e0e0;}
      .rg-lane-marker{position:absolute;left:${SHOULDER_W + ROAD_W / 2 - 2}px;top:0;bottom:0;width:4px;
        background:repeating-linear-gradient(to bottom,#e8c84a 0,#e8c84a 18px,transparent 18px,transparent 34px);}
      .rg-rows-area{position:relative;}
      .rg-row{position:relative;height:${ROW_H}px;}
      .rg-car{position:absolute;top:7px;width:${CAR_W}px;height:${CAR_H}px;border-radius:6px 6px 4px 4px;
        display:flex;flex-direction:column;align-items:center;justify-content:center;
        transition:left 0.4s cubic-bezier(0.4,0,0.2,1);z-index:10;}
      .rg-car-left{background:#378ADD;}.rg-car-right{background:#D85A30;}
      .rg-car-window{width:34px;height:14px;background:rgba(255,255,255,0.35);border-radius:3px;margin-bottom:4px;}
      .rg-car-strip{width:34px;height:4px;background:rgba(0,0,0,0.12);border-radius:2px;}
      .rg-clear-ind{position:absolute;left:50%;top:0;bottom:0;transform:translateX(-50%);
        width:30px;border-left:2.5px dashed rgba(255,255,255,0.2);border-right:2.5px dashed rgba(255,255,255,0.2);
        pointer-events:none;transition:border-color 0.3s;z-index:5;}
      .rg-clear-ind.open{border-left-color:rgba(30,200,120,0.7);border-right-color:rgba(30,200,120,0.7);}
      .rg-passed-overlay{position:absolute;left:${SHOULDER_W}px;right:${SHOULDER_W}px;top:0;bottom:0;
        background:rgba(30,160,100,0.15);opacity:0;transition:opacity 0.4s;pointer-events:none;z-index:3;}
      .rg-row-num{position:absolute;left:4px;top:50%;transform:translateY(-50%);font-size:10px;color:rgba(255,255,255,0.5);z-index:20;}
      .rg-amb-layer{position:absolute;left:0;right:0;pointer-events:none;z-index:30;}
      .rg-ambulance{position:absolute;left:50%;transform:translateX(-50%);
        width:44px;height:${AMB_H}px;background:#eee;border-radius:6px 6px 4px 4px;
        border:2px solid #ccc;display:flex;flex-direction:column;align-items:center;justify-content:center;
        transition:top 0.55s cubic-bezier(0.4,0,0.2,1);}
      .rg-amb-siren{width:28px;height:8px;background:#1a6fc4;border-radius:3px;margin-bottom:3px;transition:background 0.2s;}
      .rg-amb-siren.red{background:#e84040;}
      .rg-amb-cross{position:relative;width:20px;height:20px;}
      .rg-amb-cross::before,.rg-amb-cross::after{content:'';position:absolute;background:#cc2222;border-radius:1px;}
      .rg-amb-cross::before{width:6px;height:20px;left:7px;top:0;}
      .rg-amb-cross::after{width:20px;height:6px;left:0;top:7px;}
      .rg-lion-row{height:${LION_H}px;display:flex;align-items:center;justify-content:center;
        font-size:42px;position:relative;z-index:5;transition:font-size 0.3s;}
      .rg-prog-wrap{width:${ROAD_W + SHOULDER_W * 2}px;height:6px;background:#ddd;border-radius:3px;margin:8px 0 10px;overflow:hidden;}
      .rg-prog-fill{height:100%;background:#1D9E75;border-radius:3px;transition:width 0.4s ease;}
    `;
    document.head.appendChild(style);
  }

  /** Build the initial DOM structure inside the container. */
  function buildScaffold(container, prefix) {
    container.innerHTML = `
      <div class="rg-scene">
        <div class="rg-prog-wrap"><div class="rg-prog-fill" id="${prefix}-prog" style="width:0%"></div></div>
        <div class="rg-road-wrap">
          <div class="rg-shoulder-l"></div>
          <div class="rg-shoulder-r"></div>
          <div class="rg-road-bg"></div>
          <div class="rg-road-edge-l"></div>
          <div class="rg-road-edge-r"></div>
          <div class="rg-lane-marker"></div>
          <div class="rg-lion-row" id="${prefix}-lion">🦁</div>
          <div class="rg-rows-area" id="${prefix}-rows"></div>
          <div class="rg-amb-layer" id="${prefix}-amb-layer">
            <div class="rg-ambulance" id="${prefix}-amb">
              <div class="rg-amb-siren" id="${prefix}-siren"></div>
              <div class="rg-amb-cross"></div>
            </div>
          </div>
        </div>
      </div>`;
  }

  /** Build all row elements from scratch. */
  function buildRows(prefix, rows) {
    const area = document.getElementById(`${prefix}-rows`);
    area.innerHTML = '';
    rows.forEach(([lp, rp], i) => {
      const div = document.createElement('div');
      div.className = 'rg-row';
      div.id = `${prefix}-row-${i}`;

      const ov  = document.createElement('div'); ov.className  = 'rg-passed-overlay'; div.appendChild(ov);
      const ci  = document.createElement('div'); ci.className  = 'rg-clear-ind';      div.appendChild(ci);
      const rn  = document.createElement('div'); rn.className  = 'rg-row-num';
      rn.textContent = rows.length - i; div.appendChild(rn);

      // Left car (G) – only if position is not null
      if (lp !== null) {
        const lc = document.createElement('div');
        lc.className = 'rg-car rg-car-left';
        lc.id = `${prefix}-cl-${i}`;
        lc.style.left = POS_X[lp] + 'px';
        lc.innerHTML = '<div class="rg-car-window"></div><div class="rg-car-strip"></div>';
        div.appendChild(lc);
      }

      // Right car (L) – only if position is not null
      if (rp !== null) {
        const rc = document.createElement('div');
        rc.className = 'rg-car rg-car-right';
        rc.id = `${prefix}-cr-${i}`;
        rc.style.left = POS_X[rp] + 'px';
        rc.innerHTML = '<div class="rg-car-window"></div><div class="rg-car-strip"></div>';
        div.appendChild(rc);
      }

      area.appendChild(div);
    });
  }

  /**
   * A row is clear for the ambulance when both sides are out of the way:
   * - left car absent (null) or on shoulder (0)
   * - right car absent (null) or on shoulder (3)
   */
  function isClear(lp, rp) {
    return (lp === null || lp === 0) && (rp === null || rp === 3);
  }

  /**
   * Calculate how far the ambulance can advance.
   * Count consecutive clear rows from the bottom (index rows.length-1 upward).
   * Returns -1 if the bottom row is blocked (ambulance hasn't moved at all).
   */
  function calcAmbAt(rows) {
    let ambAt = -1;
    for (let i = rows.length - 1; i >= 0; i--) {
      const [lp, rp] = rows[i];
      if (isClear(lp, rp)) {
        ambAt = rows.length - 1 - i; // distance from bottom
      } else {
        break;
      }
    }
    return ambAt;
  }

  /** Update car positions and overlays without rebuilding DOM. */
  function updateRows(prefix, rows, ambAt) {
    rows.forEach(([lp, rp], i) => {
      const rowFromBottom = rows.length - 1 - i;
      const passed = rowFromBottom < ambAt;
      const clear  = isClear(lp, rp);

      const lc = document.getElementById(`${prefix}-cl-${i}`);
      const rc = document.getElementById(`${prefix}-cr-${i}`);
      if (lc && lp !== null) lc.style.left = POS_X[lp] + 'px';
      if (rc && rp !== null) rc.style.left = POS_X[rp] + 'px';

      const rowEl = document.getElementById(`${prefix}-row-${i}`);
      if (rowEl) {
        rowEl.querySelector('.rg-passed-overlay').style.opacity = (clear || passed) ? '1' : '0';
        rowEl.querySelector('.rg-clear-ind').className = 'rg-clear-ind' + (clear ? ' open' : '');
      }
    });
  }

  /** Calculate the CSS top value for the ambulance element. */
  function ambTopPx(ambAt, totalRows) {
    if (ambAt < 0)          return totalRows * ROW_H - AMB_H / 2 + 8; // waiting below all rows
    if (ambAt >= totalRows) return -AMB_H + 8;                          // past all rows (at lion)
    const rowIdx = totalRows - 1 - ambAt;
    return rowIdx * ROW_H + (ROW_H - AMB_H) / 2;
  }

  /** Start or restart the siren blink for this instance. */
  function startSiren(prefix) {
    clearInterval(sirenTimers[prefix]);
    const siren = document.getElementById(`${prefix}-siren`);
    let on = false;
    sirenTimers[prefix] = setInterval(() => {
      on = !on;
      if (siren) siren.className = 'rg-amb-siren' + (on ? ' red' : '');
    }, 380);
  }

  /**
   * Public API – render or update a rettungsgasse widget.
   *
   * @param {string} containerId - ID of the host element
   * @param {Array}  rows        - output of to_rettungswagen(grid)
   */
  window.renderRettungsgasse = function (containerId, rows) {
    injectStyles();

    const container = document.getElementById(containerId);
    if (!container) { console.error('renderRettungsgasse: container not found:', containerId); return; }

    // Use container ID as prefix to keep all IDs unique across instances
    const prefix = containerId;
    const isFirstRender = !container.querySelector('.rg-scene');

    if (isFirstRender) {
      buildScaffold(container, prefix);
      buildRows(prefix, rows);

      // Set ambulance layer height
      const layer = document.getElementById(`${prefix}-amb-layer`);
      layer.style.top    = LION_H + 'px';
      layer.style.height = (rows.length * ROW_H + AMB_H) + 'px';

      startSiren(prefix);
    }

    const ambAt = calcAmbAt(rows);

    updateRows(prefix, rows, ambAt);

    // Position ambulance
    const amb = document.getElementById(`${prefix}-amb`);
    if (amb) amb.style.top = ambTopPx(ambAt, rows.length) + 'px';

    // Progress bar: fraction of rows the ambulance has passed
    const progress = ambAt < 0 ? 0 : Math.min(ambAt / rows.length, 1);
    const prog = document.getElementById(`${prefix}-prog`);
    if (prog) prog.style.width = (progress * 100) + '%';

    // Lion pulse when ambulance reaches the end
    const lion = document.getElementById(`${prefix}-lion`);
    if (lion) lion.style.fontSize = (ambAt >= rows.length) ? '56px' : '42px';
  };
})();
