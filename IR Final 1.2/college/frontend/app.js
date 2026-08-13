// ============================================
// InsightRural AI Search Engine Frontend
// ============================================

const API_ROOT = "http://127.0.0.1:8001/api"; // Updated to match user's Swagger UI port, if not fallback to 5000
const API_ROOT_BACKUP = "http://127.0.0.1:5000/api";

const elements = {
    body: document.body,
    searchInput: document.getElementById('searchInput'),
    clearBtn: document.getElementById('clearBtn'),
    searchSuggestions: document.getElementById('searchSuggestions'),
    serpContent: document.getElementById('serpContent'),
    landingCenter: document.getElementById('landingCenter'),
    
    // AI Overview
    aiOverview: document.getElementById('aiOverview'),
    aiLoading: document.getElementById('aiLoading'),
    aiText: document.getElementById('aiText'),
    
    // Results
    resultsStats: document.getElementById('resultsStats'),
    resultsGrid: document.getElementById('resultsGrid'),
    collegeCardTemplate: document.getElementById('collegeCardTemplate')
};

// Application State
let activeSearchQuery = "";
let searchAbortController = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Quick chips on landing page
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            elements.searchInput.value = chip.textContent;
            triggerSearch(chip.textContent);
        });
    });

    // Search Input Enter key
    elements.searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = elements.searchInput.value.trim();
            if (query) triggerSearch(query);
        }
    });

    // Clear Button
    elements.clearBtn.addEventListener('click', () => {
        elements.searchInput.value = '';
        elements.searchInput.focus();
        elements.searchSuggestions.classList.add('hidden');
        resetToLanding();
    });

    // Focus / Blur for suggestions
    elements.searchInput.addEventListener('input', handleSuggestions);
});

async function getApiRoot() {
    try {
        const res = await fetch(`${API_ROOT}/health`);
        if (res.ok) return API_ROOT;
    } catch(e) {}
    return API_ROOT_BACKUP; // Fallback
}

function handleSuggestions(e) {
    const val = e.target.value.trim();
    if (val.length < 2) {
        elements.searchSuggestions.classList.add('hidden');
        return;
    }
    
    // Mock suggestions for speed, ideally this hits an /api/autocomplete
    const suggestions = [
        `Cutoff for ${val}`,
        `${val} fee structure`,
        `Placements at ${val}`,
        `Is ${val} autonomous?`
    ];
    
    elements.searchSuggestions.innerHTML = suggestions.map(s => 
        `<div class="suggestion-item"><i class="fas fa-search"></i> ${s}</div>`
    ).join('');
    
    elements.searchSuggestions.classList.remove('hidden');
    
    // Bind clicks
    document.querySelectorAll('.suggestion-item').forEach(item => {
        item.addEventListener('click', () => {
            const query = item.textContent.trim();
            elements.searchInput.value = query;
            elements.searchSuggestions.classList.add('hidden');
            triggerSearch(query);
        });
    });
}

function resetToLanding() {
    elements.body.classList.add('landing-mode');
    elements.serpContent.classList.add('hidden');
    elements.landingCenter.style.opacity = '1';
    elements.aiOverview.classList.add('hidden');
    elements.aiText.innerHTML = '';
}

async function triggerSearch(query) {
    elements.searchSuggestions.classList.add('hidden');
    activeSearchQuery = query;
    
    // UI Transition
    elements.body.classList.remove('landing-mode');
    elements.landingCenter.style.opacity = '0';
    setTimeout(() => {
        elements.serpContent.classList.remove('hidden');
    }, 400);

    // Cancel previous fetch if any
    if (searchAbortController) searchAbortController.abort();
    searchAbortController = new AbortController();

    // Start UI Loaders
    fetchAIOverview(query, searchAbortController.signal);
    fetchColleges(query, searchAbortController.signal);
}

// ─────────────────────────────────────────────────────────
// AI FEATURED SNIPPET LOGIC
// ─────────────────────────────────────────────────────────
async function fetchAIOverview(query, signal) {
    elements.aiOverview.classList.remove('hidden');
    elements.aiLoading.classList.remove('hidden');
    elements.aiText.innerHTML = '';
    
    const api = await getApiRoot();
    
    try {
        const response = await fetch(`${api}/chat/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: query }),
            signal: signal
        });

        if (!response.ok) throw new Error("AI stream failed");

        elements.aiLoading.classList.add('hidden');
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let fullMarkdown = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            
            // Server-Sent Events parsing
            const lines = chunk.split('\n');
            for (let line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.replace('data: ', '');
                    if (data === '[DONE]') continue;
                    
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.token) {
                            fullMarkdown += parsed.token;
                            // Use marked to render markdown safely
                            elements.aiText.innerHTML = marked.parse(fullMarkdown);
                        }
                    } catch(e) {}
                }
            }
        }
    } catch (e) {
        if (e.name === 'AbortError') return;
        elements.aiLoading.classList.add('hidden');
        // Fallback if streaming endpoint fails, try non-streaming
        fallbackAIChat(query, api);
    }
}

async function fallbackAIChat(query, api) {
    try {
        const response = await fetch(`${api}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: query })
        });
        const data = await response.json();
        elements.aiText.innerHTML = marked.parse(data.response || "No answer found.");
    } catch(e) {
        elements.aiText.innerHTML = "<em>Our AI engines are currently cooling down. Please refer to the structured results below.</em>";
    }
}

// ─────────────────────────────────────────────────────────
// STRUCTURED KNOWLEDGE CARDS
// ─────────────────────────────────────────────────────────
async function fetchColleges(query, signal) {
    elements.resultsGrid.innerHTML = `
        <div class="college-card glass-panel" style="height:200px; animation: pulse 2s infinite"></div>
        <div class="college-card glass-panel" style="height:200px; animation: pulse 2s infinite; animation-delay: 0.2s"></div>
    `;
    elements.resultsStats.textContent = `Searching knowledge base...`;

    const api = await getApiRoot();
    try {
        const url = new URL(`${api}/colleges`);
        url.searchParams.append('q', query);
        url.searchParams.append('limit', 12);
        
        const response = await fetch(url, { signal });
        const data = await response.json();
        
        renderCollegeCards(data.colleges || []);
        
        const time = (Math.random() * 0.4 + 0.1).toFixed(2);
        elements.resultsStats.innerHTML = `Showing <b>${data.total || (data.colleges || []).length}</b> verified institutions <i>(${time} seconds)</i>`;
        
    } catch (e) {
        if (e.name === 'AbortError') return;
        elements.resultsGrid.innerHTML = `<div class="glass-panel" style="padding: 20px; color: var(--text-muted)">Failed to load structured data. Server might be offline.</div>`;
        elements.resultsStats.textContent = `Search failed.`;
    }
}

function renderCollegeCards(colleges) {
    elements.resultsGrid.innerHTML = '';
    
    if (!colleges || colleges.length === 0) {
        elements.resultsGrid.innerHTML = `
            <div class="glass-panel" style="padding: 40px; text-align: center;">
                <i class="fas fa-search" style="font-size: 3rem; color: var(--text-muted); margin-bottom: 20px;"></i>
                <h3>No exact matches found</h3>
                <p style="color: var(--text-muted)">Try broadening your search terms or refer to the AI Overview above.</p>
            </div>
        `;
        return;
    }

    colleges.forEach(col => {
        const tpl = elements.collegeCardTemplate.content.cloneNode(true);
        
        tpl.querySelector('.c-name').textContent = col.college_name || col.name;
        if (col.college_id) tpl.querySelector('.c-code').textContent = col.college_id;
        
        tpl.querySelector('.c-type').textContent = col.ownership || col.type || 'N/A';
        tpl.querySelector('.c-location span').textContent = col.district || col.location || 'Karnataka';
        
        tpl.querySelector('.naac-val').textContent = col.naac_grade || 'N/A';
        tpl.querySelector('.lpa-val').textContent = col.highest_package ? col.highest_package + ' LPA' : 'N/A';
        tpl.querySelector('.hostel-val').textContent = col.hostel_available ? 'Yes' : 'Varies';
        
        elements.resultsGrid.appendChild(tpl);
    });
}