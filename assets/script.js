
// Mobile nav toggle
const btn = document.querySelector('.nav-toggle');
const nav = document.getElementById('nav');
if (btn && nav) {
  btn.addEventListener('click', () => {
    const open = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!open));
    nav.classList.toggle('show');
  });
}
// Active link highlight
const here = location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.nav a').forEach(a => {
  const file = a.getAttribute('href').split('/').pop();
  if (file === here) a.classList.add('active');
});
// Year
document.getElementById('year').textContent = new Date().getFullYear();
