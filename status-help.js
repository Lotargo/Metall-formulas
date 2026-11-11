/* Native popovers provide light dismissal and Escape; hover also supports focus. */
(() => {
  const buttons = [...document.querySelectorAll('button[data-status-help]')];
  const tips = [...document.querySelectorAll('.status-tooltip')];
  if (typeof HTMLElement.prototype.showPopover !== 'function') {
    buttons.forEach(button => { button.title = document.getElementById(button.getAttribute('popovertarget')).textContent; });
    return;
  }
  const anchors = new Map();
  let activeTip = null, activeTrigger = null, pinnedTip = null;
  let hoveredTrigger = null, hoveredTip = null, opening = null, closing = null;
  const cancelTimers = () => { clearTimeout(opening); clearTimeout(closing); };
  const tipFor = button => document.getElementById(button.getAttribute('popovertarget'));

  function position(tip, trigger) {
    if (!trigger?.isConnected || !tip.matches(':popover-open')) return;
    const rect = trigger.getBoundingClientRect();
    const popup = tip.getBoundingClientRect();
    const headerBottom = document.querySelector('.topbar').getBoundingClientRect().bottom;
    const minimumTop = headerBottom + popup.height + 24 < innerHeight ? headerBottom + 8 : 12;
    const left = Math.max(12, Math.min(rect.left, innerWidth-popup.width-12));
    let top = rect.bottom + 8;
    if (top + popup.height > innerHeight-12) top = rect.top-popup.height-8;
    top = Math.max(minimumTop, Math.min(top, innerHeight-popup.height-12));
    tip.style.left = `${Math.round(left)}px`;
    tip.style.top = `${Math.round(top)}px`;
  }
  function show(button) {
    cancelTimers();
    if (button.closest('[hidden]')) return;
    const tip = tipFor(button);
    anchors.set(tip.id, button);
    if (!tip.matches(':popover-open')) tip.showPopover();
    else position(tip, button);
  }
  function dismiss() {
    cancelTimers();
    if (activeTip?.matches(':popover-open')) activeTip.hidePopover();
  }
  function scheduleDismiss() {
    clearTimeout(closing);
    closing = setTimeout(() => {
      if (activeTip && activeTip!==pinnedTip && hoveredTrigger!==activeTrigger
        && hoveredTip!==activeTip && !activeTrigger?.matches(':focus-visible')) dismiss();
    }, 180);
  }
  tips.forEach(tip => {
    tip.addEventListener('beforetoggle', event => {
      if (event.newState === 'open') {
        activeTip = tip;
        activeTrigger = anchors.get(tip.id);
      } else {
        if (activeTip===tip) { activeTip=null; activeTrigger=null; }
        if (pinnedTip===tip) pinnedTip=null;
      }
    });
    tip.addEventListener('toggle', event => {
      if (event.newState === 'open') position(tip, anchors.get(tip.id));
    });
  });
  document.addEventListener('pointerover', event => {
    if (event.pointerType!=='mouse') return;
    const button = event.target.closest?.('button[data-status-help]');
    const tip = event.target.closest?.('.status-tooltip');
    if (button && !button.contains(event.relatedTarget)) {
      cancelTimers();
      hoveredTrigger=button;
      opening=setTimeout(() => show(button), 120);
    }
    if (tip) { hoveredTip=tip; clearTimeout(closing); }
  });
  document.addEventListener('pointerout', event => {
    if (event.pointerType!=='mouse') return;
    const button=event.target.closest?.('button[data-status-help]');
    const tip=event.target.closest?.('.status-tooltip');
    if (button && !button.contains(event.relatedTarget)) {
      clearTimeout(opening); hoveredTrigger=null; scheduleDismiss();
    }
    if (tip && !tip.contains(event.relatedTarget)) { hoveredTip=null; scheduleDismiss(); }
  });
  document.addEventListener('focusin', event => {
    const button=event.target.closest?.('button[data-status-help]');
    if (button?.matches(':focus-visible')) show(button);
  });
  document.addEventListener('focusout', event => {
    if (event.target.closest?.('button[data-status-help]')) scheduleDismiss();
  });
  document.addEventListener('click', event => {
    const button=event.target.closest?.('button[data-status-help]');
    if (!button) return;
    cancelTimers();
    const tip=tipFor(button);
    anchors.set(tip.id, button);
    pinnedTip=tip.matches(':popover-open') ? null : tip;
  }, true);
  document.addEventListener('scroll', event => {
    if (event.target instanceof Element && event.target.closest('.status-tooltip')) return;
    dismiss();
  }, { capture:true, passive:true });
  window.addEventListener('resize', dismiss);
})();
