(() => {
  const DEFAULT_DURATION_MS = 450;
  const MIN_TICK_MS = 16;
  const activeAnimations = new Map();

  function getSlider(steps) {
    return document.querySelector(steps.dataset.sliderSelector);
  }

  function notifySlider(slider) {
    slider.dispatchEvent(new Event("input", { bubbles: true }));
  }

  function roundedStepValue(value, step) {
    return Math.round(value / step) * step;
  }

  function animationDuration(steps) {
    return Number(steps.dataset.sliderDuration) || DEFAULT_DURATION_MS;
  }

  function animateSlider(steps, targetValue) {
    const slider = getSlider(steps);
    if (!slider) return;

    const activeAnimation = activeAnimations.get(slider);
    if (activeAnimation !== undefined) {
      window.clearInterval(activeAnimation);
      activeAnimations.delete(slider);
    }

    const step = Number(slider.step) || 0.01;
    const target = roundedStepValue(Number(targetValue), step);
    const start = roundedStepValue(slider.valueAsNumber, step);
    const direction = Math.sign(target - start);
    const tickCount = Math.max(1, Math.round(Math.abs(target - start) / step));
    const tickMs = Math.max(MIN_TICK_MS, animationDuration(steps) / tickCount);

    if (direction === 0) {
      slider.value = String(target);
      notifySlider(slider);
      return;
    }

    let current = start;
    const animation = window.setInterval(() => {
      current = roundedStepValue(current + direction * step, step);

      if ((direction > 0 && current >= target) || (direction < 0 && current <= target)) {
        current = target;
        window.clearInterval(animation);
        activeAnimations.delete(slider);
      }

      slider.value = String(current);
      notifySlider(slider);
    }, tickMs);
    activeAnimations.set(slider, animation);
  }

  function previousValue(fragment) {
    let previous = fragment.previousElementSibling;
    while (previous) {
      if (previous.dataset?.sliderValue !== undefined) return previous.dataset.sliderValue;
      previous = previous.previousElementSibling;
    }
    const steps = fragment.closest(".fragment-slider-steps");
    return steps ? (getSlider(steps)?.min ?? "0") : "0";
  }

  function syncSlidersToCurrentFragments() {
    document.querySelectorAll(".fragment-slider-steps").forEach((steps) => {
      const visibleSteps = steps.querySelectorAll(".fragment.visible[data-slider-value]");
      const value = visibleSteps.item(visibleSteps.length - 1)?.dataset.sliderValue ?? "0";
      animateSlider(steps, value);
    });
  }

  function installFragmentSliderControls() {
    if (!window.Reveal?.on) {
      window.setTimeout(installFragmentSliderControls, 50);
      return;
    }

    window.Reveal.on("fragmentshown", (event) => {
      const steps = event.fragment.closest(".fragment-slider-steps");
      if (steps && event.fragment.dataset.sliderValue !== undefined) {
        animateSlider(steps, event.fragment.dataset.sliderValue);
      }
    });

    window.Reveal.on("fragmenthidden", (event) => {
      const steps = event.fragment.closest(".fragment-slider-steps");
      if (steps && event.fragment.dataset.sliderValue !== undefined) {
        animateSlider(steps, previousValue(event.fragment));
      }
    });

    window.Reveal.on("slidechanged", syncSlidersToCurrentFragments);
    window.Reveal.on("ready", syncSlidersToCurrentFragments);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", installFragmentSliderControls);
  } else {
    installFragmentSliderControls();
  }
})();
