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

// Evidenzia link attivo
const here = location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.nav a').forEach(a => {
  const file = a.getAttribute('href').split('/').pop();
  if (file === here) a.classList.add('active');
});

// Anno footer
const y = document.getElementById('year');
if (y) y.textContent = new Date().getFullYear();

// Gestione consenso Google Analytics
(function(){
  const storageKey = 'beholderlab_cookie_consent';
  let consent = null;
  try {
    consent = localStorage.getItem(storageKey);
  } catch (_) {}

  function setConsent(choice) {
    const granted = choice === 'granted';
    if (typeof gtag === 'function') {
      gtag('consent', 'update', {
        ad_storage: 'denied',
        ad_user_data: 'denied',
        ad_personalization: 'denied',
        analytics_storage: granted ? 'granted' : 'denied'
      });
    }
    try {
      localStorage.setItem(storageKey, choice);
    } catch (_) {}
  }

  if (consent === 'granted' || consent === 'denied') {
    setConsent(consent);
  }

  const banner = document.createElement('div');
  banner.className = 'cookie-banner';
  banner.setAttribute('role', 'dialog');
  banner.setAttribute('aria-label', 'Preferenze cookie');
  banner.innerHTML = `
    <div class="cookie-banner-copy">
      <strong>Cookie e privacy</strong>
      <p>Usiamo Google Analytics per statistiche aggregate sulle visite. Puoi accettare o rifiutare i cookie di analisi.</p>
    </div>
    <div class="cookie-banner-actions">
      <button type="button" class="cookie-btn cookie-btn-secondary" data-consent="denied">Rifiuta</button>
      <button type="button" class="cookie-btn cookie-btn-primary" data-consent="granted">Accetta</button>
    </div>
  `;

  const manageButton = document.createElement('button');
  manageButton.type = 'button';
  manageButton.className = 'cookie-manage';
  manageButton.textContent = 'Cookie';
  manageButton.setAttribute('aria-label', 'Gestisci le preferenze cookie');

  function closeBanner() {
    banner.remove();
    manageButton.hidden = false;
  }

  banner.addEventListener('click', (event) => {
    const button = event.target.closest('[data-consent]');
    if (!button) return;
    setConsent(button.dataset.consent);
    closeBanner();
  });

  manageButton.addEventListener('click', () => {
    if (document.body.contains(banner)) {
      banner.remove();
      manageButton.hidden = false;
    } else {
      document.body.appendChild(banner);
      manageButton.hidden = true;
    }
  });

  document.body.appendChild(manageButton);
  if (!consent) {
    document.body.appendChild(banner);
    manageButton.hidden = true;
  }
})();

// --- Neural particles (light density, moderate speed) ---
(function(){
  const canvas = document.getElementById('neural-bg');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let w, h, dpi = window.devicePixelRatio || 1;
  const N = 34;          // densità leggera
  const SPEED = 0.35;    // velocità moderata
  const RANGE = 140;     // distanza di collegamento
  let nodes = [];

  function resize(){
    w = canvas.clientWidth; h = canvas.clientHeight;
    canvas.width = Math.floor(w * dpi); canvas.height = Math.floor(h * dpi);
    ctx.setTransform(dpi,0,0,dpi,0,0);
  }
  window.addEventListener('resize', resize, {passive:true});
  resize();

  function init(){
    nodes = [];
    for (let i=0;i<N;i++){
      nodes.push({
        x: Math.random()*w,
        y: Math.random()*h,
        vx: (Math.random()*2-1)*SPEED,
        vy: (Math.random()*2-1)*SPEED,
        r: 1.6 + Math.random()*1.6
      });
    }
  }
  init();

  function step(){
    ctx.clearRect(0,0,w,h);

    // collegamenti
    for (let i=0;i<N;i++){
      for (let j=i+1;j<N;j++){
        const a = nodes[i], b = nodes[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const d = Math.hypot(dx,dy);
        if (d < RANGE){
          const alpha = 1 - d/RANGE;
          ctx.strokeStyle = `rgba(0, 212, 255, ${alpha*0.13})`;
          ctx.lineWidth = 1;
          ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
        }
      }
    }

    // particelle
    for (const p of nodes){
      p.x += p.vx; p.y += p.vy;
      if (p.x<0||p.x>w) p.vx *= -1;
      if (p.y<0||p.y>h) p.vy *= -1;

      const g = ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.r*2.2);
      g.addColorStop(0,'rgba(0,212,255,0.9)');    // turchese
      g.addColorStop(1,'rgba(181,109,255,0.85)'); // viola
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2); ctx.fill();
    }

    requestAnimationFrame(step);
  }

  // avvia il loop
  step();
})();
