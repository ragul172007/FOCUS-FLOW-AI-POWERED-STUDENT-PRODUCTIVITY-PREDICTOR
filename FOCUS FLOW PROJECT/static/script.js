/* =========================================================
   FOCUS FLOW AI — SCRIPT
   Handles entrance animations, confidence gauge, counters,
   button ripple/loading state, and stat bar fills.
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
  initFadeInReveal();
  initGauge();
  initStatCounters();
  initPredictButton();
});

/* ---------------------------------------------------------
   1. Fade-in-up reveal for cards/panels on load
   --------------------------------------------------------- */
function initFadeInReveal() {
  const elements = document.querySelectorAll("[data-animate]");

  if (!("IntersectionObserver" in window)) {
    elements.forEach((el) => el.classList.add("in-view"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );

  elements.forEach((el) => observer.observe(el));
}

/* ---------------------------------------------------------
   2. Animated circular confidence gauge
   --------------------------------------------------------- */
function initGauge() {
  const circle = document.getElementById("gauge-progress");
  const numberEl = document.getElementById("confidence-number");
  if (!circle || !numberEl) return;

  const radius = circle.r.baseVal.value;
  const circumference = 2 * Math.PI * radius;
  circle.style.strokeDasharray = `${circumference}`;
  circle.style.strokeDashoffset = `${circumference}`;

  let confidence = parseFloat(circle.dataset.confidence);
  if (Number.isNaN(confidence)) confidence = 0;
  confidence = Math.max(0, Math.min(100, confidence));

  // Color transitions from blue -> cyan as confidence rises
  const strokeColor = confidence >= 70 ? "#22e5ff" : confidence >= 40 ? "#4ea8ff" : "#ff5c7a";
  circle.style.stroke = strokeColor;

  // Delay slightly so the fade-in has already started
  window.setTimeout(() => {
    const offset = circumference - (confidence / 100) * circumference;
    circle.style.strokeDashoffset = `${offset}`;
    animateCount(numberEl, 0, Math.round(confidence), 1400);
  }, 350);
}

/* ---------------------------------------------------------
   3. Animate numeric counters + statistic bars
   --------------------------------------------------------- */
function initStatCounters() {
  const numberEls = document.querySelectorAll(".stat-item__number[data-count]");
  const barEls = document.querySelectorAll(".stat-item__bar-fill[data-bar]");

  numberEls.forEach((el, i) => {
    const target = parseFloat(el.dataset.count) || 0;
    window.setTimeout(() => {
      animateCount(el, 0, target, 1000);
    }, 200 + i * 150);
  });

  // Normalize bar widths against the largest value so they're visually comparable,
  // capped at 100% and given a sensible floor so small values are still visible.
  const values = Array.from(barEls).map((el) => parseFloat(el.dataset.bar) || 0);
  const maxValue = Math.max(...values, 1);

  barEls.forEach((el, i) => {
    const value = values[i];
    const pct = Math.max(6, Math.min(100, (value / maxValue) * 100));
    window.setTimeout(() => {
      el.style.width = `${pct}%`;
    }, 250 + i * 150);
  });
}

/* Generic requestAnimationFrame count-up helper */
function animateCount(el, from, to, duration) {
  const startTime = performance.now();

  function tick(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const value = Math.round(from + (to - from) * eased);
    el.textContent = value;

    if (progress < 1) {
      requestAnimationFrame(tick);
    } else {
      el.textContent = to;
    }
  }

  requestAnimationFrame(tick);
}

/* ---------------------------------------------------------
   4. Predict button: ripple effect + loading state
   --------------------------------------------------------- */
function initPredictButton() {
  const form = document.getElementById("predict-form");
  const button = document.getElementById("predict-btn");
  if (!form || !button) return;

  button.addEventListener("click", (event) => {
    spawnRipple(button, event);
  });

  form.addEventListener("submit", (event) => {
    // Basic client-side sanity check before showing the loading state
    const inputs = form.querySelectorAll(".field__input");
    let valid = true;

    inputs.forEach((input) => {
      if (input.value === "" || Number(input.value) < 0) {
        valid = false;
        input.style.borderColor = "#ff5c7a";
        window.setTimeout(() => {
          input.style.borderColor = "";
        }, 900);
      }
    });

    if (!valid) {
      event.preventDefault();
      return;
    }

    // Show a short loading animation, then let the native Flask form submit proceed
    event.preventDefault();
    button.classList.add("is-loading");
    button.disabled = true;

    window.setTimeout(() => {
      form.submit();
    }, 750);
  });
}

function spawnRipple(button, event) {
  const rect = button.getBoundingClientRect();
  const ripple = document.createElement("span");
  const size = Math.max(rect.width, rect.height);
  const x = (event.clientX || rect.left + rect.width / 2) - rect.left - size / 2;
  const y = (event.clientY || rect.top + rect.height / 2) - rect.top - size / 2;

  ripple.className = "ripple";
  ripple.style.width = `${size}px`;
  ripple.style.height = `${size}px`;
  ripple.style.left = `${x}px`;
  ripple.style.top = `${y}px`;

  button.appendChild(ripple);
  ripple.addEventListener("animationend", () => ripple.remove());
}
