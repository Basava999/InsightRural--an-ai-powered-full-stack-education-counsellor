/**
 * ============================================================================
 * InsightRural — Cinematic Landing Experience
 * World-Class AI Admission Intelligence Platform
 * Inspired by: Apple, OpenAI, Stripe, Tesla, Vercel
 * ============================================================================
 */

(function () {
    'use strict';

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // INTELLIGENCE PILLARS DATA
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    const PILLARS = [
        { icon: '🏛️', title: 'College Intelligence', desc: 'AI-powered seat prediction with 98% accuracy' },
        { icon: '🎓', title: 'Scholarship Intelligence', desc: 'Auto-detect eligible scholarships & fee waivers' },
        { icon: '🧭', title: 'Career Intelligence', desc: '5-year roadmap with salary & growth projections' },
        { icon: '🧠', title: 'Risk Intelligence', desc: '11-dimension success & regret analysis' },
        { icon: '🚀', title: 'Future Intelligence', desc: 'ROI calculator, placement outlook & breakeven' },
    ];

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // TRUST SOURCES DATA
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    const TRUST_SOURCES = [
        { icon: '🏛️', name: 'KEA', desc: 'Karnataka Examinations Authority' },
        { icon: '📋', name: 'JoSAA', desc: 'Joint Seat Allocation Authority' },
        { icon: '⚕️', name: 'MCC', desc: 'Medical Counselling Committee' },
        { icon: '🎓', name: 'AICTE', desc: 'All India Council for Technical Education' },
        { icon: '🏫', name: 'UGC', desc: 'University Grants Commission' },
        { icon: '📊', name: 'NIRF', desc: 'National Institutional Ranking Framework' },
        { icon: '💰', name: 'NSP', desc: 'National Scholarship Portal' },
    ];

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // PROBLEM STATEMENTS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    const PROBLEMS = [
        { icon: '😰', text: 'Confusing counseling processes' },
        { icon: '❌', text: 'Wrong branch choices leading to regret' },
        { icon: '💸', text: 'Financial uncertainty & hidden fees' },
        { icon: '🤷', text: 'Missed scholarship opportunities' },
        { icon: '🔮', text: 'No clarity on career outcomes' },
    ];

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // STATS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    const STATS = [
        { value: 230000, label: 'Students Guided', prefix: '', suffix: '+' },
        { value: 200, label: 'Colleges Mapped', prefix: '', suffix: '+' },
        { value: 5, label: 'Cr Scholarships', prefix: '₹', suffix: '' },
        { value: 98, label: '% Accuracy', prefix: '', suffix: '%' },
    ];

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // AI CONVERSATION DATA
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    const AI_CONVERSATION = [
        {
            type: 'user',
            text: 'I got KCET rank 8500. What are my options?',
            delay: 800,
        },
        {
            type: 'typing',
            delay: 1500,
        },
        {
            type: 'ai',
            text: 'Based on your rank and 3-year cutoff trends, here are your personalized insights:',
            delay: 600,
        },
        {
            type: 'cards',
            cards: [
                { label: '🏛️ 12 Colleges', cls: 'chip-college' },
                { label: '🎓 3 Scholarships', cls: 'chip-scholarship' },
                { label: '🏠 Hostel Options', cls: 'chip-hostel' },
                { label: '🧭 Career Roadmap', cls: 'chip-career' },
                { label: '🧠 Risk Analysis', cls: 'chip-risk' },
            ],
            delay: 400,
        },
    ];

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // EMOTIONAL HEADLINES (rotate)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    const EMOTIONAL_HEADLINES = [
        '"Every student deserves <em>clarity</em> about their future."',
        '"Transforming <em>uncertainty</em> into opportunity."',
        '"Your future deserves <em>better guidance</em>."',
    ];

    let particleRAF = null;

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // BUILD THE COMPLETE LANDING HTML
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    function buildLanding() {
        const landing = document.createElement('div');
        landing.id = 'landing-screen';
        landing.setAttribute('role', 'main');

        landing.innerHTML = `
            <!-- Aurora Background -->
            <div class="landing-aurora">
                <div class="aurora-layer aurora-1"></div>
                <div class="aurora-layer aurora-2"></div>
                <div class="aurora-layer aurora-3"></div>
                <div class="aurora-layer aurora-4"></div>
            </div>

            <!-- Grid Overlay -->
            <div class="landing-grid"></div>

            <!-- Particle Canvas -->
            <canvas id="landing-canvas"></canvas>

            <!-- Skip Button -->
            <button id="landing-skip">Skip &#8594;</button>

            <!-- ═══════════════════════════════════════════
                 PHASE 1: LOGO REVEAL + WELCOME
                 ═══════════════════════════════════════════ -->
            <section class="landing-phase-logo">
                <div class="landing-logo-wrap">
                    <div class="landing-logo-glow"></div>
                    <img src="img/logo.jpg" alt="InsightRural Logo" class="landing-logo-img" />
                </div>

                <div class="landing-welcome-text">
                    <div class="landing-welcome-label">Welcome to</div>
                    <div class="landing-welcome-brand">InsightRural</div>
                    <div class="landing-welcome-sub">AI Admission Intelligence Platform</div>
                </div>

                <div class="landing-emotion">
                    <div class="landing-emotion-text" id="landing-emotion-text">
                        ${EMOTIONAL_HEADLINES[0]}
                    </div>
                </div>

                <div class="landing-scroll-hint" id="scroll-hint">
                    <span>Discover More</span>
                    <div class="scroll-arrow"></div>
                </div>
            </section>

            <!-- ═══════════════════════════════════════════
                 PHASE 2: HERO — INTELLIGENCE PILLARS
                 ═══════════════════════════════════════════ -->
            <section class="landing-phase-hero">
                <div class="hero-cinematic-title reveal">
                    <h2>Not a website. <span>An AI Counselor.</span></h2>
                    <p>Five pillars of intelligence working together to guide your most important decision.</p>
                </div>

                <div class="hero-pillars" id="hero-pillars">
                    ${PILLARS.map((p, i) => `
                        <div class="hero-pillar reveal reveal-delay-${i + 1}">
                            <span class="pillar-icon">${p.icon}</span>
                            <div class="pillar-title">${p.title}</div>
                            <div class="pillar-desc">${p.desc}</div>
                        </div>
                    `).join('')}
                </div>
            </section>

            <!-- ═══════════════════════════════════════════
                 PHASE 3: TRUST BUILDING
                 ═══════════════════════════════════════════ -->
            <section class="landing-phase-trust">
                <div class="trust-section-label reveal">Powered by Official Data</div>
                <div class="trust-section-title reveal">Trusted Sources. Verified Intelligence.</div>

                <div class="trust-grid" id="trust-grid">
                    ${TRUST_SOURCES.map((t, i) => `
                        <div class="trust-badge reveal reveal-delay-${(i % 5) + 1}">
                            <div class="trust-badge-icon">${t.icon}</div>
                            <div>
                                <div class="trust-badge-name">${t.name}</div>
                                <div class="trust-badge-desc">${t.desc}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </section>

            <!-- ═══════════════════════════════════════════
                 PHASE 4: AI SHOWCASE — LIVE PREVIEW
                 ═══════════════════════════════════════════ -->
            <section class="landing-phase-ai">
                <div class="trust-section-label reveal">Live AI Preview</div>
                <div class="trust-section-title reveal">See the Intelligence in Action</div>

                <div class="ai-showcase-window reveal">
                    <div class="ai-window-bar">
                        <div class="ai-window-dot"></div>
                        <div class="ai-window-dot"></div>
                        <div class="ai-window-dot"></div>
                        <div class="ai-window-title">InsightRural AI Counselor</div>
                    </div>
                    <div class="ai-chat-body" id="ai-chat-body"></div>
                </div>
            </section>

            <!-- ═══════════════════════════════════════════
                 PHASE 5: EMOTIONAL STORYTELLING
                 ═══════════════════════════════════════════ -->
            <section class="landing-phase-story">
                <div class="trust-section-label reveal">The Problem We Solve</div>
                <div class="trust-section-title reveal">Millions of students struggle with...</div>

                <div class="story-problem-grid" id="story-problems">
                    ${PROBLEMS.map((p, i) => `
                        <div class="story-problem-card reveal reveal-delay-${i + 1}">
                            <div class="story-problem-icon">${p.icon}</div>
                            <div class="story-problem-text">${p.text}</div>
                        </div>
                    `).join('')}
                </div>

                <div class="story-solution reveal">
                    <div class="story-solution-badge">
                        <span>&#10003;</span> Our AI Solves This
                    </div>
                    <h3>One platform. Complete clarity.</h3>
                    <p>InsightRural uses local AI, official government data, and 11-dimensional risk analysis to give every student — especially rural students — the guidance they deserve.</p>
                </div>
            </section>

            <!-- ═══════════════════════════════════════════
                 STATS SECTION
                 ═══════════════════════════════════════════ -->
            <section class="landing-stats-section">
                <div class="landing-stats" id="landing-stats"></div>
            </section>

            <!-- ═══════════════════════════════════════════
                 PHASE 6: FINAL CTA
                 ═══════════════════════════════════════════ -->
            <section class="landing-phase-cta">
                <div class="cta-headline reveal">Ready to discover your future?</div>
                <div class="cta-sub reveal">Join thousands of students who found their perfect college, scholarship, and career path.</div>

                <button class="landing-cta-btn reveal" id="landing-enter">
                    Get Started — It's Free
                    <span class="cta-arrow">&#8594;</span>
                </button>
                <div class="cta-hint reveal">No sign-up required &middot; Works offline &middot; 100% private</div>
            </section>
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
        STATS.forEach((s, i) => {
            const el = document.createElement('div');
            el.className = `landing-stat reveal reveal-delay-${i + 1}`;
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
    // PARTICLE ENGINE (Premium Canvas)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

        const N = Math.min(60, Math.floor(window.innerWidth / 22));
        const particles = Array.from({ length: N }, () => ({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.3,
            vy: (Math.random() - 0.5) * 0.3,
            r: Math.random() * 1.5 + 0.5,
            a: Math.random() * 0.4 + 0.1,
            color: ['16,163,127', '59,130,246', '139,92,246'][Math.floor(Math.random() * 3)],
        }));

        const CONNECT_DIST = 140;

        function loop() {
            if (!document.getElementById('landing-canvas')) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            particles.forEach((p) => {
                p.x += p.vx;
                p.y += p.vy;
                if (p.x < 0 || p.x > canvas.width) { p.vx *= -1; p.x = Math.max(0, Math.min(canvas.width, p.x)); }
                if (p.y < 0 || p.y > canvas.height) { p.vy *= -1; p.y = Math.max(0, Math.min(canvas.height, p.y)); }

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${p.color}, ${p.a})`;
                ctx.fill();
            });

            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < CONNECT_DIST) {
                        const alpha = (1 - dist / CONNECT_DIST) * 0.12;
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = `rgba(${particles[i].color}, ${alpha})`;
                        ctx.lineWidth = 0.6;
                        ctx.stroke();
                    }
                }
            }

            particleRAF = requestAnimationFrame(loop);
        }
        loop();
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // EMOTIONAL HEADLINE ROTATION
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    let emotionIdx = 0;
    let emotionInterval = null;

    function startEmotionRotation() {
        const el = document.getElementById('landing-emotion-text');
        if (!el) return;

        emotionInterval = setInterval(() => {
            if (!document.getElementById('landing-screen')) {
                clearInterval(emotionInterval);
                return;
            }
            el.style.opacity = '0';
            el.style.transform = 'translateY(10px)';
            setTimeout(() => {
                emotionIdx = (emotionIdx + 1) % EMOTIONAL_HEADLINES.length;
                el.innerHTML = EMOTIONAL_HEADLINES[emotionIdx];
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, 400);
        }, 4000);

        el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // AI CHAT SHOWCASE ANIMATION
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    let aiChatStarted = false;

    function startAIChatDemo() {
        if (aiChatStarted) return;
        aiChatStarted = true;

        const body = document.getElementById('ai-chat-body');
        if (!body) return;

        let totalDelay = 0;

        AI_CONVERSATION.forEach((item) => {
            totalDelay += item.delay;

            setTimeout(() => {
                if (!document.getElementById('landing-screen')) return;

                if (item.type === 'user') {
                    const msg = document.createElement('div');
                    msg.className = 'ai-msg ai-msg-user';
                    msg.textContent = item.text;
                    body.appendChild(msg);
                    body.scrollTop = body.scrollHeight;
                } else if (item.type === 'typing') {
                    const typing = document.createElement('div');
                    typing.className = 'ai-typing';
                    typing.id = 'ai-typing-indicator';
                    typing.innerHTML = '<div class="ai-typing-dot"></div><div class="ai-typing-dot"></div><div class="ai-typing-dot"></div>';
                    body.appendChild(typing);
                    body.scrollTop = body.scrollHeight;
                } else if (item.type === 'ai') {
                    // Remove typing indicator
                    const typing = document.getElementById('ai-typing-indicator');
                    if (typing) typing.remove();

                    const msg = document.createElement('div');
                    msg.className = 'ai-msg ai-msg-ai';
                    msg.textContent = item.text;
                    body.appendChild(msg);
                    body.scrollTop = body.scrollHeight;
                } else if (item.type === 'cards') {
                    const wrap = document.createElement('div');
                    wrap.className = 'ai-response-cards';
                    item.cards.forEach((card, ci) => {
                        setTimeout(() => {
                            if (!document.getElementById('landing-screen')) return;
                            const chip = document.createElement('div');
                            chip.className = `ai-card-chip ${card.cls}`;
                            chip.textContent = card.label;
                            wrap.appendChild(chip);
                        }, ci * 200);
                    });
                    body.appendChild(wrap);
                    body.scrollTop = body.scrollHeight;
                }
            }, totalDelay);
        });
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // COUNTER ANIMATION
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    let countersAnimated = false;

    function animateCounters() {
        if (countersAnimated) return;
        countersAnimated = true;

        const els = document.querySelectorAll('#landing-stats .stat-value');
        els.forEach((el) => {
            const target = parseInt(el.dataset.target, 10);
            const prefix = el.dataset.prefix || '';
            const suffix = el.dataset.suffix || '';
            const duration = 2000;
            const startTime = performance.now();

            function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

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
    // INTERSECTION OBSERVER — Scroll Reveals
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    function initScrollReveals() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');

                    // Trigger AI chat when showcase is visible
                    if (entry.target.closest('.landing-phase-ai')) {
                        startAIChatDemo();
                    }

                    // Trigger counter animation when stats visible
                    if (entry.target.closest('.landing-stats-section')) {
                        animateCounters();
                    }
                }
            });
        }, {
            threshold: 0.15,
            rootMargin: '0px 0px -50px 0px',
        });

        document.querySelectorAll('.reveal').forEach((el) => {
            observer.observe(el);
        });
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // DISMISS LANDING (Cinematic Exit)
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    function dismissLanding() {
        const landing = document.getElementById('landing-screen');
        if (!landing) return;

        // Stop animations
        if (particleRAF) {
            cancelAnimationFrame(particleRAF);
            particleRAF = null;
        }
        if (emotionInterval) clearInterval(emotionInterval);

        // Cinematic exit
        landing.classList.add('exit');

        setTimeout(() => {
            landing.remove();

            // Reveal main app with smooth entrance
            const appContent = document.getElementById('app-content');
            if (appContent) {
                appContent.style.display = '';
                appContent.style.opacity = '0';
                appContent.style.transform = 'scale(0.98)';
                appContent.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        appContent.style.opacity = '1';
                        appContent.style.transform = 'scale(1)';
                    });
                });
                setTimeout(() => {
                    appContent.style.transition = '';
                    appContent.style.opacity = '';
                    appContent.style.transform = '';
                }, 700);
            }
        }, 1000);
    }

    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    // EVENT LISTENERS
    // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    function bindEvents() {
        const enterBtn = document.getElementById('landing-enter');
        const skipBtn = document.getElementById('landing-skip');
        const scrollHint = document.getElementById('scroll-hint');

        if (enterBtn) {
            enterBtn.addEventListener('click', dismissLanding);
        }
        if (skipBtn) {
            skipBtn.addEventListener('click', dismissLanding);
        }
        if (scrollHint) {
            scrollHint.addEventListener('click', () => {
                const hero = document.querySelector('.landing-phase-hero');
                if (hero) hero.scrollIntoView({ behavior: 'smooth' });
            });
        }

        // Keyboard: Enter to dismiss
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
            showAppContent();
            return;
        }

        // Build landing
        buildLanding();
        buildStats();

        // Start animations
        requestAnimationFrame(() => {
            initParticles();
            bindEvents();
            initScrollReveals();
            setTimeout(startEmotionRotation, 2000);
        });

        // Mark as seen
        sessionStorage.setItem('ir_landing_seen', '1');
    }

    // Run ASAP
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
