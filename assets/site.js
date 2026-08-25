(function () {
  var bar = document.querySelector(".topbar");
  var toggle = document.querySelector(".menu-toggle");
  if (toggle && bar) {
    toggle.addEventListener("click", function () {
      var open = bar.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var scene = document.querySelector("[data-scene]");
  if (scene && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var mx = 0;
    var my = 0;
    var cx = 0;
    var cy = 0;
    window.addEventListener("pointermove", function (e) {
      mx = (e.clientX / window.innerWidth - 0.5) * 2;
      my = (e.clientY / window.innerHeight - 0.5) * 2;
    });
    (function tick() {
      cx += (mx - cx) * 0.05;
      cy += (my - cy) * 0.05;
      scene.style.transform = "translate(" + cx * 18 + "px," + cy * 12 + "px)";
      requestAnimationFrame(tick);
    })();
  }

  document.querySelectorAll("[data-egg]").forEach(function (egg) {
    egg.addEventListener("click", function () {
      egg.classList.remove("is-boing");
      void egg.offsetWidth;
      egg.classList.add("is-boing");
    });
    egg.addEventListener("animationend", function (e) {
      if (e.animationName === "egg-boing") egg.classList.remove("is-boing");
    });
  });

  (function bounceRoute() {
    var stage = document.querySelector("[data-bounce-stage]");
    var ball = document.querySelector("[data-bounce-ball]");
    if (!stage || !ball) return;

    var body = ball.querySelector(".bounce-egg");
    var shadow = ball.querySelector(".egg-shadow");
    var svg = stage.querySelector(".bounce-route");
    var line = stage.querySelector("[data-route-line]");
    var apexes = stage.querySelector("[data-route-apexes]");
    var reduce =
      window.matchMedia("(prefers-reduced-motion: reduce)").matches ||
      /(?:\?|&)motion=reduce(?:&|$)/.test(location.search);

    var gravity = 2120;
    var groundFriction = 18;
    var enterDelay = 180;
    var swayAmp = 13;
    var swayMs = 2600;

    var wld = null;
    var plan = null;
    var state = null;
    var phase = "wait";
    var launchedAt = 0;
    var enterDone = false;
    var segK = -1;
    var segT = 0;
    var dragging = false;
    var grabDX = 0;
    var grabDY = 0;
    var hist = [];
    var last = 0;
    var acc = 0;
    var dt = 1 / 60;
    var squash = 0;
    var squashV = 0;
    var squashHold = 0;
    var swayOrigin = 0;

    if (reduce) stage.classList.add("is-reduced");

    function world() {
      var route = svg.getBoundingClientRect();
      return {
        w: route.width,
        h: route.height,
        rx: (body.offsetWidth || 52) / 2,
        r: (body.offsetHeight || 66) / 2,
        top: route.top,
        left: route.left,
        bottom: route.bottom,
      };
    }

    function buildEnterPath() {
      var x0 = wld.rx + 8;
      var xEnd = wld.w - wld.rx;
      var floor = wld.r;
      var dropY = floor + Math.max(96, (wld.h - floor - 14) * 0.82);
      var hops = 4;
      var rest = 0.82;
      var fric = 0.85;
      var h0 = Math.max(64, (wld.h - floor - 18) * 0.5);
      var v00 = Math.sqrt(2 * gravity * h0);
      var span = Math.max(80, xEnd - x0);
      var q = rest * fric;
      var geom = (1 - Math.pow(q, hops)) / (1 - q);
      var vx0 = (span * gravity) / (2 * v00 * geom);
      var landings = [x0];
      var v0s = [];
      var vxs = [];
      var k;
      var xk = x0;
      for (k = 0; k < hops; k += 1) {
        var v0k = v00 * Math.pow(rest, k);
        var vxk = vx0 * Math.pow(fric, k);
        v0s.push(v0k);
        vxs.push(vxk);
        xk += (2 * v0k * vxk) / gravity;
        landings.push(xk);
      }
      landings[hops] = xEnd;
      plan = {
        x0: x0,
        xEnd: xEnd,
        floor: floor,
        dropY: dropY,
        hops: hops,
        v0s: v0s,
        vxs: vxs,
        landings: landings,
      };
    }

    // y_k(x) = -g/(2 vx_k^2) (x - x_k)^2 + (v0k / vx_k) (x - x_k)
    // 空中 vx_k 不变；每次落地地面摩擦：vx_{k+1} = vx_k * fric
    function yk(x, xk, v0k, vx) {
      var dx = x - xk;
      return (-gravity / (2 * vx * vx)) * dx * dx + (v0k / vx) * dx;
    }

    function stepSpring(pos, vel, target, stepDt, stiffness, damping, mass) {
      var accel = (-stiffness * (pos - target) - damping * vel) / mass;
      vel += accel * stepDt;
      pos += vel * stepDt;
      return { pos: pos, vel: vel };
    }

    function grounded(s) {
      return s.y <= wld.r + 1.5 && Math.abs(s.vy) < 48;
    }

    function settled(s) {
      return s.y <= wld.r + 1.5 && Math.abs(s.vy) < 28 && Math.abs(s.vx) < 22;
    }

    function recoverSquash(stepDt) {
      if (squashHold > 0) {
        squashHold -= stepDt;
        return;
      }
      var rec = stepSpring(squash, squashV, 0, stepDt, 70, 14, 1);
      squash = rec.pos;
      squashV = rec.vel;
      if (Math.abs(squash) < 0.006 && Math.abs(squashV) < 0.08) {
        squash = 0;
        squashV = 0;
      }
    }

    function squashImpact(vy) {
      squash = Math.min(0.48, 0.22 + Math.abs(vy) / 1600);
      squashV = 0;
      squashHold = 0.08;
    }

    function step(s, stepDt, grip) {
      var wasAir = s.y > wld.r + 0.8;
      var prevVy = s.vy;

      if (wasAir) s.vy -= gravity * stepDt;
      s.y += s.vy * stepDt;
      s.x += s.vx * stepDt;

      if (s.y <= wld.r) {
        if (wasAir && prevVy < -80) squashImpact(prevVy);
        s.y = wld.r;
        s.vy = 0;
      } else {
        recoverSquash(stepDt);
      }

      if (grip && grounded(s)) {
        s.vx *= Math.exp(-groundFriction * stepDt);
        if (Math.abs(s.vx) < 16) s.vx = 0;
      }

      if (s.x < wld.rx) {
        s.x = wld.rx;
        if (s.vx < 0) s.vx = 0;
      } else if (s.x > wld.w - wld.rx) {
        s.x = wld.w - wld.rx;
        if (s.vx > 0) s.vx = 0;
      }
    }

    function landEnter() {
      var v0k = plan.v0s[Math.max(0, segK)];
      squashImpact(segK < 0 ? state.vy : -v0k);
      state.y = wld.r;
      state.vy = 0;
      if (segK < 0) {
        state.x = plan.x0;
        state.vx = 0;
        segK = 0;
        segT = 0;
        return;
      }
      state.x = plan.landings[segK + 1];
      segK += 1;
      segT = 0;
      if (segK >= plan.hops) {
        state.vx = 0;
        state.x = plan.xEnd;
        finishEnter();
      }
    }

    function advanceEnter(stepDt) {
      if (enterDone) return;
      if (segK < 0) {
        segT += stepDt;
        state.x = plan.x0;
        state.vx = 0;
        state.vy = -gravity * segT;
        state.y = plan.dropY - 0.5 * gravity * segT * segT;
        if (state.y <= wld.r) landEnter();
        else recoverSquash(stepDt);
        return;
      }
      var v0k = plan.v0s[segK];
      var vxk = plan.vxs[segK];
      var xk = plan.landings[segK];
      var xNext = plan.landings[segK + 1];
      segT += stepDt;
      state.vx = vxk;
      state.x = xk + vxk * segT;
      state.vy = v0k - gravity * segT;
      state.y = wld.r + Math.max(0, yk(state.x, xk, v0k, vxk));
      if (state.x >= xNext) landEnter();
      else recoverSquash(stepDt);
    }

    function seedEnter() {
      return {
        x: plan.x0,
        y: plan.dropY,
        vx: 0,
        vy: 0,
      };
    }

    function seedRight() {
      return { x: wld.w - wld.rx, y: wld.r, vx: 0, vy: 0 };
    }

    function pointerPhys(e) {
      return {
        x: e.clientX - wld.left,
        y: wld.bottom - e.clientY,
      };
    }

    function recordHist(x, y, t) {
      hist.push({ x: x, y: y, t: t });
      while (hist.length && t - hist[0].t > 130) hist.shift();
    }

    function flickVel() {
      if (hist.length < 2) return { vx: 0, vy: 0 };
      var a = hist[0];
      var b = hist[hist.length - 1];
      var d = (b.t - a.t) / 1000;
      if (d < 0.012) return { vx: 0, vy: 0 };
      var vx = (b.x - a.x) / d;
      var vy = (b.y - a.y) / d;
      var cap = 1800;
      var sp = Math.sqrt(vx * vx + vy * vy);
      if (sp > cap) {
        vx *= cap / sp;
        vy *= cap / sp;
      }
      return { vx: vx, vy: vy };
    }

    function drawRoute() {}

    function fadeRoute() {
      if (svg) svg.classList.add("is-gone");
    }

    function enableDrag() {
      enterDone = true;
      phase = "idle";
      swayOrigin = last || performance.now();
      ball.classList.add("is-draggable");
      ball.setAttribute("aria-label", "拖动鸡蛋，松手可甩出");
    }

    function finishEnter() {
      if (enterDone) return;
      fadeRoute();
      enableDrag();
    }

    function paint(now) {
      var lift = Math.max(0, state.y - wld.r);
      var air = Math.min(1, lift / 140);
      var sq = Math.max(0, squash);
      var stretch = lift > 18 && state.vy > 40 ? Math.min(0.16, lift / 900) : 0;
      var lean = 0;
      if (phase === "idle" && !dragging && !reduce) {
        lean = Math.sin((((now || 0) - swayOrigin) / swayMs) * Math.PI * 2) * swayAmp;
      }
      ball.style.transform = "translate3d(" + (state.x - wld.rx) + "px,0,0)";
      body.style.transform =
        "translate3d(0," +
        -lift +
        "px,0) rotate(" +
        lean +
        "deg) scale(" +
        (1 + sq * 0.9 - stretch * 0.45) +
        "," +
        (1 - sq * 0.72 + stretch) +
        ")";
      if (shadow) {
        shadow.style.transform =
          "scale(" + (1.12 + sq * 0.55 - air * 0.55) + "," + (1 - air * 0.35) + ")";
        shadow.style.opacity = String(0.58 - air * 0.38);
      }
    }

    function onDown(e) {
      if (!enterDone || e.button === 2) return;
      e.preventDefault();
      dragging = true;
      phase = "drag";
      ball.classList.add("is-dragging");
      try {
        ball.setPointerCapture(e.pointerId);
      } catch (err) {}
      var p = pointerPhys(e);
      grabDX = state.x - p.x;
      grabDY = state.y - p.y;
      hist = [];
      recordHist(state.x, state.y, e.timeStamp);
    }

    function onMove(e) {
      if (!dragging) return;
      e.preventDefault();
      var p = pointerPhys(e);
      state.x = Math.max(wld.rx, Math.min(wld.w - wld.rx, p.x + grabDX));
      state.y = Math.max(wld.r, p.y + grabDY);
      state.vx = 0;
      state.vy = 0;
      recordHist(state.x, state.y, e.timeStamp);
      paint(e.timeStamp);
    }

    function onUp(e) {
      if (!dragging) return;
      dragging = false;
      ball.classList.remove("is-dragging");
      recordHist(state.x, state.y, e.timeStamp);
      var v = flickVel();
      state.vx = v.vx;
      state.vy = v.vy;
      phase = "throw";
      hist = [];
    }

    ball.addEventListener("pointerdown", onDown);
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
    window.addEventListener("pointercancel", onUp);

    function frame(now) {
      var cur = world();
      if (wld) {
        wld.left = cur.left;
        wld.top = cur.top;
        wld.bottom = cur.bottom;
      }
      if (wld && (Math.abs(cur.w - wld.w) > 2 || Math.abs(cur.h - wld.h) > 2)) {
        var ratio = wld.w ? state.x / wld.w : 1;
        wld = cur;
        state.x = Math.max(wld.rx, Math.min(wld.w - wld.rx, ratio * wld.w));
        if (!enterDone) {
          buildEnterPath();
          if (phase === "wait") state = seedEnter();
          drawRoute();
        }
      }

      acc += Math.min(0.032, (now - last) / 1000);
      last = now;

      if (phase === "wait") {
        if (now - launchedAt >= enterDelay) {
          phase = "enter";
          segK = -1;
          segT = 0;
          state.vx = 0;
          state.vy = 0;
        }
      } else if (phase === "enter") {
        while (acc >= dt) {
          advanceEnter(dt);
          acc -= dt;
        }
        if (!enterDone && now - launchedAt > enterDelay + 5200) {
          state.x = plan.xEnd;
          state.y = wld.r;
          state.vx = 0;
          state.vy = 0;
          finishEnter();
        }
      } else if (phase === "throw") {
        while (acc >= dt) {
          step(state, dt, true);
          acc -= dt;
        }
        if (settled(state)) {
          state.vx = 0;
          state.vy = 0;
          state.y = wld.r;
          phase = "idle";
          swayOrigin = now;
        }
      } else if (phase === "idle" && !dragging) {
        recoverSquash(dt);
        acc = 0;
      } else {
        acc = 0;
      }

      paint(now);
      requestAnimationFrame(frame);
    }

    function start() {
      wld = world();
      if (wld.w < 40 || wld.h < 40) {
        requestAnimationFrame(start);
        return;
      }
      if (reduce) {
        state = seedRight();
        svg.classList.add("is-gone");
        ball.classList.add("is-calm");
        paint(0);
        enableDrag();
        last = performance.now();
        requestAnimationFrame(frame);
        return;
      }
      buildEnterPath();
      state = seedEnter();
      drawRoute();
      paint(0);
      launchedAt = performance.now();
      last = launchedAt;
      requestAnimationFrame(frame);
    }

    requestAnimationFrame(start);
  })();

  var rail = document.querySelector("[data-rail]");
  if (!rail) return;
  document.querySelectorAll("[data-rail-dir]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var dir = btn.getAttribute("data-rail-dir") === "next" ? 1 : -1;
      rail.scrollBy({ left: dir * 320, behavior: "smooth" });
    });
  });
})();
