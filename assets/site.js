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

  var egg = document.querySelector("[data-egg]");
  if (egg) {
    egg.addEventListener("click", function () {
      egg.classList.remove("is-boing");
      void egg.offsetWidth;
      egg.classList.add("is-boing");
    });
    egg.addEventListener("animationend", function (e) {
      if (e.animationName === "egg-boing") egg.classList.remove("is-boing");
    });
  }

  var rail = document.querySelector("[data-rail]");
  if (!rail) return;
  document.querySelectorAll("[data-rail-dir]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var dir = btn.getAttribute("data-rail-dir") === "next" ? 1 : -1;
      rail.scrollBy({ left: dir * 320, behavior: "smooth" });
    });
  });
})();
