(() => {
  const DEFAULT_DURATION_MS = 450;
  const MIN_TICK_MS = 16;
  let activeAnimation = null;

  function getNoiseSlider() {
    return document.querySelector(".eddington-noise-slider");
  }

  function notifySlider(slider) {
    slider.dispatchEvent(new Event("input", { bubbles: true }));
  }

  function roundedStepValue(value, step) {
    return Math.round(value / step) * step;
  }

  function animationDuration(fragment) {
    const configuredDuration =
      fragment?.dataset?.eddingtonDuration ??
      fragment?.closest?.(".eddington-noise-steps")?.dataset?.eddingtonDuration;
    return Number(configuredDuration) || DEFAULT_DURATION_MS;
  }

  function animateNoiseSlider(targetValue, duration = DEFAULT_DURATION_MS) {
    const slider = getNoiseSlider();
    if (!slider) return;

    if (activeAnimation !== null) {
      window.clearInterval(activeAnimation);
      activeAnimation = null;
    }

    const step = Number(slider.step) || 0.05;
    const target = roundedStepValue(Number(targetValue), step);
    const start = roundedStepValue(slider.valueAsNumber, step);
    const direction = Math.sign(target - start);
    const tickCount = Math.max(1, Math.round(Math.abs(target - start) / step));
    const tickMs = Math.max(MIN_TICK_MS, duration / tickCount);

    if (direction === 0) {
      slider.value = target.toFixed(2);
      notifySlider(slider);
      return;
    }

    let current = start;
    activeAnimation = window.setInterval(() => {
      current = roundedStepValue(current + direction * step, step);

      if ((direction > 0 && current >= target) || (direction < 0 && current <= target)) {
        current = target;
        window.clearInterval(activeAnimation);
        activeAnimation = null;
      }

      slider.value = current.toFixed(2);
      notifySlider(slider);
    }, tickMs);
  }

  function previousNoiseValue(fragment) {
    let previous = fragment.previousElementSibling;
    while (previous) {
      if (previous.dataset?.eddingtonNoise !== undefined) {
        return previous.dataset.eddingtonNoise;
      }
      previous = previous.previousElementSibling;
    }
    return "0";
  }

  function syncNoiseToCurrentFragment() {
    const visibleSteps = [
      ...document.querySelectorAll(".eddington-noise-steps .fragment.visible[data-eddington-noise]")
    ];
    const fragment = visibleSteps.at(-1);
    const value = fragment?.dataset.eddingtonNoise ?? "0";
    animateNoiseSlider(value, animationDuration(fragment));
  }

  function installEddingtonFragmentControls() {
    if (!window.Reveal?.on) {
      window.setTimeout(installEddingtonFragmentControls, 50);
      return;
    }

    window.Reveal.on("fragmentshown", (event) => {
      const value = event.fragment.dataset.eddingtonNoise;
      if (value !== undefined) animateNoiseSlider(value, animationDuration(event.fragment));
    });

    window.Reveal.on("fragmenthidden", (event) => {
      if (event.fragment.dataset.eddingtonNoise !== undefined) {
        animateNoiseSlider(previousNoiseValue(event.fragment), animationDuration(event.fragment));
      }
    });

    window.Reveal.on("slidechanged", syncNoiseToCurrentFragment);
    window.Reveal.on("ready", syncNoiseToCurrentFragment);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", installEddingtonFragmentControls);
  } else {
    installEddingtonFragmentControls();
  }
})();
