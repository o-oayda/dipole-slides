(() => {
  const slideSelector = ".fragment-background-zoom";
  const backgroundSelector = ".reveal .backgrounds .slide-background";
  const activeClass = "fragment-background-zoomed";

  function configuredNumber(slide, name, fallback) {
    const value = Number(slide?.dataset?.[name]);
    return Number.isFinite(value) ? value : fallback;
  }

  function currentFragmentStep(slide) {
    const visibleFragments = [...slide.querySelectorAll(".fragment.visible")];
    if (!visibleFragments.length) return -1;

    const indexedSteps = visibleFragments
      .map((fragment) => Number(fragment.dataset.fragmentIndex))
      .filter(Number.isFinite);

    if (indexedSteps.length) return Math.max(...indexedSteps);
    return visibleFragments.length - 1;
  }

  function slideBackground(slide) {
    return (
      window.Reveal?.getSlideBackground?.(slide) ??
      document.querySelector(`${backgroundSelector}.present`)
    );
  }

  function resetBackground(background) {
    background.classList.remove(activeClass);
    background.style.removeProperty("--fragment-background-zoom-scale");
    background.style.removeProperty("--fragment-background-zoom-duration");
    background.style.removeProperty("--fragment-background-zoom-origin");
  }

  function updateFragmentBackgroundZoom() {
    if (!window.Reveal) return;

    const slide = window.Reveal.getCurrentSlide?.();
    const background = slide?.matches?.(slideSelector) ? slideBackground(slide) : null;

    document.querySelectorAll(backgroundSelector).forEach((candidate) => {
      if (candidate !== background) resetBackground(candidate);
    });

    if (!background) return;

    const triggerStep = configuredNumber(slide, "backgroundZoomFragment", 1);
    const scale = configuredNumber(slide, "backgroundZoomScale", 1.15);
    const duration = configuredNumber(slide, "backgroundZoomDuration", 2000);
    const origin = slide.dataset.backgroundZoomOrigin ?? "50% 50%";

    background.style.setProperty("--fragment-background-zoom-scale", scale);
    background.style.setProperty("--fragment-background-zoom-duration", `${duration}ms`);
    background.style.setProperty("--fragment-background-zoom-origin", origin);
    background.classList.toggle(activeClass, currentFragmentStep(slide) >= triggerStep);
  }

  function installFragmentBackgroundZoom() {
    updateFragmentBackgroundZoom();
    window.Reveal?.on?.("ready", updateFragmentBackgroundZoom);
    window.Reveal?.on?.("slidechanged", updateFragmentBackgroundZoom);
    window.Reveal?.on?.("fragmentshown", updateFragmentBackgroundZoom);
    window.Reveal?.on?.("fragmenthidden", updateFragmentBackgroundZoom);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", installFragmentBackgroundZoom);
  } else {
    installFragmentBackgroundZoom();
  }
})();
