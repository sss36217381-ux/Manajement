/* ====================================================
   SIGTEMBAKAU – Shared JavaScript Utilities
   ==================================================== */

const API = {
  base: '',
  async get(path) {
    const r = await fetch(this.base + path, { credentials: 'include' });
    if (!r.ok) throw new Error((await r.json()).detail || 'Error');
    return r.json();
  },
  async post(path, data, isForm = false) {
    const opts = { method: 'POST', credentials: 'include' };
    if (isForm) {
      opts.body = data;
    } else {
      opts.headers = { 'Content-Type': 'application/json' };
      opts.body = JSON.stringify(data);
    }
    const r = await fetch(this.base + path, opts);
    if (!r.ok) throw new Error((await r.json()).detail || 'Error');
    return r.json();
  },
  async patch(path, data) {
    const r = await fetch(this.base + path, {
      method: 'PATCH', credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!r.ok) throw new Error((await r.json()).detail || 'Error');
    return r.json();
  },
  async del(path) {
    const r = await fetch(this.base + path, { method: 'DELETE', credentials: 'include' });
    if (!r.ok) throw new Error((await r.json()).detail || 'Error');
    return r.json();
  }
};

/* ── Toast Notifications ─── */
function showToast(msg, type = 'success') {
  let tc = document.getElementById('toast-container');
  if (!tc) {
    tc = document.createElement('div');
    tc.id = 'toast-container';
    document.body.appendChild(tc);
  }
  const t = document.createElement('div');
  const icons = { success: '✅', error: '❌', warn: '⚠️', info: 'ℹ️' };
  t.className = `toast${type === 'error' ? ' toast-error' : type === 'warn' ? ' toast-warn' : ''}`;
  t.innerHTML = `<span>${icons[type] || '✅'}</span><span>${msg}</span>`;
  tc.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}

/* ── Loading Overlay ─── */
function showLoading(msg = 'Memuat data...') {
  let el = document.getElementById('loading-overlay');
  if (!el) {
    el = document.createElement('div');
    el.id = 'loading-overlay';
    el.className = 'loading-overlay';
    el.innerHTML = `<div class="spinner"></div><span></span>`;
    document.body.appendChild(el);
  }
  el.querySelector('span').textContent = msg;
  el.style.display = 'flex';
}
function hideLoading() {
  const el = document.getElementById('loading-overlay');
  if (el) el.style.display = 'none';
}

/* ── Auth Check ─── */
async function checkAuth(requiredRole = null) {
  try {
    const data = await API.get('/api/auth/me');
    if (!data.logged_in) {
      window.location.href = '/';
      return null;
    }
    if (requiredRole && !requiredRole.includes(data.user.role)) {
      showToast(`Akses ditolak. Role diperlukan: ${requiredRole}`, 'error');
      return null;
    }
    return data.user;
  } catch {
    window.location.href = '/';
    return null;
  }
}

/* ── Render Navbar User Info ─── */
function renderNavUser(user) {
  const el = document.getElementById('nav-user-name');
  const el2 = document.getElementById('nav-user-role');
  const el3 = document.getElementById('nav-user-avatar');
  if (el) el.textContent = user.nama.split(' ').slice(0, 2).join(' ');
  if (el2) el2.textContent = user.role.toUpperCase();
  if (el3) el3.textContent = user.nama.charAt(0).toUpperCase();
}

/* ── Format Helpers ─── */
function fmtRp(num) {
  if (num == null) return '-';
  return 'Rp ' + Number(num).toLocaleString('id-ID');
}
function fmtTon(num) {
  if (num == null) return '-';
  return Number(num).toFixed(2) + ' ton';
}
function fmtHa(num) {
  if (num == null) return '-';
  return Number(num).toFixed(2) + ' ha';
}
function fmtDate(str) {
  if (!str) return '-';
  return new Date(str).toLocaleDateString('id-ID', { day:'2-digit', month:'short', year:'numeric' });
}
function fmtNum(num) {
  if (num == null) return '-';
  return Number(num).toLocaleString('id-ID');
}

/* ── Badge Helpers ─── */
function badgeStatus(status) {
  const map = {
    'terverifikasi': '<span class="badge badge-success">✓ Terverifikasi</span>',
    'diajukan': '<span class="badge badge-warn">⏳ Diajukan</span>',
    'ditolak': '<span class="badge badge-danger">✗ Ditolak</span>',
    'draft': '<span class="badge badge-gray">📝 Draft</span>',
    'baru': '<span class="badge badge-danger">🔴 Baru</span>',
    'ditindaklanjuti': '<span class="badge badge-warn">🟡 Ditindaklanjuti</span>',
    'selesai': '<span class="badge badge-success">✅ Selesai</span>'
  };
  return map[status] || `<span class="badge badge-gray">${status}</span>`;
}
function badgeTingkat(tingkat) {
  const map = {
    'ringan': '<span class="badge badge-info">🟢 Ringan</span>',
    'sedang': '<span class="badge badge-warn">🟡 Sedang</span>',
    'berat': '<span class="badge badge-danger">🔴 Berat</span>'
  };
  return map[tingkat] || `<span class="badge badge-gray">${tingkat}</span>`;
}
function badgeGrade(grade) {
  const map = {
    'A': '<span class="badge badge-success">🌟 Grade A</span>',
    'B': '<span class="badge badge-info">⭐ Grade B</span>',
    'C': '<span class="badge badge-warn">Grade C</span>',
    'D': '<span class="badge badge-gray">Grade D</span>'
  };
  return map[grade] || `<span class="badge badge-gray">${grade}</span>`;
}

/* ── Tab System ─── */
function initTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const group = btn.closest('.tabs').dataset.group || 'default';
      document.querySelectorAll(`.tab-btn[data-group="${group}"] , .tabs[data-group="${group}"] .tab-btn`).forEach(b => b.classList.remove('active'));
      document.querySelectorAll(`.tab-content[data-group="${group}"]`).forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const target = document.getElementById(btn.dataset.tab);
      if (target) target.classList.add('active');
    });
  });
}

/* ── Logout ─── */
async function doLogout() {
  try {
    await API.post('/api/auth/logout', {});
    window.location.href = '/';
  } catch { window.location.href = '/'; }
}

/* ── Active Nav ─── */
function setActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.getAttribute('href') === path);
  });
}

document.addEventListener('DOMContentLoaded', setActiveNav);

