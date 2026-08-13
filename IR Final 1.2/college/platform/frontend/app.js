/**
 * InsightRural v2.0 — Production JavaScript Application
 * Modular, async-first, deterministic UI
 */

/* ════════════════════════════════════════════════════════════════════════════
   CONFIG
   ════════════════════════════════════════════════════════════════════════════ */
const API = {
  base: 'http://localhost:5000/api',
  legacyBase: 'http://localhost:5000/api',

  async get(path, params = {}) {
    const url = new URL(this.base + path, window.location.href);
    Object.entries(params).forEach(([k, v]) => v !== '' && url.searchParams.append(k, v));
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return res.json();
  },

  async post(path, body = {}) {
    const res = await fetch(this.base + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return res.json();
  },
};

/* ════════════════════════════════════════════════════════════════════════════
   STATE
   ════════════════════════════════════════════════════════════════════════════ */
const state = {
  currentPage: 'dashboard',
  sessionId: `session_${Date.now()}`,
  chatHistory: [],
  compareList: [],
  selectedBranches: [],
  currentPage_colleges: 1,
  collegesPerPage: 12,
  theme: localStorage.getItem('theme') || 'dark',
};

/* ════════════════════════════════════════════════════════════════════════════
   UTILITY HELPERS
   ════════════════════════════════════════════════════════════════════════════ */
function fmt(n) {
  if (n == null || n === 0) return '—';
  if (n >= 100000) return '₹' + (n / 100000).toFixed(1) + 'L';
  if (n >= 1000) return '₹' + (n / 1000).toFixed(0) + 'K';
  return '₹' + n;
}

function fmtLPA(v) {
  if (!v) return '—';
  return parseFloat(v).toFixed(1) + ' LPA';
}

function now() {
  return new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

function toast(msg, type = 'info', duration = 3000) {
  const container = document.getElementById('toastContainer');
  const icons = { success: 'fa-check-circle', error: 'fa-times-circle', info: 'fa-info-circle' };
  const colors = { success: '#10b981', error: '#ef4444', info: '#6366f1' };
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<i class="fas ${icons[type]}" style="color:${colors[type]}"></i><span>${msg}</span>`;
  container.appendChild(t);
  setTimeout(() => t.remove(), duration);
}

function showLoading(text = 'Processing...') {
  document.getElementById('loadingText').textContent = text;
  document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
  document.getElementById('loadingOverlay').classList.add('hidden');
}

function typeBadge(type) {
  const t = (type || '').toLowerCase();
  if (t.includes('government') && !t.includes('aided')) return 'govt';
  if (t.includes('aided')) return 'aided';
  return 'private';
}

function typeBadgeText(type) {
  const t = (type || '').toLowerCase();
  if (t.includes('government') && !t.includes('aided')) return 'Government';
  if (t.includes('aided')) return 'Aided';
  return 'Private';
}

/* ════════════════════════════════════════════════════════════════════════════
   NAVIGATION
   ════════════════════════════════════════════════════════════════════════════ */
function navigateTo(page) {
  // Deactivate old
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));

  // Activate new
  const navItem = document.querySelector(`[data-page="${page}"]`);
  const pageEl = document.getElementById(`page-${page}`);

  if (navItem) navItem.classList.add('active');
  if (pageEl) pageEl.classList.add('active');

  state.currentPage = page;

  // Load page-specific data
  if (page === 'colleges') loadColleges();
  if (page === 'analytics') loadAnalyticsPage();
  if (page === 'hostels') loadHostels();

  // Close mobile sidebar
  document.getElementById('sidebar').classList.remove('open');
}

/* ════════════════════════════════════════════════════════════════════════════
   DASHBOARD
   ════════════════════════════════════════════════════════════════════════════ */
async function loadDashboardStats() {
  try {
    const data = await API.get('/stats');
    document.getElementById('statColleges').textContent = data.total_colleges;
    document.getElementById('statBranches').textContent = data.total_branches;
    document.getElementById('tbColleges').textContent = data.total_colleges;
    document.getElementById('tbLocations').textContent = data.total_locations;
  } catch (e) {
    console.warn('Stats load failed:', e.message);
  }
}

async function quickPredict() {
  const rank = parseInt(document.getElementById('qpRank').value);
  const category = document.getElementById('qpCategory').value;
  const branch = document.getElementById('qpBranch').value;

  if (!rank || rank < 1) {
    toast('Please enter a valid KCET rank', 'error');
    return;
  }

  // Navigate to predictor and pre-fill
  navigateTo('predictor');

  document.getElementById('predRank').value = rank;
  document.getElementById('predCategory').value = category;

  // Select the branch chip
  state.selectedBranches = [branch];
  document.querySelectorAll('.branch-chip').forEach(chip => {
    chip.classList.toggle('selected', chip.dataset.branch === branch);
  });

  // Auto-run
  await runPredictor();
}

/* ════════════════════════════════════════════════════════════════════════════
   COLLEGE PREDICTOR
   ════════════════════════════════════════════════════════════════════════════ */
function initBranchChips() {
  const branches = [
    { code: 'CSE', label: 'CSE' },
    { code: 'ISE', label: 'ISE' },
    { code: 'ECE', label: 'ECE' },
    { code: 'EEE', label: 'EEE' },
    { code: 'ME', label: 'Mechanical' },
    { code: 'CIVIL', label: 'Civil' },
    { code: 'AI_DS', label: 'AI & DS' },
    { code: 'CY', label: 'Cyber Security' },
    { code: 'ML', label: 'ML' },
    { code: 'AERO', label: 'Aerospace' },
    { code: 'BIOTECH', label: 'Biotech' },
  ];

  const container = document.getElementById('branchChips');
  if (!container) return;

  container.innerHTML = branches.map(b => `
    <button class="branch-chip ${state.selectedBranches.includes(b.code) ? 'selected' : ''}"
            data-branch="${b.code}" onclick="toggleBranchChip(this, '${b.code}')">
      ${b.label}
    </button>
  `).join('');
}

function toggleBranchChip(el, branch) {
  if (state.selectedBranches.includes(branch)) {
    state.selectedBranches = state.selectedBranches.filter(b => b !== branch);
    el.classList.remove('selected');
  } else {
    state.selectedBranches.push(branch);
    el.classList.add('selected');
  }
}

async function runPredictor() {
  const rank = parseInt(document.getElementById('predRank').value);
  const category = document.getElementById('predCategory').value;
  const location = document.getElementById('predLocation').value;
  const budget = parseInt(document.getElementById('predBudget').value) || 0;
  const collegeType = document.getElementById('predCollegeType').value;

  const hostelRequired = document.getElementById('quotaHostel').checked;
  const ruralQuota = document.getElementById('quotaRural').checked;
  const kannadaMedium = document.getElementById('quotaKannada').checked;
  const hk371j = document.getElementById('quota371j').checked;
  const snq = document.getElementById('quotaSNQ').checked;

  if (!rank || rank < 1) {
    toast('Please enter your KCET rank', 'error');
    return;
  }

  const branches = state.selectedBranches.length > 0 ? state.selectedBranches : ['CSE'];

  showLoading('Running ML prediction engine...');

  try {
    const result = await API.post('/predict', {
      kcet_rank: rank,
      category,
      preferred_branches: branches,
      preferred_locations: location ? [location] : [],
      budget: budget || null,
      hostel_required: hostelRequired,
      college_type: collegeType || null,
      rural_quota: ruralQuota,
      kannada_medium: kannadaMedium,
      hk_371j: hk371j,
      snq,
      top_n: 20,
    });

    renderPredictorResults(result, rank, category);
    toast('Prediction complete!', 'success');

  } catch (e) {
    toast('Prediction engine error: ' + e.message, 'error');
    console.error(e);
  } finally {
    hideLoading();
  }
}

function renderPredictorResults(result, rank, category) {
  const container = document.getElementById('predictorResults');
  if (!container) return;

  // Support both old and new API format
  const predictions = result.predictions || [];
  const safe = (result.safe || predictions.filter(p => ['Safe', 'Very Safe'].includes(p.category || p.admission_tier))).slice(0, 8);
  const moderate = (result.moderate || predictions.filter(p => p.category === 'Moderate' || p.admission_tier === 'Moderate')).slice(0, 6);
  const ambitious = (result.ambitious || predictions.filter(p => ['Dream', 'Ambitious'].includes(p.category || p.admission_tier))).slice(0, 4);

  const totalEligible = result.total_eligible || predictions.length;

  container.innerHTML = `
    <div class="prediction-summary" style="margin-bottom:20px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <div>
          <span style="font-size:1.1rem;font-weight:700;">Rank ${rank.toLocaleString()} • ${category}</span>
          <span style="color:var(--text-muted);font-size:0.82rem;margin-left:10px;">${totalEligible} eligible colleges found</span>
        </div>
        <div style="display:flex;gap:8px;">
          <span style="background:rgba(16,185,129,0.15);color:var(--accent-green);padding:4px 12px;border-radius:20px;font-size:0.78rem;font-weight:600;">
            ✅ ${safe.length} Safe
          </span>
          <span style="background:rgba(245,158,11,0.15);color:var(--accent-orange);padding:4px 12px;border-radius:20px;font-size:0.78rem;font-weight:600;">
            🎯 ${moderate.length} Moderate
          </span>
          <span style="background:rgba(236,72,153,0.15);color:var(--accent-pink);padding:4px 12px;border-radius:20px;font-size:0.78rem;font-weight:600;">
            🌟 ${ambitious.length} Ambitious
          </span>
        </div>
      </div>
    </div>

    ${safe.length ? renderTierSection('SAFE', safe, 'safe') : ''}
    ${moderate.length ? renderTierSection('MODERATE', moderate, 'moderate') : ''}
    ${ambitious.length ? renderTierSection('AMBITIOUS', ambitious, 'ambitious') : ''}

    ${safe.length === 0 && moderate.length === 0 && ambitious.length === 0 ? `
      <div class="empty-state">
        <i class="fas fa-search"></i>
        <h3>No colleges found</h3>
        <p>No colleges satisfy all the constraints you specified.<br/>Try relaxing location, budget, or branch filters.</p>
      </div>
    ` : ''}
  `;
}

function renderTierSection(label, colleges, tier) {
  const icons = { safe: '✅', moderate: '🎯', ambitious: '🌟' };
  const colors = { safe: 'var(--accent-green)', moderate: 'var(--accent-orange)', ambitious: 'var(--accent-pink)' };

  return `
    <div class="tier-section">
      <div class="tier-label">
        <span style="font-size:1rem;">${icons[tier]}</span>
        <h3 style="color:${colors[tier]};">${label} OPTIONS</h3>
        <span class="count">${colleges.length} colleges</span>
      </div>
      <div class="result-cards">
        ${colleges.map(c => renderResultCard(c, tier)).join('')}
      </div>
    </div>
  `;
}

function renderResultCard(c, tier) {
  const prob = c.admission_probability || c.probability || 50;
  const feeData = c.annual_fee || {};
  const feeVal = typeof feeData === 'object' ? (feeData.gm || feeData.sc_st || 0) : (feeData || 0);
  const name = c.college_name || c.name || 'Unknown College';
  const location = c.location || '—';
  const naac = c.naac_grade || 'N/A';
  const branch = c.branch || (c.branches ? c.branches[0] : '—');
  const lpa = c.placement_avg_lpa;

  return `
    <div class="result-card ${tier}" onclick="openCollegeDetail('${c.college_id || ''}')">
      <div class="result-prob ${tier}">
        <span class="result-prob-val">${Math.round(prob)}%</span>
        <span class="result-prob-label">chance</span>
      </div>
      <div class="result-info">
        <div class="result-name" title="${name}">${name}</div>
        <div class="result-meta">
          <span><i class="fas fa-map-marker-alt"></i>${location}</span>
          ${branch ? `<span><i class="fas fa-code-branch"></i>${branch}</span>` : ''}
          ${naac !== 'N/A' ? `<span><i class="fas fa-star"></i>NAAC ${naac}</span>` : ''}
          ${lpa ? `<span><i class="fas fa-briefcase"></i>${fmtLPA(lpa)}</span>` : ''}
        </div>
      </div>
      <div class="result-fee">
        ${feeVal ? `<div class="fee-val">${fmt(feeVal)}</div><div class="fee-label">/year</div>` : ''}
      </div>
    </div>
  `;
}

/* ════════════════════════════════════════════════════════════════════════════
   COLLEGE EXPLORER
   ════════════════════════════════════════════════════════════════════════════ */
async function loadColleges(page = 1) {
  state.currentPage_colleges = page;
  const loading = document.getElementById('collegeLoading');
  const grid = document.getElementById('collegeGrid');

  if (loading) loading.classList.remove('hidden');
  if (grid) grid.innerHTML = '';

  const q = document.getElementById('collegeSearch')?.value || '';
  const branch = document.getElementById('filterBranch')?.value || '';
  const location = document.getElementById('filterLocation')?.value || '';
  const type = document.getElementById('filterType')?.value || '';

  try {
    const data = await API.get('/colleges', { q, branch, location, college_type: type, page, limit: state.collegesPerPage });
    document.getElementById('collegeTotal').textContent = data.total;
    renderCollegeGrid(data.items);
    renderPagination(data.total, data.page, data.pages);
    if (loading) loading.classList.add('hidden');
  } catch (e) {
    if (loading) loading.classList.add('hidden');
    toast('Failed to load colleges', 'error');
  }
}

function renderCollegeGrid(colleges) {
  const grid = document.getElementById('collegeGrid');
  if (!grid) return;

  if (!colleges || colleges.length === 0) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1;">
        <i class="fas fa-search"></i>
        <h3>No colleges found</h3>
        <p>Try different search criteria</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = colleges.map(c => {
    const btype = typeBadge(c.type);
    const btypeText = typeBadgeText(c.type);
    const feeVal = c.annual_fee_gm;

    return `
      <div class="college-card" onclick="openCollegeDetail('${c.college_id}')">
        <div class="cc-header">
          <span class="cc-badge ${btype}">${btypeText}</span>
          <span class="cc-naac">${c.naac_grade || 'N/A'}</span>
        </div>
        <div class="cc-name">${c.name}</div>
        <div class="cc-location"><i class="fas fa-map-marker-alt"></i>${c.location || '—'}</div>
        <div class="cc-meta">
          <span><i class="fas fa-code-branch"></i>${(c.branches || []).slice(0, 3).join(', ') || '—'}</span>
          ${feeVal ? `<span class="cc-fee">${fmt(feeVal)}/yr</span>` : ''}
        </div>
        ${c.hostel_available ? `<div style="margin-top:8px;"><span class="tag"><i class="fas fa-bed"></i> Hostel</span></div>` : ''}
      </div>
    `;
  }).join('');
}

function renderPagination(total, page, pages) {
  const container = document.getElementById('collegePagination');
  if (!container || pages <= 1) { if (container) container.innerHTML = ''; return; }

  const buttons = [];

  if (page > 1) buttons.push(`<button class="page-btn" onclick="loadColleges(${page - 1})"><i class="fas fa-chevron-left"></i></button>`);

  const start = Math.max(1, page - 2);
  const end = Math.min(pages, page + 2);

  if (start > 1) buttons.push(`<button class="page-btn" onclick="loadColleges(1)">1</button>`);
  if (start > 2) buttons.push(`<span style="color:var(--text-muted);padding:0 4px;">...</span>`);

  for (let i = start; i <= end; i++) {
    buttons.push(`<button class="page-btn ${i === page ? 'active' : ''}" onclick="loadColleges(${i})">${i}</button>`);
  }

  if (end < pages - 1) buttons.push(`<span style="color:var(--text-muted);padding:0 4px;">...</span>`);
  if (end < pages) buttons.push(`<button class="page-btn" onclick="loadColleges(${pages})">${pages}</button>`);

  if (page < pages) buttons.push(`<button class="page-btn" onclick="loadColleges(${page + 1})"><i class="fas fa-chevron-right"></i></button>`);

  container.innerHTML = buttons.join('');
}

async function loadFilterOptions() {
  try {
    const [branches, locations] = await Promise.all([
      API.get('/branches'),
      API.get('/locations'),
    ]);

    const branchSelects = ['filterBranch', 'predLocation'];
    ['filterBranch'].forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      branches.forEach(b => {
        const opt = document.createElement('option');
        opt.value = b; opt.textContent = b;
        el.appendChild(opt);
      });
    });

    ['filterLocation', 'predLocation', 'hostelLocation'].forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      locations.forEach(l => {
        const opt = document.createElement('option');
        opt.value = l; opt.textContent = l;
        el.appendChild(opt);
      });
    });
  } catch (e) {
    console.warn('Filter options load failed:', e.message);
  }
}

/* ════════════════════════════════════════════════════════════════════════════
   COLLEGE DETAIL MODAL
   ════════════════════════════════════════════════════════════════════════════ */
async function openCollegeDetail(collegeId) {
  if (!collegeId) return;
  showLoading('Loading college details...');
  try {
    const c = await API.get(`/colleges/${collegeId}`);
    hideLoading();
    renderCollegeModal(c);
    document.getElementById('collegeModal').classList.remove('hidden');
  } catch (e) {
    hideLoading();
    toast('Could not load college details', 'error');
  }
}

function renderCollegeModal(c) {
  document.getElementById('modalCollegeName').textContent = c.name;

  const fee = c.annual_fee || {};
  const branches = (c.branches || []).join(', ') || '—';
  const cutoffs = c.cutoffs || c.cutoff_data || {};
  const cutoff2024 = cutoffs['2024'] || {};

  document.getElementById('modalBody').innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;">
      <div>
        <p style="color:var(--text-muted);font-size:0.78rem;margin-bottom:4px;">TYPE</p>
        <p style="font-weight:600;">${c.type || '—'}</p>
      </div>
      <div>
        <p style="color:var(--text-muted);font-size:0.78rem;margin-bottom:4px;">LOCATION</p>
        <p style="font-weight:600;">${c.location || '—'}</p>
      </div>
      <div>
        <p style="color:var(--text-muted);font-size:0.78rem;margin-bottom:4px;">NAAC GRADE</p>
        <p style="font-weight:600;">${c.naac_grade || 'N/A'}</p>
      </div>
      <div>
        <p style="color:var(--text-muted);font-size:0.78rem;margin-bottom:4px;">AFFILIATION</p>
        <p style="font-weight:600;">${c.affiliation || '—'}</p>
      </div>
    </div>

    <div style="margin-bottom:16px;">
      <p style="color:var(--text-muted);font-size:0.78rem;margin-bottom:8px;">BRANCHES OFFERED</p>
      <div style="display:flex;flex-wrap:wrap;gap:6px;">${(c.branches || []).map(b =>
        `<span class="tag">${b}</span>`).join('')}</div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px;">
      <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:14px;text-align:center;">
        <div style="font-size:1.2rem;font-weight:700;color:var(--accent-cyan);">${fmt(typeof fee === 'object' ? fee.gm : fee)}</div>
        <div style="font-size:0.72rem;color:var(--text-muted);">Annual Fee (GM)</div>
      </div>
      <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:14px;text-align:center;">
        <div style="font-size:1.2rem;font-weight:700;color:var(--accent-green);">${fmtLPA(c.placement_avg_lpa)}</div>
        <div style="font-size:0.72rem;color:var(--text-muted);">Avg Placement</div>
      </div>
      <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:14px;text-align:center;">
        <div style="font-size:1.2rem;font-weight:700;color:var(--accent-orange);">${c.hostel_available ? '✓ Yes' : '✗ No'}</div>
        <div style="font-size:0.72rem;color:var(--text-muted);">Hostel</div>
      </div>
    </div>

    ${Object.keys(cutoff2024).length ? `
    <div>
      <p style="color:var(--text-muted);font-size:0.78rem;margin-bottom:8px;">2024 CUTOFF RANKS</p>
      <div style="display:flex;flex-direction:column;gap:6px;">
        ${Object.entries(cutoff2024).slice(0, 5).map(([branch, cats]) => `
          <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;">
            <span style="font-weight:600;font-size:0.875rem;">${branch}</span>
            <div style="display:flex;gap:12px;font-size:0.78rem;color:var(--text-secondary);">
              ${typeof cats === 'object' ? Object.entries(cats).map(([cat, rank]) =>
                `<span>${cat}: <strong>${rank?.toLocaleString() || '—'}</strong></span>`).join('') : cats}
            </div>
          </div>
        `).join('')}
      </div>
    </div>
    ` : ''}

    <div style="display:flex;gap:10px;margin-top:20px;">
      <button class="btn-primary" onclick="addToCompare('${c.college_id}','${c.name.replace(/'/g,"\\'")}'); document.getElementById('collegeModal').classList.add('hidden');">
        <i class="fas fa-balance-scale"></i> Add to Compare
      </button>
      ${c.website ? `<a href="${c.website}" target="_blank" class="btn-outline"><i class="fas fa-external-link-alt"></i> Visit Website</a>` : ''}
    </div>
  `;
}

/* ════════════════════════════════════════════════════════════════════════════
   COMPARE
   ════════════════════════════════════════════════════════════════════════════ */
function addToCompare(id, name) {
  if (state.compareList.length >= 4) {
    toast('Maximum 4 colleges for comparison', 'error');
    return;
  }
  if (state.compareList.find(c => c.id === id)) {
    toast('Already added for comparison', 'info');
    return;
  }
  state.compareList.push({ id, name });
  renderCompareTags();
  toast(`${name} added to comparison`, 'success');
  document.getElementById('runCompare').disabled = state.compareList.length < 2;
}

function removeFromCompare(id) {
  state.compareList = state.compareList.filter(c => c.id !== id);
  renderCompareTags();
  document.getElementById('runCompare').disabled = state.compareList.length < 2;
}

function renderCompareTags() {
  const container = document.getElementById('compareSelected');
  if (!container) return;

  container.innerHTML = state.compareList.map(c => `
    <div class="compare-tag">
      <span>${c.name}</span>
      <button onclick="removeFromCompare('${c.id}')"><i class="fas fa-times"></i></button>
    </div>
  `).join('');
}

async function runCompare() {
  if (state.compareList.length < 2) {
    toast('Select at least 2 colleges', 'error');
    return;
  }

  showLoading('Comparing colleges...');
  try {
    const result = await API.post('/colleges/compare', {
      college_ids: state.compareList.map(c => c.id),
      session_id: state.sessionId,
    });

    renderCompareTable(result.colleges);
    hideLoading();
    toast('Comparison ready!', 'success');
  } catch (e) {
    hideLoading();
    toast('Compare failed: ' + e.message, 'error');
  }
}

function renderCompareTable(colleges) {
  const container = document.getElementById('compareTable');
  if (!container || !colleges) return;

  const metrics = [
    { key: 'type', label: 'Type' },
    { key: 'location', label: 'Location' },
    { key: 'naac_grade', label: 'NAAC Grade' },
    { key: 'annual_fee_gm', label: 'Annual Fee (GM)', format: v => fmt(v?.gm || v) },
    { key: 'placement_avg_lpa', label: 'Avg Placement', format: fmtLPA },
    { key: 'hostel_available', label: 'Hostel', format: v => v ? '✅ Yes' : '❌ No' },
    { key: 'admission_probability', label: 'Admission Chance', format: v => v ? `${v}%` : '—' },
    { key: 'total_seats', label: 'Total Seats' },
  ];

  container.innerHTML = `
    <table class="compare-table">
      <thead>
        <tr>
          <th>Metric</th>
          ${colleges.map(c => `<th>${c.name}</th>`).join('')}
        </tr>
      </thead>
      <tbody>
        ${metrics.map(m => `
          <tr>
            <td style="font-weight:600;color:var(--text-muted);">${m.label}</td>
            ${colleges.map(c => {
              const raw = c[m.key];
              const val = m.format ? m.format(raw) : (raw || '—');
              return `<td>${val}</td>`;
            }).join('')}
          </tr>
        `).join('')}
        <tr>
          <td style="font-weight:600;color:var(--text-muted);">Branches</td>
          ${colleges.map(c => `<td style="font-size:0.78rem;">${(c.branches || []).join(', ')}</td>`).join('')}
        </tr>
      </tbody>
    </table>
  `;
}

async function compareSearchHandler(e) {
  const q = e.target.value;
  const dropdown = document.getElementById('compareSuggestions');
  if (!q || q.length < 2) { dropdown.classList.remove('show'); return; }

  try {
    const data = await API.get('/colleges', { q, limit: 5 });
    if (!data.items || data.items.length === 0) { dropdown.classList.remove('show'); return; }

    dropdown.innerHTML = data.items.map(c => `
      <div class="compare-dropdown-item" onclick="addToCompare('${c.college_id}', '${c.name.replace(/'/g, "\\'")}'); this.parentElement.classList.remove('show'); document.getElementById('compareSearch').value='';">
        <strong>${c.name}</strong> <span style="color:var(--text-muted);font-size:0.75rem;">${c.location || ''}</span>
      </div>
    `).join('');
    dropdown.classList.add('show');
  } catch (e) {
    dropdown.classList.remove('show');
  }
}

/* ════════════════════════════════════════════════════════════════════════════
   SCHOLARSHIPS
   ════════════════════════════════════════════════════════════════════════════ */
async function checkScholarships() {
  const category = document.getElementById('schCategory').value;
  const income = parseInt(document.getElementById('schIncome').value) || null;
  const rural = document.getElementById('schRural').checked;
  const hk371j = document.getElementById('sch371j').checked;
  const snq = document.getElementById('schSNQ').checked;

  showLoading('Checking scholarship eligibility...');

  try {
    const result = await API.post('/scholarships/check', {
      category,
      annual_income: income,
      rural_quota: rural,
      hk_371j: hk371j,
      snq,
    });

    renderScholarshipResults(result);
    hideLoading();
  } catch (e) {
    hideLoading();
    toast('Scholarship check failed: ' + e.message, 'error');
  }
}

function renderScholarshipResults(result) {
  const container = document.getElementById('scholarshipResults');
  if (!container) return;

  const sch = result.scholarships || {};
  const eligible = sch.eligible || [];
  const ineligible = sch.ineligible || [];
  const summary = sch.summary || {};

  container.innerHTML = `
    ${eligible.length ? `
    <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:12px;padding:16px;margin-bottom:16px;">
      <div style="font-weight:700;color:var(--accent-green);margin-bottom:4px;">
        🎉 ${eligible.length} Scholarship${eligible.length !== 1 ? 's' : ''} Eligible!
      </div>
      ${summary.estimated_annual_benefit_inr ? `
        <div style="font-size:0.82rem;color:var(--text-secondary);">
          Estimated annual benefit: <strong style="color:var(--accent-cyan);">${fmt(summary.estimated_annual_benefit_inr)}</strong>
        </div>
      ` : ''}
    </div>
    ` : `
    <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);border-radius:12px;padding:16px;margin-bottom:16px;">
      <div style="font-weight:700;color:var(--accent-red);">No scholarships eligible based on current profile</div>
      <div style="font-size:0.82rem;color:var(--text-secondary);">Update your income or special situation details for better results</div>
    </div>
    `}

    <h3 style="font-size:0.9rem;font-weight:600;color:var(--text-secondary);margin-bottom:12px;">Eligible Schemes</h3>
    ${eligible.map(s => renderSchCard(s, true)).join('')}

    ${ineligible.length ? `
    <h3 style="font-size:0.9rem;font-weight:600;color:var(--text-muted);margin-bottom:12px;margin-top:16px;">Not Eligible</h3>
    ${ineligible.map(s => renderSchCard(s, false)).join('')}
    ` : ''}
  `;
}

function renderSchCard(s, eligible) {
  const reasons = s.reasons || [];
  const icon = eligible ? '✅' : '❌';

  return `
    <div class="sch-card ${eligible ? 'eligible' : 'ineligible'}">
      <div class="sch-header">
        <div class="sch-name">${icon} ${s.name}</div>
        <div class="sch-amount">${s.amount.split('(')[0].trim()}</div>
      </div>
      <div class="sch-authority"><i class="fas fa-building"></i> ${s.authority} &bull; ${s.coverage}</div>
      <div class="sch-reasons">
        ${reasons.slice(0, 3).map(r => `
          <div class="sch-reason ${eligible ? 'ok' : 'fail'}">
            <i class="fas ${eligible ? 'fa-check' : 'fa-times'}"></i>${r}
          </div>
        `).join('')}
      </div>
      ${eligible ? `<a href="${s.url}" target="_blank" class="sch-portal"><i class="fas fa-external-link-alt"></i>${s.portal}</a>` : ''}
    </div>
  `;
}

/* ════════════════════════════════════════════════════════════════════════════
   HOSTELS
   ════════════════════════════════════════════════════════════════════════════ */
async function loadHostels() {
  const location = document.getElementById('hostelLocation')?.value || '';
  const budget = parseInt(document.getElementById('hostelBudget')?.value || 100000);

  try {
    const result = await API.get('/hostels', { location, budget });
    renderHostelGrid(result.hostels || []);
    toast(`${result.total} hostels found`, 'success');
  } catch (e) {
    toast('Failed to load hostels: ' + e.message, 'error');
  }
}

function renderHostelGrid(hostels) {
  const grid = document.getElementById('hostelGrid');
  if (!grid) return;

  if (!hostels.length) {
    grid.innerHTML = `<div class="empty-state"><i class="fas fa-bed"></i><h3>No hostels found</h3><p>Try different filters</p></div>`;
    return;
  }

  grid.innerHTML = hostels.map(h => `
    <div class="hostel-card">
      <div class="hostel-name">${h.college_name}</div>
      <div class="hostel-location"><i class="fas fa-map-marker-alt"></i> ${h.location || '—'}</div>
      <div class="hostel-features">
        ${h.boys_hostel ? `<span class="hostel-feature active"><i class="fas fa-male"></i> Boys</span>` : ''}
        ${h.girls_hostel ? `<span class="hostel-feature active"><i class="fas fa-female"></i> Girls</span>` : ''}
        ${h.mess_available ? `<span class="hostel-feature active"><i class="fas fa-utensils"></i> Mess</span>` : ''}
        ${h.wifi ? `<span class="hostel-feature active"><i class="fas fa-wifi"></i> WiFi</span>` : ''}
      </div>
      <div class="hostel-fee">${h.annual_fee ? fmt(h.annual_fee) + '/year' : 'Fee N/A'}</div>
    </div>
  `).join('');
}

/* ════════════════════════════════════════════════════════════════════════════
   ANALYTICS
   ════════════════════════════════════════════════════════════════════════════ */
async function loadAnalyticsPage() {
  const branch = document.getElementById('analyticsBranch')?.value || 'CSE';
  const category = document.getElementById('analyticsCategory')?.value || 'GM';

  showLoading('Loading analytics...');

  try {
    const [trendsData, placementData] = await Promise.all([
      API.get('/analytics/cutoff-trends', { branch, category, limit: 15 }),
      API.get('/analytics/placement-overview'),
    ]);

    renderCutoffChart(trendsData.data || []);
    renderPlacementChart(placementData.top_colleges || [], placementData.by_college_type || {});
    renderTrendTable(trendsData.data || []);
    hideLoading();
  } catch (e) {
    hideLoading();
    toast('Analytics load failed: ' + e.message, 'error');
  }
}

function renderCutoffChart(data) {
  const container = document.getElementById('cutoffChart');
  if (!container) return;

  const maxCutoff = Math.max(...data.map(d => d.latest_cutoff || 0), 1);

  container.innerHTML = data.slice(0, 10).map(d => {
    const pct = Math.min(100, (d.latest_cutoff / maxCutoff) * 100);
    const col = pct > 70 ? '#ef4444' : pct > 40 ? '#f59e0b' : '#10b981';
    const name = (d.college_name || '').length > 30 ? d.college_name.substring(0, 28) + '…' : d.college_name;

    return `
      <div class="chart-bar-row">
        <div class="chart-bar-label" title="${d.college_name}">${name}</div>
        <div class="chart-bar-track">
          <div class="chart-bar-fill" style="width:${pct}%;background:${col};">
            ${d.latest_cutoff?.toLocaleString() || '—'}
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function renderPlacementChart(colleges, byType) {
  const container = document.getElementById('placementChart');
  if (!container) return;

  const maxLPA = Math.max(...Object.values(byType), 1);

  const typeRows = Object.entries(byType).map(([type, avg]) => {
    const pct = Math.min(100, (avg / maxLPA) * 100);
    const label = type.replace('_', ' ');
    const col = type.includes('Government') && !type.includes('Aided') ? '#10b981'
              : type.includes('Aided') ? '#6366f1' : '#f59e0b';

    return `
      <div class="chart-bar-row">
        <div class="chart-bar-label">${label}</div>
        <div class="chart-bar-track">
          <div class="chart-bar-fill" style="width:${pct}%;background:${col};">${avg} LPA</div>
        </div>
      </div>
    `;
  });

  container.innerHTML = typeRows.join('') || '<p style="color:var(--text-muted);">No placement data available</p>';
}

function renderTrendTable(data) {
  const container = document.getElementById('trendTable');
  if (!container) return;

  if (!data.length) {
    container.innerHTML = '<p style="color:var(--text-muted);">No trend data available</p>';
    return;
  }

  container.innerHTML = `
    <table class="data-table">
      <thead>
        <tr>
          <th>College</th>
          <th>Location</th>
          <th>Latest Cutoff</th>
          <th>1yr Trend</th>
          <th>Direction</th>
        </tr>
      </thead>
      <tbody>
        ${data.map(d => `
          <tr>
            <td style="font-weight:600;">${d.college_name}</td>
            <td style="color:var(--text-secondary);">${d.location || '—'}</td>
            <td>${d.latest_cutoff?.toLocaleString() || '—'}</td>
            <td style="color:${d.trend_1yr < 0 ? 'var(--accent-red)' : 'var(--accent-green)'};">
              ${d.trend_1yr > 0 ? '+' : ''}${d.trend_1yr || 0}
            </td>
            <td>${d.trend_direction || '—'}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}

/* ════════════════════════════════════════════════════════════════════════════
   AI CHAT
   ════════════════════════════════════════════════════════════════════════════ */
function addChatMessage(role, content, isTyping = false) {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `chat-message ${role === 'user' ? 'user-message' : 'bot-message'}${isTyping ? ' typing-indicator' : ''}`;

  const avatar = role === 'user'
    ? `<div class="msg-avatar"><i class="fas fa-user"></i></div>`
    : `<div class="msg-avatar"><i class="fas fa-robot"></i></div>`;

  const bubbleContent = isTyping
    ? `<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>`
    : content.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>');

  div.innerHTML = `
    ${avatar}
    <div class="msg-content">
      <div class="msg-bubble">${bubbleContent}</div>
      <span class="msg-time">${now()}</span>
    </div>
  `;

  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function updateProfileDisplay(profile) {
  const container = document.getElementById('profileDisplay');
  if (!container || !profile) return;

  const fields = [
    { label: 'Rank', value: profile.rank ? `#${profile.rank.toLocaleString()}` : null },
    { label: 'Category', value: profile.category },
    { label: 'Branches', value: (profile.preferred_branches || []).join(', ') || null },
    { label: 'Location', value: (profile.preferred_locations || []).join(', ') || null },
    { label: 'Budget', value: profile.budget ? fmt(profile.budget) + '/yr' : null },
    { label: 'Hostel', value: profile.hostel_required ? 'Required' : null },
    { label: 'Rural Quota', value: profile.rural_quota ? 'Yes' : null },
    { label: '371(J)', value: profile.hk_371j ? 'Yes' : null },
  ].filter(f => f.value);

  if (!fields.length) return;

  container.innerHTML = fields.map(f => `
    <div class="profile-field">
      <span class="profile-field-label">${f.label}</span>
      <span class="profile-field-value">${f.value}</span>
    </div>
  `).join('');
}

async function sendChatMessage(msg) {
  if (!msg || !msg.trim()) return;

  // Add user message
  addChatMessage('user', msg);
  state.chatHistory.push({ role: 'user', content: msg });

  // Clear input
  const input = document.getElementById('chatInput');
  if (input) input.value = '';

  // Show typing indicator
  const typingEl = addChatMessage('bot', '', true);

  try {
    const result = await API.post('/chat', {
      message: msg,
      session_id: state.sessionId,
      history: state.chatHistory.slice(-10),
    });

    typingEl.remove();

    // Update profile display
    if (result.pipeline_data?.student_profile) {
      updateProfileDisplay(result.pipeline_data.student_profile);
    }

    // Show response
    const response = result.response || 'Sorry, I could not process that.';
    addChatMessage('bot', response);
    state.chatHistory.push({ role: 'assistant', content: response });

    // If structured results available, show a summary card
    if (result.pipeline_data?.safe?.length || result.pipeline_data?.moderate?.length) {
      const pd = result.pipeline_data;
      const safeCount = (pd.safe || []).length;
      const modCount = (pd.moderate || []).length;

      const card = addChatMessage('bot', `
📊 **Results Summary:**
✅ ${safeCount} Safe options | 🎯 ${modCount} Moderate options

💡 Want detailed predictions? <button class="btn-primary" onclick="navigateTo('predictor')" style="display:inline-flex;padding:6px 14px;font-size:0.78rem;margin-top:6px;">Open Predictor →</button>
      `);
    }

  } catch (e) {
    typingEl.remove();
    addChatMessage('bot', 'I encountered an error. Please try again. If the issue persists, try restating your query with your KCET rank and category.');
    console.error('Chat error:', e);
  }
}

/* ════════════════════════════════════════════════════════════════════════════
   THEME TOGGLE
   ════════════════════════════════════════════════════════════════════════════ */
function toggleTheme() {
  state.theme = state.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', state.theme);
  localStorage.setItem('theme', state.theme);
  const icon = document.querySelector('#themeToggle i');
  if (icon) icon.className = state.theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
}

/* ════════════════════════════════════════════════════════════════════════════
   INIT
   ════════════════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', async () => {
  // Apply saved theme
  if (state.theme === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
    const icon = document.querySelector('#themeToggle i');
    if (icon) icon.className = 'fas fa-sun';
  }

  // Nav items
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => navigateTo(item.dataset.page));
  });

  // Feature cards
  document.querySelectorAll('.feature-card[data-goto]').forEach(card => {
    card.addEventListener('click', () => navigateTo(card.dataset.goto));
  });

  // Quick predict
  document.getElementById('quickPredictBtn')?.addEventListener('click', quickPredict);

  // Theme toggle
  document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);

  // Mobile menu
  document.getElementById('menuToggle')?.addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
  });

  // Modal close
  document.getElementById('closeModal')?.addEventListener('click', () => {
    document.getElementById('collegeModal').classList.add('hidden');
  });
  document.getElementById('collegeModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'collegeModal') e.target.classList.add('hidden');
  });

  // Predictor
  document.getElementById('runPredictor')?.addEventListener('click', runPredictor);
  initBranchChips();

  // College explorer
  document.getElementById('collegeSearch')?.addEventListener('input', debounce(() => loadColleges(1), 400));
  document.getElementById('filterBranch')?.addEventListener('change', () => loadColleges(1));
  document.getElementById('filterLocation')?.addEventListener('change', () => loadColleges(1));
  document.getElementById('filterType')?.addEventListener('change', () => loadColleges(1));
  document.getElementById('clearFilters')?.addEventListener('click', () => {
    ['collegeSearch', 'filterBranch', 'filterLocation', 'filterType'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '';
    });
    loadColleges(1);
  });

  // Compare
  document.getElementById('compareSearch')?.addEventListener('input', debounce(compareSearchHandler, 300));
  document.getElementById('runCompare')?.addEventListener('click', runCompare);

  // Scholarships
  document.getElementById('checkScholarships')?.addEventListener('click', checkScholarships);

  // Hostels
  document.getElementById('hostelBudget')?.addEventListener('input', (e) => {
    const val = parseInt(e.target.value);
    document.getElementById('hostelBudgetVal').textContent = fmt(val);
  });
  document.getElementById('findHostels')?.addEventListener('click', loadHostels);

  // Analytics
  document.getElementById('loadAnalytics')?.addEventListener('click', loadAnalyticsPage);

  // Chat
  document.getElementById('sendMessage')?.addEventListener('click', () => {
    const input = document.getElementById('chatInput');
    if (input) sendChatMessage(input.value.trim());
  });

  document.getElementById('chatInput')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const input = document.getElementById('chatInput');
      if (input) sendChatMessage(input.value.trim());
    }
  });

  document.querySelectorAll('.suggest-chip').forEach(chip => {
    chip.addEventListener('click', () => sendChatMessage(chip.dataset.msg));
  });

  // Global search
  document.getElementById('globalSearch')?.addEventListener('input', debounce((e) => {
    const q = e.target.value.trim();
    if (q.length > 1) {
      navigateTo('colleges');
      const searchBox = document.getElementById('collegeSearch');
      if (searchBox) { searchBox.value = q; loadColleges(1); }
    }
  }, 400));

  // Load initial data
  await loadDashboardStats();
  await loadFilterOptions();

  // Check API health
  try {
    const health = await API.get('/health');
    const dot = document.querySelector('.status-dot');
    if (dot) {
      dot.className = `status-dot ${health.status === 'healthy' ? 'online' : 'offline'}`;
    }
  } catch (e) {
    const dot = document.querySelector('.status-dot');
    if (dot) dot.className = 'status-dot offline';
    console.warn('API not reachable:', e.message);
  }

  // Navigate to initial page
  navigateTo('dashboard');
});

/* ════════════════════════════════════════════════════════════════════════════
   UTILITIES
   ════════════════════════════════════════════════════════════════════════════ */
function debounce(fn, delay) {
  let t;
  return function (...args) {
    clearTimeout(t);
    t = setTimeout(() => fn.apply(this, args), delay);
  };
}
