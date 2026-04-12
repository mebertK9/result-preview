/**
 * rettungsgasse.js
 *
 * Usage:
 *   renderRettungsgasse(containerId, rows, options)
 *
 * rows = array of rows, each row is an array of car objects:
 *   [
 *     [{ lane: 1, side: "left", gameIdx: 5 }, { lane: 2, side: "right", gameIdx: 5 }],
 *     [{ lane: 0, side: "right", gameIdx: 3 }, { lane: 3, side: "right", gameIdx: 7 }],
 *     [],
 *     ...
 *   ]
 *
 * Car object fields:
 *   lane    {0|1|2|3}   - position on road
 *   side    {"left"|"right"} - determines car color (left=blue, right=orange)
 *   gameIdx {number|null}   - index into options.games; null if no game
 *
 * options (optional):
 *   {
 *     games: [                  // lookup by gameIdx
 *       { team1: "BB Löwen Braunschweig", team2: "Opponent" },
 *       ...
 *     ],
 *     hypotheticals: {},        // keyed by gameIdx: [score1, score2]
 *     onAction: function(gameIdx, score1, score2) {}
 *   }
 */

(function () {
  const ROW_H = 72, CAR_W = 48, CAR_H = 58, SHOULDER_W = 80, ROAD_W = 160;
  const LION_H = 68, AMB_H = 60;

  const POS_X = [
    SHOULDER_W / 2 - CAR_W / 2,
    SHOULDER_W + ROAD_W / 4 - CAR_W / 2,
    SHOULDER_W + (3 * ROAD_W) / 4 - CAR_W / 2,
    SHOULDER_W + ROAD_W + SHOULDER_W / 2 - CAR_W / 2,
  ];

  const sirenTimers = {};

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
      .rg-car.has-game{cursor:pointer;outline:2.5px solid rgba(255,255,255,0.6);outline-offset:2px;}
      .rg-car.has-game:active{transform:scale(0.93);}
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

      /* --- Game popup --- */
      .rg-backdrop{position:fixed;inset:0;z-index:1000;background:rgba(0,0,0,0.4);}
      .rg-popup{position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:1001;
        background:#fff;border-radius:14px;padding:20px 18px 16px;width:min(310px,92vw);
        font-family:Arial,sans-serif;box-shadow:0 6px 32px rgba(0,0,0,0.22);}
      .rg-popup-label{font-size:0.73rem;color:#999;margin:0 0 3px;text-transform:uppercase;letter-spacing:0.05em;}
      .rg-popup-teams{font-size:1rem;font-weight:bold;margin:0 0 14px;line-height:1.4;color:#222;}
      .rg-popup-scores{display:flex;align-items:center;gap:8px;margin-bottom:14px;}
      .rg-popup-scores input{width:58px;padding:9px 4px;font-size:1.1rem;text-align:center;
        border:1px solid #bbb;border-radius:7px;-moz-appearance:textfield;}
      .rg-popup-scores input::-webkit-outer-spin-button,
      .rg-popup-scores input::-webkit-inner-spin-button{-webkit-appearance:none;}
      .rg-popup-scores .rg-sep{font-weight:bold;font-size:1.2rem;color:#666;}
      .rg-popup-btns{display:flex;gap:8px;align-items:stretch;}
      .rg-popup-btns button{flex:1;padding:11px 8px;font-size:0.88rem;border:none;
        border-radius:9px;cursor:pointer;font-weight:bold;line-height:1.3;}
      .rg-btn-commit{background:#1D9E75;color:#fff;}
      .rg-btn-cancel{flex:0 0 auto !important;padding:11px 14px !important;background:#ececec;color:#666;}
      .rg-popup-hint{font-size:0.72rem;color:#bbb;margin:10px 0 0;text-align:center;}
    `;
    document.head.appendChild(style);
  }

  function buildScaffold(container, prefix) {
    container.innerHTML = `
      <div class="rg-scene">
        <div class="rg-prog-wrap"><div class="rg-prog-fill" id="${prefix}-prog" style="width:0%"></div></div>
        <div class="rg-road-wrap">
          <div class="rg-shoulder-l"></div><div class="rg-shoulder-r"></div>
          <div class="rg-road-bg"></div>
          <div class="rg-road-edge-l"></div><div class="rg-road-edge-r"></div>
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

  /**
   * Builds (or rebuilds) all row DOM elements.
   * Called on every render to support cars moving between rows.
   *
   * @param {string}   prefix
   * @param {Array}    rows          - array of car-object arrays
   * @param {Array}    games         - lookup by gameIdx
   * @param {Array}    compGames     - lookup by compGameIdx
   * @param {Object}   hypotheticals - keyed by gameIdx: [score1, score2]
   * @param {Function} onAction      - callback(gameIdx, score1, score2)
   */
  function buildRows(prefix, rows, games, compGames, hypotheticals, onAction, comptetior) {
    const area = document.getElementById(`${prefix}-rows`);
    area.innerHTML = '';

    rows.forEach((cars, i) => {
      const div = document.createElement('div');
      div.className = 'rg-row';
      div.id = `${prefix}-row-${i}`;

      const ov = document.createElement('div'); ov.className = 'rg-passed-overlay'; div.appendChild(ov);
      const ci = document.createElement('div'); ci.className = 'rg-clear-ind';      div.appendChild(ci);
      const rn = document.createElement('div'); rn.className = 'rg-row-num';
      rn.textContent = rows.length - i; div.appendChild(rn);

      // Each car in this row gets its own element, keyed by its index within the row
      cars.filter((c) => c.type).forEach((car, j) => {
        const el = document.createElement('div');
        el.className = `rg-car rg-car-${car.type}`;
        el.id = `${prefix}-car-${i}-${j}`;
        el.style.left = POS_X[car.lane] + 'px';
        el.innerHTML = '<div class="rg-car-window"></div><div class="rg-car-strip"></div>';

        var game = null;
        var team = null;
        if(car.type == "right") {
          game = games && games.find(g => g.idx == car.idx);
          team = "BB Löwen Braunschweig";
        } else if( car.type == "left") {
          game = compGames && compGames.find(g => g.idx == car.idx);
          team = comptetior;
        }
         const hypothetical = hypotheticals && hypotheticals[game?.idx];
        if (game && onAction) {
          console.log("build rows: found game for popup:", game, " with index", car.idx)
          el.classList.add('has-game');
          el.addEventListener('click', () => openPopup(game, hypothetical, games.length - 1 - i, onAction, team));
        }

        div.appendChild(el);
      });

      area.appendChild(div);
    });
  }

  /**
   * Opens the score-entry popup for a single car's game.
   *
   * @param {Object}   game         - { team1, team2 }
   * @param {Array}    hypothetical - [score1, score2] or null
   * @param {number}   gameIdx
   * @param {Function} onAction     - callback(gameIdx, rowIndex, score1, score2)
   */
  function openPopup(game, hypothetical, rowIndex, onAction, team) {
    closePopup();

    const isHome = game.team1 === team;
    const opponent = isHome ? game.team2 : game.team1;
    const homeLabel = isHome ? team : opponent;
    const awayLabel = isHome ? opponent : team;

    const backdrop = document.createElement('div');
    backdrop.className = 'rg-backdrop';
    backdrop.id = 'rg-active-backdrop';
    backdrop.addEventListener('click', closePopup);

    const popup = document.createElement('div');
    popup.className = 'rg-popup';
    popup.addEventListener('click', e => e.stopPropagation());
    popup.innerHTML = `
      <p class="rg-popup-label">Ergebnis eintragen</p>
      <p class="rg-popup-teams">${homeLabel} : ${awayLabel}</p>
      <div class="rg-popup-scores">
        <input type="number" id="rg-s1" inputmode="numeric" value="${hypothetical ? hypothetical[0] : ''}" placeholder="–" min="0">
        <span class="rg-sep">:</span>
        <input type="number" id="rg-s2" inputmode="numeric" value="${hypothetical ? hypothetical[1] : ''}" placeholder="–" min="0">
      </div>
      <div class="rg-popup-btns">
        <button class="rg-btn-commit" id="rg-btn-commit">✔ Ergebnis bestätigen</button>
        <button class="rg-btn-cancel" id="rg-btn-cancel">✕</button>
      </div>
      <p class="rg-popup-hint">Ergebnis optional</p>
    `;

    popup.querySelector('#rg-btn-cancel').addEventListener('click', closePopup);

    popup.querySelector('#rg-btn-commit').addEventListener('click', () => {
      const s1 = popup.querySelector('#rg-s1').value;
      const s2 = popup.querySelector('#rg-s2').value;
      closePopup();
      onAction(game, rowIndex, s1 || null, s2 || null, team);
    });

    document.body.appendChild(backdrop);
    document.body.appendChild(popup);
    popup.querySelector('#rg-s1').focus();
  }

  function closePopup() {
    document.getElementById('rg-active-backdrop')?.remove();
    document.querySelector('.rg-popup')?.remove();
  }

  /** A row is clear for the ambulance if no car occupies lanes 1 or 2. */
  function isClear(cars) {
    return cars.filter(c => c.type).every(c => c.lane === 0 || c.lane === 3);
  }

  /** Returns how many rows from the bottom the ambulance has cleared. */
  function calcAmbAt(rows) {
    let ambAt = -1;
    for (let i = rows.length - 1; i >= 0; i--) {
      if (isClear(rows[i])) {
        ambAt = rows.length - 1 - i;
      } else {
        break;
      }
    }
    return ambAt;
  }

  /** Updates overlays and clear-gap indicators after rows have been built. */
  function updateRows(prefix, rows, ambAt) {
    rows.forEach((cars, i) => {
      const rowFromBottom = rows.length - 1 - i;
      const passed = rowFromBottom < ambAt;
      const clear  = isClear(cars);

      const rowEl = document.getElementById(`${prefix}-row-${i}`);
      if (rowEl) {
        rowEl.querySelector('.rg-passed-overlay').style.opacity = (clear || passed) ? '1' : '0';
        rowEl.querySelector('.rg-clear-ind').className = 'rg-clear-ind' + (clear ? ' open' : '');
      }
    });
  }

  function ambTopPx(ambAt, totalRows) {
    if (ambAt < 0)          return totalRows * ROW_H - AMB_H / 2 + 8;
    if (ambAt >= totalRows) return -AMB_H + 8;
    const rowIdx = totalRows - 1 - ambAt;
    return rowIdx * ROW_H + (ROW_H - AMB_H) / 2;
  }

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
   * Public API.
   *
   * @param {string} containerId
   * @param {Array}  rows      - array of rows; each row is an array of car objects
   *                            { lane: 0|1|2|3, side: "left"|"right", gameIdx: number|null }
   * @param {Object} [options]
   * @param {Array}  [options.games]         - lookup array by gameIdx: { team1, team2 }
   * @param {Object} [options.hypotheticals] - keyed by gameIdx: [score1, score2]
   * @param {Function} [options.onAction]    - callback(gameIdx, rowIndex, score1, score2)
   */
  window.renderRettungsgasse = function (containerId, rows, options) {
    options = options || {};
    injectStyles();

    const container = document.getElementById(containerId);
    if (!container) { console.error('renderRettungsgasse: container not found:', containerId); return; }

    const prefix        = containerId;
    const games         = options.games         || null;
    const compGames     = options.competitor_games|| null;
    const competitor    = options.competitor;
    const hypotheticals = options.hypotheticals || null;
    const onAction      = options.onAction      || null;
    const isFirst       = !container.querySelector('.rg-scene');

    if (isFirst) {
      buildScaffold(container, prefix);
      const layer = document.getElementById(`${prefix}-amb-layer`);
      layer.style.top    = LION_H + 'px';
      layer.style.height = (rows.length * ROW_H + AMB_H) + 'px';
      startSiren(prefix);
    }

    // Always rebuild rows so cars can appear/disappear across rows
    buildRows(prefix, rows, games, compGames, hypotheticals, onAction, competitor);

    const ambAt = calcAmbAt(rows);
    updateRows(prefix, rows, ambAt);

    const amb = document.getElementById(`${prefix}-amb`);
    if (amb) amb.style.top = ambTopPx(ambAt, rows.length) + 'px';
    // if (amb) {
    //   amb.style.transition = 'none';
    //   amb.style.top = ambTopPx(-1, rows.length) + 'px';
    //   requestAnimationFrame(() => {
    //     requestAnimationFrame(() => {  // zwei rAF nötig damit transition greift
    //       amb.style.transition = '';
    //       amb.style.top = ambTopPx(ambAt, rows.length) + 'px';
    //     });
    //   });
    // }

    const progress = ambAt < 0 ? 0 : Math.min(ambAt / rows.length, 1);
    const prog = document.getElementById(`${prefix}-prog`);
    if (prog) prog.style.width = (progress * 100) + '%';

    const lion = document.getElementById(`${prefix}-lion`);
    if (lion) lion.style.fontSize = (ambAt >= rows.length) ? '56px' : '42px';
  };

})();