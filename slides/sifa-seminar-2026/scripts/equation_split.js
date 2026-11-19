(() => {
  const running = new Map();
  function setSplit(slide, split, animate = true) {
    const box = slide?.querySelector('.dipole-decomposition');
    if (!box) return;
    const source = box.querySelector('.split-equation-source');
    const targets = box.querySelector('.split-equation-targets');
    // Bodies and betas move independently. Both betas start at the same
    // original beta outside the bracket, with no opacity change.
    const pairs = ['aberration', 'flux'].flatMap(name => [
      {from: box.querySelector(`.split-source-${name}`),
       to: box.querySelector(`.split-target-${name} .split-body`)},
      {from: box.querySelector('.split-source-beta'),
       to: box.querySelector(`.split-target-${name} .split-beta`)}
    ]).concat(['lhs', 'plus'].map(name => ({
      from: box.querySelector(`.split-source-${name}`),
      to: box.querySelector(`.split-target-${name}`)
    })));
    const active = running.get(box);
    if (active) active.forEach(a => a.cancel());
    running.delete(box);
    source.setAttribute('aria-hidden', String(split));
    targets.setAttribute('aria-hidden', String(!split));
    if (!animate) {
      box.classList.toggle('is-split', split);
      return;
    }
    box.classList.add('is-split');
    const scale = window.Reveal.getScale();
    const duration = Number(slide.querySelector('.equation-split-trigger').dataset.splitDuration);
    const animations = pairs.map(({from, to}) => {
      const a = from.getBoundingClientRect(), b = to.getBoundingClientRect();
      const offset = `translate(${(a.left-b.left)/scale}px, ${(a.top-b.top)/scale}px)`;
      return to.animate(split ? [{transform: offset}, {transform: 'none'}] :
        [{transform: 'none'}, {transform: offset}],
        {duration, easing: 'ease-in-out', fill: 'both'});
    });
    running.set(box, animations);
    Promise.all(animations.map(a => a.finished)).then(() => {
      if (running.get(box) !== animations) return;
      box.classList.toggle('is-split', split);
      animations.forEach(a => a.cancel());
      running.delete(box);
    }).catch(() => {}); // Reversing navigation cancels the preceding movement.
  }
  function sync() {
    const slide = window.Reveal.getCurrentSlide();
    setSplit(slide, !!slide?.querySelector('.equation-split-trigger.visible'), false);
  }
  function install() {
    if (!window.Reveal?.on) return;
    Reveal.on('fragmentshown', e => {
      if (e.fragment.matches('.equation-split-trigger')) setSplit(e.fragment.closest('section'), true);
    });
    Reveal.on('fragmenthidden', e => {
      if (e.fragment.matches('.equation-split-trigger')) setSplit(e.fragment.closest('section'), false);
    });
    Reveal.on('slidechanged', sync);
    Reveal.on('resize', sync);
    sync();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install);
  else install();
})();
