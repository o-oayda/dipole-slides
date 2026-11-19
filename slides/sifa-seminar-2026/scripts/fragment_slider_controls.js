(() => {
  const DEFAULT_DURATION_MS = 450;
  const activeAnimations = new Map();

  function getSlider(steps) {
    return steps.closest("section").querySelector(steps.dataset.sliderSelector);
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

    cancelAnimationFrame(activeAnimations.get(slider));
    activeAnimations.delete(slider);

    const step = Number(slider.step) || 0.01;
    const target = roundedStepValue(Number(targetValue), step);
    const start = slider.valueAsNumber;
    const duration = animationDuration(steps);
    const started = performance.now();

    // Manual dragging takes over immediately from a preset animation.
    if (!slider.dataset.animationControlsInstalled) {
      slider.addEventListener("pointerdown", () => {
        cancelAnimationFrame(activeAnimations.get(slider));
        activeAnimations.delete(slider);
      });
      slider.addEventListener("keydown", () => {
        cancelAnimationFrame(activeAnimations.get(slider));
        activeAnimations.delete(slider);
      });
      slider.dataset.animationControlsInstalled = "true";
    }

    function tick(now) {
      const progress = Math.min(1, (now - started) / duration);
      const eased = progress * progress * (3 - 2 * progress);
      slider.value = String(progress === 1 ? target :
        roundedStepValue(start + (target - start) * eased, step));
      notifySlider(slider);
      if (progress < 1) {
        activeAnimations.set(slider, requestAnimationFrame(tick));
      } else {
        activeAnimations.delete(slider);
      }
    }
    activeAnimations.set(slider, requestAnimationFrame(tick));
  }

  function previousValue(fragment) {
    let previous = fragment.previousElementSibling;
    while (previous) {
      if (previous.dataset?.sliderValue !== undefined) return previous.dataset.sliderValue;
      previous = previous.previousElementSibling;
    }
    const steps = fragment.closest(".fragment-slider-steps");
    return steps ? (steps.dataset.sliderInitialValue ?? getSlider(steps)?.min ?? "0") : "0";
  }

  function syncSlidersToCurrentFragments() {
    window.Reveal.getCurrentSlide()?.querySelectorAll(".fragment-slider-steps").forEach((steps) => {
      if (steps.hasAttribute("data-slider-preserve-state")) return;
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
        if (steps.hasAttribute("data-slider-capture-initial") &&
            event.fragment === steps.querySelector("[data-slider-value]")) {
          steps.dataset.sliderInitialValue = String(getSlider(steps).valueAsNumber);
        }
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
