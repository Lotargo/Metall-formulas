const data = JSON.parse(document.getElementById('search-data').textContent);
const search = document.getElementById('search');
const status = document.getElementById('status');
const clearSearch = document.getElementById('search-clear');
const norm = value => value.normalize('NFKC').toLocaleLowerCase('ru');
const searchable = new Map(data.map(entry => [entry.id, norm(entry.text)]));

function filter() {
  let count = 0;
  const words = norm(search.value.trim()).split(/\s+/).filter(Boolean);
  document.querySelectorAll('.entry').forEach(element => {
    const visible = (status.value === 'all' || element.dataset.status === status.value)
      && words.every(word => searchable.get(element.id).includes(word));
    element.hidden = !visible;
    if (visible) count++;
  });
  const sectionCounts = new Map();
  document.querySelectorAll('.provenance-group, .chapter').forEach(section => {
    const visibleCount = section.querySelectorAll('.entry:not([hidden])').length;
    section.hidden = visibleCount === 0;
    if (section.classList.contains('chapter')) sectionCounts.set(section.id, visibleCount);
  });
  document.getElementById('empty').hidden = count > 0;
  const filtered = Boolean(search.value) || status.value !== 'all';
  document.getElementById('result-count').textContent = filtered ? `${count} из ${data.length} статей` : `${count} статей`;
  document.querySelector('.topbar').classList.toggle('is-filtered', filtered);
  document.querySelector('.header-search').classList.toggle('has-value', Boolean(search.value));
  clearSearch.hidden = !search.value;
  document.querySelectorAll('#booknav a[data-section] .count').forEach(badge => {
    const value = sectionCounts.get(badge.closest('a').dataset.section) || 0;
    badge.textContent = value;
    badge.setAttribute('aria-label', `Статей в разделе: ${value}`);
  });
  document.getElementById('start').hidden = filtered;
}
search.addEventListener('input', filter);
status.addEventListener('change', filter);
clearSearch.addEventListener('click', () => { search.value = ''; filter(); search.focus(); });
search.addEventListener('keydown', event => {
  if (event.key === 'Escape' && search.value) { event.preventDefault(); search.value = ''; filter(); }
});
document.getElementById('reset').addEventListener('click', () => {
  search.value = '';
  status.value = 'all';
  filter();
  search.focus();
});
document.getElementById('print').addEventListener('click', () => window.print());

const navigation = document.getElementById('booknav');
const navToggle = document.getElementById('nav-toggle');
const navDialog = document.getElementById('nav-dialog');
const navigationHome = document.createComment('Navigation desktop position');
navigation.before(navigationHome);
const mobileNavigation = matchMedia('(max-width: 900px)');
function closeNavigation() {
  if (navDialog.open) navDialog.close();
  navToggle.setAttribute('aria-expanded', 'false');
}
function placeNavigation() {
  closeNavigation();
  if (mobileNavigation.matches) navDialog.append(navigation);
  else navigationHome.after(navigation);
}
mobileNavigation.addEventListener('change', placeNavigation);
placeNavigation();
navToggle.addEventListener('click', () => {
  if (!mobileNavigation.matches) return;
  navDialog.showModal();
  navToggle.setAttribute('aria-expanded', 'true');
});
document.getElementById('nav-close').addEventListener('click', closeNavigation);
navDialog.addEventListener('close', () => navToggle.setAttribute('aria-expanded', 'false'));
navDialog.addEventListener('click', event => {
  const bounds = navDialog.getBoundingClientRect();
  if (event.target === navDialog && (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom)) closeNavigation();
});
document.addEventListener('keydown', event => {
  if ((event.ctrlKey || event.metaKey) && !event.altKey && event.key.toLowerCase() === 'k') {
    event.preventDefault();
    closeNavigation();
    search.focus();
    search.select();
  }
});
const navLinks = [...navigation.querySelectorAll('a[data-section]')];
function selectChapter(id) {
  navLinks.forEach(link => {
    if (link.dataset.section === id) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
}
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', () => {
    search.value = '';
    status.value = 'all';
    filter();
    closeNavigation();
    const id = anchor.getAttribute('href').slice(1);
    const target = document.getElementById(id);
    if (target) selectChapter(target.closest('.chapter')?.id || id);
  });
});
function hashTarget() {
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  if (id === 'origins' || id.startsWith('origin-')) {
    history.replaceState(null, '', '#start');
    id = 'start';
  }
  const target = document.getElementById(id);
  if (target && (target.classList.contains('entry') || target.classList.contains('chapter') || ['start','coverage'].includes(id))) {
    search.value = '';
    status.value = 'all';
    filter();
    requestAnimationFrame(() => target.scrollIntoView());
  }
}
window.addEventListener('hashchange', hashTarget);
const header = document.querySelector('.topbar');
let chapterObserver;
const watchedSections = navLinks.map(link => document.getElementById(link.dataset.section)).filter(Boolean);
const visibleSections = new Set();
function updateHeaderHeight() {
  const height = Math.ceil(header.getBoundingClientRect().height);
  document.documentElement.style.setProperty('--bar-height', `${height}px`);
  chapterObserver?.disconnect();
  visibleSections.clear();
  chapterObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => entry.isIntersecting ? visibleSections.add(entry.target) : visibleSections.delete(entry.target));
    const current = watchedSections.filter(section => visibleSections.has(section) && !section.hidden).at(-1);
    if (current) selectChapter(current.id);
  }, { rootMargin: `-${height}px 0px -${Math.max(0, innerHeight-height-180)}px 0px`, threshold: 0 });
  watchedSections.forEach(section => chapterObserver.observe(section));
}
new ResizeObserver(updateHeaderHeight).observe(header);
window.addEventListener('resize', updateHeaderHeight);
new IntersectionObserver(([entry]) => header.classList.toggle('is-scrolled', !entry.isIntersecting)).observe(document.getElementById('header-sentinel'));
updateHeaderHeight();


const number = value => value.toLocaleString('ru-RU', { maximumFractionDigits: 4 });
function example() {
  const inputs = ['ex-d', 'ex-r', 'ex-k'].map(id => document.getElementById(id));
  const [diameter, rate, kerf] = inputs.map(input => Number(input.value));
  const valid = inputs.every(input => input.value !== '' && input.validity.valid
    && Number.isFinite(Number(input.value)) && Number(input.value) > 0);
  inputs.forEach(input => input.setAttribute('aria-invalid', String(!input.validity.valid || input.value === '')));
  if (!valid) {
    document.getElementById('ex-error').textContent = 'Введите положительные значения в указанных диапазонах.';
    document.getElementById('example-time').textContent = '';
    document.getElementById('example-steps').textContent = '';
    document.getElementById('example-volume').textContent = '';
    return;
  }
  document.getElementById('ex-error').textContent = '';
  const area = Math.PI * diameter * diameter / 4;
  const time = area / 100 / rate;
  document.getElementById('example-steps').textContent = `A = πD²/4 = ${number(area)} мм² → ${number(area / 100)} см²`;
  document.getElementById('example-time').textContent = `t = A/(100R) = ${number(time)} мин`;
  document.getElementById('example-volume').textContent = `Объём пропила A·k = ${number(area * kerf)} мм³. Производительность пропила R·k/10 = ${number(rate * kerf / 10)} см³/мин.`;
}
document.querySelectorAll('.example input').forEach(input => input.addEventListener('input', example));
filter();
example();
hashTarget();
