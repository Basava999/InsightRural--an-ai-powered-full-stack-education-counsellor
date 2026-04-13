/**
 * InsightRural — Animated Landing Page
 * Million-Dollar Interactive Splash Experience
 */

(function () {
    'use strict';

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // FEATURE CARDS DATA
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    const FEATURES = [
        {
            icon: '🤖',
            title: 'AI Chat Counselor',
            tag: 'RAG · LLM',
            feature: 'chat',
            demo: 'chat',
            demoTexts: [
                'Best CSE colleges for KCET rank 5000?',
                'Scholarship for SC rural students?',
                'VTU fee structure 2025...',
            ],
        },
        {
            icon: '🎯',
            title: 'College Predictor',
            tag: 'ML · KEA',
            feature: 'predictor',
            demo: 'bars',
        },
        {
            icon: '💰',
            title: 'Scholarship Autopilot',
            tag: 'Auto-Apply',
            feature: 'scholarships',
            demo: 'progress',
            progressValue: 72,
        },
        {
            icon: '📊',
            title: 'Live Dashboard',
            tag: 'LIVE',
            feature: 'dashboard',
            demo: 'chart',
        },
        {
            icon: '🧭',
            title: 'Career Counselor',
            tag: 'AI · Gen',
            feature: 'career',
            demo: 'typing',
            demoTexts: [
                'Your path: Computer Science → SDE',
                'Salary range ₹8–22 LPA in 5 years',
                'Recommended: Data Structures, DSA',
            ],
        },
        {
            icon: '🏛️',
            title: 'KEA Counseling Suite',
            tag: 'Round 1–3',
            feature: 'counseling',
            demo: 'badge',
        },
    ];

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // MARQUEE TAGS — scrolling tech strip
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    const MARQUEE_ITEMS = [
        { icon: '🦙', label: 'LLaMA 3 Local' },
        { icon: '🔍', label: 'ChromaDB RAG' },
        { icon: '🏛️', label: 'KEA Algorithm' },
        { icon: '🤖', label: 'Ollama Engine' },
        { icon: '📈', label: 'ML Predictor' },
        { icon: '🎙️', label: 'Voice AI' },
        { icon: '🔒', label: '100% Private' },
        { icon: '🗂️', label: 'Document Vault' },
        { icon: '🌐', label: 'PWA Ready' },
        { icon: '🎬', label: 'Video Counselor' },
        { icon: '📋', label: 'Serial Dictatorship' },
        { icon: '⚡', label: 'Realtime Updates' },
    ];

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // TYPEWRITER PHRASES
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    const TYPEWRITER_PHRASES = [
        'Your AI Guide to Karnataka Colleges',
        'Predict Your Perfect College Seat',
        'Never Miss a Scholarship Again',
        'Voice-Powered Career Counseling',
        'From Village to Varsity with AI',
    ];

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // STATS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    const STATS = [
        { value: 230000, label: 'Candidates', prefix: '', suffix: '+' },
        { value: 200, label: 'Colleges', prefix: '', suffix: '+' },
        { value: 5, label: 'Cr Scholarships', prefix: '₹', suffix: 'Cr' },
        { value: 98, label: 'Accuracy', prefix: '', suffix: '%' },
    ];

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // BUILD THE LANDING HTML
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    function buildLanding() {
        const landing = document.createElement('div');
        landing.id = 'landing-screen';
        landing.setAttribute('role', 'main');
        landing.innerHTML = `
            <!-- Grid & canvas & blobs -->
            <div class="landing-grid"></div>
            <canvas id="landing-canvas"></canvas>
            <div class="landing-blob landing-blob-1"></div>
            <div class="landing-blob landing-blob-2"></div>
            <div class="landing-blob landing-blob-3"></div>
            <div class="landing-blob landing-blob-4"></div>

            <!-- Skip -->
            <button id="landing-skip">Skip →</button>

            <div class="landing-content">
                <!-- Logo -->
                <div class="landing-logomark">IR</div>

                <!-- Live pill -->
                <div class="landing-pill">
                    <div class="dot"></div>
                    AI-Powered · Karnataka Education · Free Forever
                </div>

                <!-- Headline -->
                <h1 class="landing-headline">
                    <span class="headline-static">InsightRural</span>
                    <span class="headline-dynamic" id="landing-typewriter">
                        Your AI Guide to Karnataka Colleges<span class="tw-cursor"></span>
                    </span>
                </h1>

                <!-- Sub -->
                <p class="landing-sub">
                    Helping rural Karnataka students navigate college admissions, scholarships, loans &amp; career paths — powered by local AI, completely free.
                </p>

                <!-- Stats -->
                <div class="landing-stats" id="landing-stats"></div>

                <!-- Feature Cards -->
                <div class="landing-features" id="landing-features"></div>

                <!-- Marquee -->
                <div class="landing-marquee-wrap">
                    <div class="landing-marquee-track" id="landing-marquee"></div>
                </div>

                <!-- CTA -->
                <div class="landing-cta-wrap">
                    <button class="landing-cta-btn" id="landing-enter">
                        Explore InsightRural
                        <span class="cta-arrow">→</span>
                    </button>
                    <span class="landing-cta-hint">Free · No Sign-up Required · Works Offline</span>
                </div>
            </div>
        `;
        document.body.insertBefore(landing, document.body.firstChild);
        return landing;
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // BUILD STATS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    function buildStats() {
        const container = document.getElementById('landing-stats');
        if (!container) return;
        STATS.forEach((s) => {
            const el = document.createElement('div');
            el.className = 'landing-stat';
            el.innerHTML = `
                <span class="stat-value" data-target="${s.value}" data-prefix="${s.prefix}" data-suffix="${s.suffix}">
                    ${s.prefix}0${s.suffix}
                </span>
                <span class="stat-label">${s.label}</span>
            `;
            container.appendChild(el);
        });
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // BUILD FEATURE CARDS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    function buildFeatureCards() {
        const container = document.getElementById('landing-features');
        if (!container) return;

        FEATURES.forEach((f, i) => {
            const card = document.createElement('div');
            card.className = 'landing-feature-card';
            card.dataset.demo = f.demo;
            card.dataset.idx = i;
            card.dataset.feature = f.feature; // Map card → sidebar section

            let demoHtml = '';
            if (f.demo === 'chat' || f.demo === 'typing') {
                demoHtml = `<div class="card-demo"><div class="card-demo-text" id="demo-text-${i}"></div></div>`;
            } else if (f.demo === 'bars') {
                const heights = [55, 80, 40, 95, 65];
                const bars = heights.map(h =>
                    `<div class="mini-bar" style="height:${h}%;"></div>`
                ).join('');
                demoHtml = `<div class="card-demo"><div class="mini-bars">${bars}</div></div>`;
            } else if (f.demo === 'progress') {
                const circum = 88;
                const val = f.progressValue || 70;
                const offset = circum - (circum * val / 100);
                demoHtml = `
                    <div class="card-demo progress-ring-wrap">
                        <svg width="42" height="42" viewBox="0 0 42 42">
                            <circle cx="21" cy="21" r="14" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="4"/>
                            <circle class="progress-ring" cx="21" cy="21" r="14" fill="none"
                                stroke-dasharray="${circum}" stroke-dashoffset="${circum}"
                                stroke="var(--card-color, #8b5cf6)" stroke-width="4" stroke-linecap="round"
                                id="progress-ring-${i}"/>
                        </svg>
                        <span style="position:absolute;font-size:10px;font-weight:700;color:#f1f5f9;">${val}%</span>
                    </div>`;
            } else if (f.demo === 'chart') {
                demoHtml = `<div class="card-demo"><div class="mini-bars">
                    <div class="mini-bar" style="height:60%;background:#10a37f;"></div>
                    <div class="mini-bar" style="height:85%;background:#3b82f6;"></div>
                    <div class="mini-bar" style="height:45%;background:#8b5cf6;"></div>
                    <div class="mini-bar" style="height:100%;background:#f59e0b;"></div>
                    <div class="mini-bar" style="height:70%;background:#ec4899;"></div>
                </div></div>`;
            } else if (f.demo === 'badge') {
                demoHtml = `<div class="card-demo" style="justify-content:center;gap:4px;">
                    <span style="font-size:10px;font-weight:700;padding:2px 7px;border-radius:8px;background:rgba(6,182,212,0.15);color:#06b6d4;border:1px solid rgba(6,182,212,0.25);">Round 1</span>
                    <span style="font-size:10px;font-weight:700;padding:2px 7px;border-radius:8px;background:rgba(6,182,212,0.15);color:#06b6d4;border:1px solid rgba(6,182,212,0.25);">Round 2</span>
                    <span style="font-size:10px;font-weight:700;padding:2px 7px;border-radius:8px;background:rgba(6,182,212,0.15);color:#06b6d4;border:1px solid rgba(6,182,212,0.25);">Mock</span>
                </div>`;
            }

            card.innerHTML = `
                <div class="card-icon-wrap">
                    <span>${f.icon}</span>
                    <div class="card-icon-pulse"></div>
                </div>
                <div class="card-title">${f.title}</div>
                <div class="card-tag">${f.tag}</div>
                ${demoHtml}
                <div class="card-explore-hint">Click to explore →</div>
            `;

            // ── Click handler: dismiss landing and navigate to section ──
            card.addEventListener('click', () => {
                const feature = f.feature;
                dismissLanding();
                // Wait for landing exit animation then navigate
                setTimeout(() => {
                    if (typeof SidebarComponent !== 'undefined' && SidebarComponent.showSection) {
                        SidebarComponent.showSection(feature);
                    }
                }, 750);
            });

            container.appendChild(card);
        });
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // BUILD MARQUEE
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    function buildMarquee() {
        const track = document.getElementById('landing-marquee');
        if (!track) return;
        // Double the items for seamless looping
        const allItems = [...MARQUEE_ITEMS, ...MARQUEE_ITEMS];
        allItems.forEach((item) => {
            const pill = document.createElement('div');
            pill.className = 'marquee-pill';
            pill.innerHTML = `<span>${item.icon}</span>${item.label}`;
            track.appendChild(pill);
        });
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // PARTICLE ENGINE (Canvas)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    let particleRAF = null;

    function initParticles() {
        const canvas = document.getElementById('landing-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);

        const N = Math.min(70, Math.floor(window.innerWidth / 18));
        const particles = Array.from({ length: N }, () => ({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4,
            r: Math.random() * 2 + 0.8,
            a: Math.random() * 0.5 + 0.15,
        }));

        const CONNECT_DIST = 130;

        function loop() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            particles.forEach((p) => {
                p.x += p.vx;
                p.y += p.vy;
                if (p.x < 0 || p.x > canvas.width) { p.vx *= -1; p.x = Math.max(0, Math.min(canvas.width, p.x)); }
                if (p.y < 0 || p.y > canvas.height) { p.vy *= -1; p.y = Math.max(0, Math.min(canvas.height, p.y)); }

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(16, 163, 127, ${p.a})`;
                ctx.fill();
            });

            // Draw connections
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < CONNECT_DIST) {
                        const alpha = (1 - dist / CONNECT_DIST) * 0.18;
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = `rgba(16, 163, 127, ${alpha})`;
                        ctx.lineWidth = 0.8;
                        ctx.stroke();
                    }
                }
            }

            particleRAF = requestAnimationFrame(loop);
        }
        loop();
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // TYPEWRITER ENGINE
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    let twIdx = 0;
    let twCharIdx = 0;
    let twDeleting = false;
    let twTimeout = null;

    function runTypewriter() {
        const el = document.getElementById('landing-typewriter');
        if (!el) return;

        const phrase = TYPEWRITER_PHRASES[twIdx];
        const cursor = '<span class="tw-cursor"></span>';

        function tick() {
            if (!document.getElementById('landing-screen')) {
                clearTimeout(twTimeout);
                return;
            }

            if (!twDeleting) {
                twCharIdx++;
                el.innerHTML = phrase.slice(0, twCharIdx) + cursor;
                if (twCharIdx >= phrase.length) {
                    twDeleting = true;
                    twTimeout = setTimeout(tick, 2200);
                    return;
                }
                twTimeout = setTimeout(tick, 55);
            } else {
                twCharIdx--;
                el.innerHTML = phrase.slice(0, twCharIdx) + cursor;
                if (twCharIdx <= 0) {
                    twDeleting = false;
                    twIdx = (twIdx + 1) % TYPEWRITER_PHRASES.length;
                    twTimeout = setTimeout(tick, 320);
                    return;
                }
                twTimeout = setTimeout(tick, 28);
            }
        }
        tick();
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // COUNTER ANIMATION
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    function animateCounters() {
        const els = document.querySelectorAll('#landing-stats .stat-value');
        els.forEach((el) => {
            const target = parseInt(el.dataset.target, 10);
            const prefix = el.dataset.prefix || '';
            const suffix = el.dataset.suffix || '';
            const duration = 1800;
            const startTime = performance.now();

            function easeOut(t) {
                return 1 - Math.pow(1 - t, 3);
            }

            function update(now) {
                const elapsed = now - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const current = Math.floor(easeOut(progress) * target);
                const formatted = current >= 1000
                    ? (current >= 100000 ? Math.round(current / 1000) + 'K' : current.toLocaleString('en-IN'))
                    : current;
                el.textContent = prefix + formatted + suffix;
                if (progress < 1) {
                    requestAnimationFrame(update);
                } else {
                    const finalFormatted = target >= 1000
                        ? (target >= 100000 ? Math.round(target / 1000) + 'K' : target.toLocaleString('en-IN'))
                        : target;
                    el.textContent = prefix + finalFormatted + suffix;
                }
            }
            requestAnimationFrame(update);
        });
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // CARD DEMO TYPEWRITERS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    function initCardDemos() {
        FEATURES.forEach((f, i) => {
            if ((f.demo === 'chat' || f.demo === 'typing') && f.demoTexts) {
                const textEl = document.getElementById(`demo-text-${i}`);
                if (!textEl) return;
                let idx = 0;
                let charIdx = 0;

                function tick() {
                    if (!document.getElementById('landing-screen')) return;
                    const phrase = f.demoTexts[idx];
                    charIdx++;
                    textEl.textContent = phrase.slice(0, charIdx);
                    if (charIdx >= phrase.length) {
                        idx = (idx + 1) % f.demoTexts.length;
                        charIdx = 0;
                        setTimeout(tick, 2000);
                        return;
                    }
                    setTimeout(tick, Math.random() * 40 + 30);
                }
                setTimeout(tick, 600 + i * 300);
            }

            // Animate progress ring
            if (f.demo === 'progress') {
                const ring = document.getElementById(`progress-ring-${i}`);
                if (ring) {
                    const circumference = 88;
                    const target = f.progressValue || 70;
                    const targetOffset = circumference - (circumference * target / 100);
                    let startTime = null;

                    function animateRing(now) {
                        if (!startTime) startTime = now;
                        const t = Math.min((now - startTime) / 1500, 1);
                        const ease = 1 - Math.pow(1 - t, 3);
                        ring.style.strokeDashoffset = circumference - (ease * (circumference - targetOffset));
                        if (t < 1) requestAnimationFrame(animateRing);
                    }
                    setTimeout(() => requestAnimationFrame(animateRing), 800);
                }
            }
        });
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // DISMISS LANDING
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    function dismissLanding() {
        const landing = document.getElementById('landing-screen');
        if (!landing) return;

        // Stop particle loop
        if (particleRAF) {
            cancelAnimationFrame(particleRAF);
            particleRAF = null;
        }
        clearTimeout(twTimeout);

        // Animate out
        landing.classList.add('exit');
        setTimeout(() => {
            landing.remove();

            // Show main app
            const appContent = document.getElementById('app-content');
            if (appContent) {
                appContent.style.display = '';
                appContent.style.opacity = '0';
                appContent.style.transition = 'opacity 0.4s ease';
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        appContent.style.opacity = '1';
                    });
                });
                setTimeout(() => {
                    appContent.style.transition = '';
                    appContent.style.opacity = '';
                }, 500);
            }
        }, 700);
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // EVENT LISTENERS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    function bindEvents() {
        const enterBtn = document.getElementById('landing-enter');
        const skipBtn = document.getElementById('landing-skip');

        if (enterBtn) {
            enterBtn.addEventListener('click', dismissLanding);
            enterBtn.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') dismissLanding();
            });
        }
        if (skipBtn) {
            skipBtn.addEventListener('click', dismissLanding);
        }

        // Keyboard shortcut: press Enter or Space anywhere on landing
        document.addEventListener('keydown', function onKey(e) {
            if (!document.getElementById('landing-screen')) {
                document.removeEventListener('keydown', onKey);
                return;
            }
            if (e.key === 'Enter') dismissLanding();
        });
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // INIT
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    function showAppContent() {
        const appContent = document.getElementById('app-content');
        if (appContent) {
            appContent.style.display = '';
        }
    }

    function init() {
        // Skip if already seen this session
        if (sessionStorage.getItem('ir_landing_seen')) {
            showAppContent(); // Still need to reveal the app
            return;
        }

        // Build & insert landing
        buildLanding();
        buildStats();
        buildFeatureCards();
        buildMarquee();

        // Start animations after a tiny delay to ensure DOM is painted
        requestAnimationFrame(() => {
            initParticles();
            bindEvents();
            setTimeout(runTypewriter, 600);
            setTimeout(animateCounters, 700);
            setTimeout(initCardDemos, 800);
        });

        // Mark as seen for this session
        sessionStorage.setItem('ir_landing_seen', '1');
    }

    // Run as early as possible (before DOMContentLoaded ensures faster load)
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
