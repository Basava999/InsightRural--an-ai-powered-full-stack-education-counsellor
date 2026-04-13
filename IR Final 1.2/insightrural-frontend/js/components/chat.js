// chat.js — ChatGPT-Style AI Chat Component for InsightRural
// Premium streaming, rich markdown, message actions, stop button, smart scroll

const ChatComponent = {
    isStreaming: false,
    abortController: null,
    lastUserMessage: '',
    lastAIBubble: null,

    init() {
        this.chatInput  = document.getElementById('chat-input');
        this.sendBtn    = document.getElementById('send-btn');
        this.stopBtn    = document.getElementById('chat-stop-btn');
        this.msgContainer = document.getElementById('messages-container');

        this.setupEventListeners();
        this.setupAutoResize();

        const history = AppState.getChatHistory();
        if (history && history.length > 0) {
            this.loadChatHistory();
        } else {
            this.renderWelcome();
        }

        this.checkAIStatus();
    },

    // ─── Welcome Hero ─────────────────────────────────────────────────────────
    renderWelcome() {
        const hero = document.createElement('div');
        hero.className = 'ir-welcome';
        hero.id = 'ir-welcome';

        const chips = [
            { emoji: '🏛️', text: 'Which college can I get with rank 5000 in CSE?' },
            { emoji: '💰', text: 'What scholarships are available for SC students?' },
            { emoji: '📊', text: 'Compare RVCE vs MSRIT for Computer Science' },
            { emoji: '🏠', text: 'What are hostel options near BMSCE?' },
            { emoji: '🏦', text: 'How do I apply for an education loan?' },
            { emoji: '📋', text: 'Explain the KEA KCET counseling process' }
        ];

        hero.innerHTML = `
            <div class="ir-welcome-logo">IR</div>
            <h2 class="ir-welcome-heading">How can I help you today?</h2>
            <p class="ir-welcome-sub">I'm InsightRural AI — your personal guide for KCET counseling, colleges, scholarships & more.</p>
            <div class="ir-chips-wrapper">
                <p class="ir-chips-label">✨ Try asking me:</p>
                <div class="ir-chips">
                    ${chips.map(c => `
                        <button class="ir-chip" data-query="${c.text}">
                            <span class="ir-chip-emoji">${c.emoji}</span>
                            <span>${c.text}</span>
                        </button>`).join('')}
                </div>
            </div>`;

        hero.querySelectorAll('.ir-chip').forEach(btn => {
            btn.addEventListener('click', () => {
                this.chatInput.value = btn.dataset.query;
                this.sendBtn.disabled = false;
                hero.remove();
                this.sendMessage();
            });
        });

        this.msgContainer.appendChild(hero);
    },

    // ─── AI Status Bar ───────────────────────────────────────────────────────
    async checkAIStatus() {
        try {
            const res  = await fetch(`${API_BASE_URL}/api/ai/status`);
            const data = await res.json();
            this.renderStatusBar(data);
        } catch {
            this.renderStatusBar({ ai_modules_available: false });
        }
    },

    renderStatusBar(status) {
        document.getElementById('ai-status-bar')?.remove();
        const bar    = document.createElement('div');
        bar.id       = 'ai-status-bar';
        bar.className = 'ir-status-bar';
        const online = status.ai_modules_available;
        bar.innerHTML = `
            <span class="ir-status-dot ${online ? 'online' : 'offline'}"></span>
            <span>${online ? '🧠 InsightRural AI · Ollama LLaMA 3' : '⚠️ Offline Mode'}</span>
            ${status.rag_indexed ? '<span class="ir-status-tag">📚 RAG Active</span>' : ''}
            <span class="ir-status-right">InsightRural v2.5</span>`;
        this.msgContainer.parentNode.insertBefore(bar, this.msgContainer);
    },

    // ─── Event Listeners ─────────────────────────────────────────────────────
    setupEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        if (this.stopBtn) {
            this.stopBtn.addEventListener('click', () => this.stopStreaming());
        }

        this.chatInput.addEventListener('keydown', e => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.sendMessage(); }
        });

        this.chatInput.addEventListener('input', () => {
            this.sendBtn.disabled = !this.chatInput.value.trim() || this.isStreaming;
            this.autoResize();
        });

        // Send button icon (arrow-up)
        this.sendBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M12 19V5M5 12l7-7 7 7"
                    stroke="currentColor" stroke-width="2.5"
                    stroke-linecap="round" stroke-linejoin="round"/>
            </svg>`;

        // Stop button icon (square)
        if (this.stopBtn) {
            this.stopBtn.innerHTML = `
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                    <rect x="4" y="4" width="16" height="16" rx="2"/>
                </svg>`;
        }
    },

    setupAutoResize() { this.autoResize(); },
    autoResize() {
        this.chatInput.style.height = 'auto';
        this.chatInput.style.height = Math.min(this.chatInput.scrollHeight, 200) + 'px';
    },

    // ─── Stop Streaming ───────────────────────────────────────────────────────
    stopStreaming() {
        if (this.abortController) {
            this.abortController.abort();
            this.abortController = null;
        }
        this.hideStopButton();
        this.isStreaming = false;
        this.sendBtn.disabled = !this.chatInput.value.trim();
    },

    showStopButton() {
        if (!this.stopBtn) return;
        this.sendBtn.style.display  = 'none';
        this.stopBtn.style.display  = 'flex';
    },

    hideStopButton() {
        if (!this.stopBtn) return;
        this.stopBtn.style.display  = 'none';
        this.sendBtn.style.display  = 'flex';
    },

    // ─── Send Message ─────────────────────────────────────────────────────────
    async sendMessage() {
        const msg = this.chatInput.value.trim();
        if (!msg || this.isStreaming) return;

        document.getElementById('ir-welcome')?.remove();

        this.lastUserMessage = msg;
        this.appendBubble('user', msg);
        AppState.addMessage('user', msg);

        this.chatInput.value = '';
        this.sendBtn.disabled = true;
        this.autoResize();

        this.isStreaming = true;
        this.showStopButton();
        this.showThinkingBubble();

        await this.fetchAIResponse(msg);
    },

    // ─── AI Response ──────────────────────────────────────────────────────────
    async fetchAIResponse(userMsg) {
        const profile     = AppState.getProfile() || {};
        const chatHistory = (AppState.getChatHistory() || []).slice(-8).map(m => ({
            role:    m.sender === 'ai' ? 'assistant' : 'user',
            content: m.content
        }));

        this.abortController = new AbortController();

        try {
            const res = await fetch(`${API_BASE_URL}/api/chat/stream`, {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ message: userMsg, profile, history: chatHistory }),
                signal:  this.abortController.signal
            });

            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            await this.readStream(res);

        } catch (err) {
            if (err.name === 'AbortError') {
                // User stopped — finalise current bubble
                this.removeThinkingBubble();
                if (this.lastAIBubble) {
                    const textEl = this.lastAIBubble.querySelector('.ir-bubble.ir-ai-bubble.ir-prose');
                    if (textEl) {
                        const cur = textEl.querySelector('.ir-cursor');
                        if (cur) cur.remove();
                        this.attachMessageActions(this.lastAIBubble);
                    }
                }
            } else {
                // Fallback to non-streaming
                console.warn('Stream failed, trying non-streaming…', err);
                try {
                    this.abortController = new AbortController();
                    const res2 = await fetch(`${API_BASE_URL}/api/chat`, {
                        method:  'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body:    JSON.stringify({ message: userMsg, profile, history: chatHistory, session_id: AppState.getSessionId() }),
                        signal:  this.abortController.signal
                    });
                    const data  = await res2.json();
                    this.removeThinkingBubble();
                    const text  = data.response || data.error || 'Sorry, something went wrong.';
                    const bubble = this.appendBubble('ai', text);
                    AppState.addMessage('ai', text);
                } catch (err2) {
                    if (err2.name === 'AbortError') return;
                    this.removeThinkingBubble();
                    const fallback = this.buildFallback(userMsg);
                    this.appendBubble('ai', fallback);
                    AppState.addMessage('ai', fallback);
                }
            }
        } finally {
            this.isStreaming     = false;
            this.abortController = null;
            this.hideStopButton();
            this.sendBtn.disabled = !this.chatInput.value.trim();
        }
    },

    async readStream(response) {
        this.removeThinkingBubble();

        const { bubble, textEl, timeEl, modelEl } = this.createAIBubble();
        this.lastAIBubble = bubble;
        this.msgContainer.appendChild(bubble);
        this.scrollToBottom();

        const reader  = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText  = '';
        let buffer    = '';
        let finished  = false;

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // keep incomplete line

                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    try {
                        const data = JSON.parse(line.slice(6));

                        if (data.model && modelEl) {
                            modelEl.textContent = '🧠 ' + data.model;
                            modelEl.style.display = 'inline-flex';
                        }
                        if (data.chunk) {
                            fullText += data.chunk;
                            textEl.innerHTML = this.renderMarkdown(fullText) + '<span class="ir-cursor"></span>';
                            this.smartScroll();
                        }
                        if (data.done) {
                            finished = true;
                            textEl.innerHTML = this.renderMarkdown(fullText);
                            timeEl.textContent = this.getTime();
                            if (data.model && modelEl) modelEl.textContent = '✨ ' + data.model;
                            this.attachCopyButtons(bubble);
                            this.attachMessageActions(bubble);
                            AppState.addMessage('ai', fullText);
                        }
                    } catch { /* ignore parse errors */ }
                }
            }
        } catch (err) {
            if (err.name === 'AbortError') throw err; // re-throw for caller
        }

        // Finalise if stream ended without explicit done event
        if (!finished && fullText) {
            textEl.innerHTML = this.renderMarkdown(fullText);
            timeEl.textContent = this.getTime();
            this.attachCopyButtons(bubble);
            this.attachMessageActions(bubble);
            AppState.addMessage('ai', fullText);
        }
    },

    // ─── Bubble Builders ──────────────────────────────────────────────────────
    appendBubble(role, content) {
        if (role === 'user') {
            const bubble = document.createElement('div');
            bubble.className = 'ir-message ir-user';
            bubble.innerHTML = `
                <div class="ir-avatar ir-user-avatar">You</div>
                <div class="ir-bubble-wrap">
                    <div class="ir-bubble ir-user-bubble">${this.escapeHtml(content)}</div>
                    <div class="ir-time">${this.getTime()}</div>
                </div>`;
            this.msgContainer.appendChild(bubble);
            this.scrollToBottom();
            return bubble;
        }

        const { bubble, textEl, timeEl } = this.createAIBubble();
        textEl.innerHTML = this.renderMarkdown(content);
        timeEl.textContent = this.getTime();
        this.msgContainer.appendChild(bubble);
        this.attachCopyButtons(bubble);
        this.attachMessageActions(bubble);
        this.scrollToBottom();
        return bubble;
    },

    createAIBubble() {
        const bubble  = document.createElement('div');
        bubble.className = 'ir-message ir-ai';

        const modelEl = document.createElement('div');
        modelEl.className = 'ir-model-badge';
        modelEl.style.display = 'none';

        const textEl  = document.createElement('div');
        textEl.className = 'ir-bubble ir-ai-bubble ir-prose';

        const timeEl  = document.createElement('div');
        timeEl.className = 'ir-time';

        const actionsEl = document.createElement('div');
        actionsEl.className = 'ir-msg-actions';

        const wrap = document.createElement('div');
        wrap.className = 'ir-bubble-wrap';
        wrap.appendChild(modelEl);
        wrap.appendChild(textEl);
        wrap.appendChild(actionsEl);
        wrap.appendChild(timeEl);

        bubble.innerHTML = `<div class="ir-avatar ir-ai-avatar">IR</div>`;
        bubble.appendChild(wrap);

        return { bubble, textEl, timeEl, modelEl, actionsEl };
    },

    // ─── Message Actions Row ──────────────────────────────────────────────────
    attachMessageActions(bubble) {
        const actionsEl = bubble.querySelector('.ir-msg-actions');
        if (!actionsEl || actionsEl.hasChildNodes()) return;

        // Copy response
        const copyBtn = document.createElement('button');
        copyBtn.className = 'ir-action-btn';
        copyBtn.title = 'Copy response';
        copyBtn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none">
            <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="2"/>
            <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" stroke="currentColor" stroke-width="2"/>
        </svg> Copy`;

        copyBtn.addEventListener('click', async () => {
            const textEl = bubble.querySelector('.ir-bubble.ir-prose');
            if (!textEl) return;
            try {
                await navigator.clipboard.writeText(textEl.innerText);
                copyBtn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                    <path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg> Copied!`;
                copyBtn.classList.add('copied');
                setTimeout(() => {
                    copyBtn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                        <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="2"/>
                        <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" stroke="currentColor" stroke-width="2"/>
                    </svg> Copy`;
                    copyBtn.classList.remove('copied');
                }, 2200);
            } catch { copyBtn.textContent = 'Error'; }
        });

        // Thumbs up
        const thumbBtn = document.createElement('button');
        thumbBtn.className = 'ir-action-btn';
        thumbBtn.title = 'Good response';
        thumbBtn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none">
            <path d="M14 9V5a3 3 0 00-3-3l-4 9v11h11.28a2 2 0 002-1.7l1.38-9a2 2 0 00-2-2.3H14z"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 22H4a2 2 0 01-2-2v-7a2 2 0 012-2h3"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>`;
        thumbBtn.addEventListener('click', () => {
            thumbBtn.style.color = '#10a37f';
        });

        // Regenerate
        const regenBtn = document.createElement('button');
        regenBtn.className = 'ir-action-btn';
        regenBtn.title = 'Regenerate response';
        regenBtn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none">
            <path d="M1 4v6h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M3.51 15a9 9 0 102.13-9.36L1 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg> Regenerate`;
        regenBtn.addEventListener('click', () => this.regenerate(bubble));

        actionsEl.appendChild(copyBtn);
        actionsEl.appendChild(thumbBtn);
        actionsEl.appendChild(regenBtn);
    },

    // ─── Regenerate ──────────────────────────────────────────────────────────
    async regenerate(oldBubble) {
        if (this.isStreaming || !this.lastUserMessage) return;

        // Remove old AI bubble from DOM
        oldBubble?.remove();

        this.isStreaming = true;
        this.showStopButton();
        this.showThinkingBubble();

        await this.fetchAIResponse(this.lastUserMessage);
    },

    // ─── Thinking Indicator ──────────────────────────────────────────────────
    showThinkingBubble() {
        const el = document.createElement('div');
        el.id = 'ir-thinking';
        el.className = 'ir-message ir-ai';
        el.innerHTML = `
            <div class="ir-avatar ir-ai-avatar">IR</div>
            <div class="ir-bubble-wrap">
                <div class="ir-bubble ir-ai-bubble">
                    <div class="ir-dots"><span></span><span></span><span></span></div>
                </div>
            </div>`;
        this.msgContainer.appendChild(el);
        this.scrollToBottom();
    },
    removeThinkingBubble() {
        document.getElementById('ir-thinking')?.remove();
    },

    // ─── Markdown Renderer ───────────────────────────────────────────────────
    renderMarkdown(text) {
        if (!text) return '';
        let t = text;

        // Fenced code blocks
        t = t.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
            const escaped = this.escapeHtml(code.trim());
            return `<div class="ir-code-block">
                <div class="ir-code-header">
                    <span class="ir-code-lang">${lang || 'code'}</span>
                    <button class="ir-copy-code" data-code="${encodeURIComponent(code.trim())}">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                            <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="2"/>
                            <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" stroke="currentColor" stroke-width="2"/>
                        </svg> Copy
                    </button>
                </div>
                <pre><code>${escaped}</code></pre>
            </div>`;
        });

        // Inline code
        t = t.replace(/`([^`]+)`/g, '<code class="ir-inline-code">$1</code>');

        // Bold & italic
        t = t.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>');
        t = t.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        t = t.replace(/\*((?!\s).*?(?<!\s))\*/g, '<em>$1</em>');

        // Headers
        t = t.replace(/^### (.+)$/gm, '<h5 class="ir-h5">$1</h5>');
        t = t.replace(/^## (.+)$/gm,  '<h4 class="ir-h4">$1</h4>');
        t = t.replace(/^# (.+)$/gm,   '<h3 class="ir-h3">$1</h3>');

        // Horizontal rule
        t = t.replace(/^---+$/gm, '<hr class="ir-hr">');

        // Blockquote
        t = t.replace(/^> (.+)$/gm, '<blockquote class="ir-bq">$1</blockquote>');

        // Markdown tables
        t = t.replace(/((?:^\|.+\|\s*\n)+)/gm, match => {
            const lines = match.trim().split('\n').filter(l => l.trim());
            if (lines.length < 2) return match;
            if (!/^\|[\s:|\\-]+\|$/.test(lines[1].trim())) return match;

            const parseRow = line => line.split('|').slice(1, -1).map(c => c.trim());
            const headers  = parseRow(lines[0]);
            const dataRows = lines.slice(2).map(parseRow);

            const thHtml = headers.map(h => `<th>${h}</th>`).join('');
            const trHtml = dataRows.map(row =>
                `<tr>${row.map(c => `<td>${c}</td>`).join('')}</tr>`
            ).join('');

            return `<div class="ir-table-wrap"><table class="ir-table">
                <thead><tr>${thHtml}</tr></thead>
                <tbody>${trHtml}</tbody>
            </table></div>`;
        });

        // Unordered lists
        t = t.replace(/(^[-•*] .+$(\n[-•*] .+$)*)/gm, match => {
            const items = match.split('\n').map(l => `<li>${l.replace(/^[-•*] /, '')}</li>`).join('');
            return `<ul class="ir-ul">${items}</ul>`;
        });

        // Ordered lists
        t = t.replace(/(^\d+\. .+$(\n\d+\. .+$)*)/gm, match => {
            const items = match.split('\n').map(l => `<li>${l.replace(/^\d+\. /, '')}</li>`).join('');
            return `<ol class="ir-ol">${items}</ol>`;
        });

        // Markdown links
        t = t.replace(/\[([^\]]+)\]\(([^)]+)\)/g,
            '<a href="$2" target="_blank" rel="noopener" class="ir-link">$1</a>');

        // Auto-links for known portals
        t = t.replace(/(ssp\.postmatric\.karnataka\.gov\.in)/gi,
            '<a href="https://$1" target="_blank" class="ir-link">$1</a>');
        t = t.replace(/(cetonline\.karnataka\.gov\.in)/gi,
            '<a href="https://$1" target="_blank" class="ir-link">$1</a>');
        t = t.replace(/(vidyalakshmi\.co\.in)/gi,
            '<a href="https://www.$1" target="_blank" class="ir-link">$1</a>');

        // Special highlights
        t = t.replace(/₹([\d,]+)/g, '<span class="ir-rupee">₹$1</span>');
        t = t.replace(/\bRank:?\s*(\d[\d,]*)/gi, 'Rank: <strong class="ir-rank">$1</strong>');
        t = t.replace(/\bCutoff:?\s*(\d[\d,]*)/gi, 'Cutoff: <strong class="ir-cutoff">$1</strong>');

        // Paragraphs
        t = t.split(/\n{2,}/).map(para => {
            para = para.trim();
            if (!para) return '';
            if (/^<(h[1-6]|ul|ol|blockquote|pre|hr|div)/.test(para)) return para;
            return `<p>${para.replace(/\n/g, '<br>')}</p>`;
        }).join('\n');

        return t;
    },

    // ─── Copy-code Buttons ───────────────────────────────────────────────────
    attachCopyButtons(bubble) {
        bubble.querySelectorAll('.ir-copy-code').forEach(btn => {
            btn.addEventListener('click', async () => {
                try {
                    await navigator.clipboard.writeText(decodeURIComponent(btn.dataset.code));
                    btn.textContent = '✓ Copied!';
                    setTimeout(() => {
                        btn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                            <rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="2"/>
                            <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" stroke="currentColor" stroke-width="2"/>
                        </svg> Copy`;
                    }, 2000);
                } catch { btn.textContent = 'Error'; }
            });
        });
    },

    // ─── Smart Auto-scroll ────────────────────────────────────────────────────
    smartScroll() {
        const el   = this.msgContainer;
        const dist = el.scrollHeight - el.scrollTop - el.clientHeight;
        if (dist < 150) {
            el.scrollTop = el.scrollHeight;
        }
    },

    scrollToBottom() {
        this.msgContainer.scrollTop = this.msgContainer.scrollHeight;
    },

    // ─── Fallback Responses ───────────────────────────────────────────────────
    buildFallback(query) {
        const q = query.toLowerCase();
        if (/^(hi|hello|hey|namaste)/i.test(q))
            return `Hello! 👋 I'm **InsightRural AI**, your KCET counselor for Karnataka.\n\nShare your **rank, branch, and category** and I'll give you personalized college recommendations, scholarship info, and more!`;
        if (/college|rank|cutoff|kcet/.test(q))
            return `**Quick Reference — CSE Cutoffs 2024:**\n\n| College | GM | OBC | Approx. Fee |\n|---|---|---|---|\n| RVCE | ~593 | ~315 | ₹1.4L/yr |\n| PES | ~2154 | ~763 | ₹2.2L/yr |\n| BMSCE | ~2156 | ~925 | ₹1.6L/yr |\n| MSRIT | ~1850 | ~920 | ₹1.8L/yr |\n| SIT Tumkur | ~3200 | ~1650 | ₹90K/yr |\n\nShare your **KCET rank and category** for personalized results.`;
        if (/scholarship/.test(q))
            return `**Karnataka Post-Matric Scholarships:**\n\n- **SC/ST** (Income < ₹2.5L): Full fee reimbursement + ₹1200/month\n- **OBC Cat-1** (Income < ₹2.5L): Fee reimbursement + ₹20K allowance\n- **EWS/General** (Income < ₹8L): Partial fee support\n\n📎 Apply at: **ssp.postmatric.karnataka.gov.in**`;
        if (/loan/.test(q))
            return `**Education Loan Options:**\n\n- **SBI Student Loan**: Up to ₹15L @ 8.5% (8% for girls)\n- **CISS Subsidy**: Zero interest if income < ₹4.5L during study\n- **No collateral** up to ₹7.5L\n\nApply via: **vidyalakshmi.co.in**`;
        if (/hostel/.test(q))
            return `**Hostel Options:**\n\n- **RVCE**: ₹45,000/yr + mess\n- **BMSCE**: ₹40,000/yr + mess\n- **SC/ST Free Hostels**: Apply through Social Welfare Dept.\n- **PG in Bangalore**: ₹6,000–₹15,000/month`;
        return `I'm here to help! Ask me about:\n\n- 🏛️ **College Recommendations** (share your rank)\n- 💰 **Scholarships** (share your category)\n- 🏦 **Education Loans**\n- 🏠 **Hostels & Accommodation**\n- 📋 **KEA Counseling Process**`;
    },

    // ─── Helpers ─────────────────────────────────────────────────────────────
    escapeHtml(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
    },
    getTime() {
        return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    loadChatHistory() {
        AppState.getChatHistory().forEach(m => this.appendBubble(m.sender, m.content));
        // Track last user message for regenerate
        const history = AppState.getChatHistory();
        const lastUser = [...history].reverse().find(m => m.sender === 'user');
        if (lastUser) this.lastUserMessage = lastUser.content;
    },

    // Backward compatibility
    addMessage(role, content) {
        return this.appendBubble(role, content);
    }
};

window.ChatComponent = ChatComponent;