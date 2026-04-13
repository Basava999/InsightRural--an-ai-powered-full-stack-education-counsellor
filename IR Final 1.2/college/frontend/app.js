// ============================================
// COMPLETE WORKING VERSION
// ============================================

const API_ROOT = "http://127.0.0.1:5000/api";

// DOM elements
const elements = {
    searchBox: document.getElementById("searchBox"),
    suggestions: document.getElementById("suggestions"),
    results: document.getElementById("results"),
    branchFilter: document.getElementById("branchFilter"),
    locationFilter: document.getElementById("locationFilter"),
    collegeType: document.getElementById("collegeType"),
    clearBtn: document.getElementById("clearBtn"),
    pagination: document.getElementById("pagination"),
    detailModal: document.getElementById("detailModal"),
    detailBody: document.getElementById("detailBody"),
    closeModal: document.getElementById("closeModal"),
    loading: document.getElementById("loading"),
    emptyState: document.getElementById("emptyState"),
    totalColleges: document.getElementById("totalColleges"),
    totalLocations: document.getElementById("totalLocations"),
    totalBranches: document.getElementById("totalBranches"),
    resultsCount: document.getElementById("resultsCount")
};

// State
let currentState = {
    page: 1,
    query: "",
    branch: "",
    location: "",
    type: "",
    limit: 12
};

// Initialize the application
async function initializeApp() {
    console.log("🚀 Initializing InsightRural College Search...");
    
    // Show loading state
    elements.loading.style.display = 'block';
    
    try {
        // First, check if backend is running
        console.log("Checking backend connection...");
        const healthResponse = await fetch(`${API_ROOT}/health`);
        
        if (!healthResponse.ok) {
            throw new Error(`Backend not responding (Status: ${healthResponse.status})`);
        }
        
        const healthData = await healthResponse.json();
        console.log("Backend status:", healthData);
        
        // Load statistics
        console.log("Loading statistics...");
        await loadStatistics();
        
        // Load filters
        console.log("Loading filters...");
        await loadFilters();
        
        // Load initial data
        console.log("Loading initial data...");
        await search();
        
        // Setup event listeners
        setupEventListeners();
        
        console.log("✅ Application initialized successfully!");
        
    } catch (error) {
        console.error("❌ Initialization error:", error);
        showError(`Failed to initialize application: ${error.message}. Please ensure the Flask backend is running on port 5000.`);
    } finally {
        elements.loading.style.display = 'none';
    }
}

// Load statistics from API
async function loadStatistics() {
    try {
        console.log("Fetching statistics from:", `${API_ROOT}/statistics`);
        const response = await fetch(`${API_ROOT}/statistics`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch statistics: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log("Statistics data:", data);
        
        // Update UI with statistics
        elements.totalColleges.textContent = data.total_colleges || "0";
        elements.totalLocations.textContent = data.total_locations || "0";
        elements.totalBranches.textContent = data.total_branches || "0";
        
    } catch (error) {
        console.error("Error loading statistics:", error);
        // Set default values
        elements.totalColleges.textContent = "0";
        elements.totalLocations.textContent = "0";
        elements.totalBranches.textContent = "0";
    }
}

// Load branch and location filters
async function loadFilters() {
    try {
        // Load branches
        console.log("Fetching branches...");
        const branchesResponse = await fetch(`${API_ROOT}/branches`);
        
        if (!branchesResponse.ok) {
            throw new Error(`Failed to fetch branches: ${branchesResponse.status}`);
        }
        
        const branches = await branchesResponse.json();
        console.log("Branches loaded:", branches);
        
        // Populate branch filter
        let branchOptions = '<option value="">All Branches</option>';
        if (Array.isArray(branches)) {
            branchOptions += branches.map(branch => 
                `<option value="${escapeHtml(branch)}">${escapeHtml(branch)}</option>`
            ).join('');
        }
        elements.branchFilter.innerHTML = branchOptions;
        
        // Load locations
        console.log("Fetching locations...");
        const locationsResponse = await fetch(`${API_ROOT}/locations`);
        
        if (!locationsResponse.ok) {
            throw new Error(`Failed to fetch locations: ${locationsResponse.status}`);
        }
        
        const locations = await locationsResponse.json();
        console.log("Locations loaded:", locations);
        
        // Populate location filter
        let locationOptions = '<option value="">All Locations</option>';
        if (Array.isArray(locations)) {
            locationOptions += locations.map(location => 
                `<option value="${escapeHtml(location)}">${escapeHtml(location)}</option>`
            ).join('');
        }
        elements.locationFilter.innerHTML = locationOptions;
        
    } catch (error) {
        console.error("Error loading filters:", error);
        // Set fallback options
        elements.branchFilter.innerHTML = `
            <option value="">All Branches</option>
            <option value="CSE">Computer Science & Engineering</option>
            <option value="ECE">Electronics & Communication</option>
            <option value="EEE">Electrical & Electronics</option>
            <option value="ME">Mechanical Engineering</option>
            <option value="CV">Civil Engineering</option>
        `;
        
        elements.locationFilter.innerHTML = `
            <option value="">All Locations</option>
            <option value="Bangalore">Bangalore</option>
            <option value="Mysore">Mysore</option>
            <option value="Hubli">Hubli</option>
            <option value="Mangalore">Mangalore</option>
        `;
    }
}

// Main search function
async function search(page = 1) {
    currentState.page = page;
    
    // Show loading state
    elements.loading.style.display = 'block';
    elements.emptyState.classList.add('hidden');
    elements.results.innerHTML = '';
    
    // Build query parameters
    const params = new URLSearchParams();
    if (currentState.query) params.append('q', currentState.query);
    if (currentState.branch) params.append('branch', currentState.branch);
    if (currentState.location) params.append('location', currentState.location);
    if (currentState.type) params.append('type', currentState.type);
    params.append('page', currentState.page);
    params.append('limit', currentState.limit);
    
    const url = `${API_ROOT}/colleges?${params.toString()}`;
    console.log("Searching with URL:", url);
    
    try {
        const response = await fetch(url);
        console.log("Response status:", response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log("Search response data:", data);
        
        // Check for error in response
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Update results count
        elements.resultsCount.textContent = data.total || 0;
        
        // Hide loading
        elements.loading.style.display = 'none';
        
        // Check if we have results
        if (!data.items || data.items.length === 0) {
            elements.emptyState.classList.remove('hidden');
            elements.pagination.innerHTML = '';
            return;
        }
        
        // Render results
        renderResults(data.items);
        
        // Render pagination
        renderPagination(data.total, data.page, data.pages || 1);
        
    } catch (error) {
        console.error("❌ Search error:", error);
        elements.loading.style.display = 'none';
        
        // Show error message
        elements.results.innerHTML = `
            <div class="error-card">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Failed to load results</h3>
                <p>${escapeHtml(error.message)}</p>
                <p class="small">Check if:</p>
                <ul class="small">
                    <li>Backend server is running</li>
                    <li>Database is properly seeded</li>
                    <li>Check browser console for details</li>
                </ul>
                <button onclick="search()" class="btn-retry">
                    <i class="fas fa-redo"></i> Try Again
                </button>
            </div>
        `;
    }
}

// Render college results as cards
function renderResults(items) {
    console.log("Rendering", items.length, "colleges");
    
    const cards = items.map(item => {
        console.log("College item:", item);
        
        const branches = Array.isArray(item.branches) ? item.branches : [];
        const firstFewBranches = branches.slice(0, 3);
        const remaining = Math.max(0, branches.length - 3);
        
        return `
            <div class="college-card fade-in">
                <div class="college-header">
                    <h3 class="college-name">${escapeHtml(item.name || 'Unnamed College')}</h3>
                    <span class="college-type">${escapeHtml(item.type || 'N/A')}</span>
                </div>
                
                <div class="college-meta">
                    <div class="location">
                        <i class="fas fa-map-marker-alt"></i>
                        ${escapeHtml(item.location || 'Location not specified')}
                    </div>
                    
                    ${item.affiliation ? `
                        <div class="affiliation">
                            <i class="fas fa-certificate"></i>
                            ${escapeHtml(item.affiliation)}
                        </div>
                    ` : ''}
                    
                    <div class="${item.hostel_available ? 'hostel-badge' : 'hostel-badge unavailable'}">
                        <i class="fas fa-bed"></i>
                        ${item.hostel_available ? 'Hostel Available' : 'No Hostel'}
                    </div>
                </div>
                
                ${firstFewBranches.length > 0 ? `
                    <div class="branches-container">
                        ${firstFewBranches.map(branch => 
                            `<span class="branch-tag">${escapeHtml(branch)}</span>`
                        ).join('')}
                        ${remaining > 0 ? 
                            `<span class="branch-tag">+${remaining} more</span>` : ''
                        }
                    </div>
                ` : ''}
                
                <div class="college-actions">
                    <button class="btn-view" onclick="viewDetails('${item.college_id || item.id}')">
                        <i class="fas fa-eye"></i> View Details
                    </button>
                    ${item.fee_category ? `
                    <button class="btn-fee" onclick="viewFee('${escapeHtml(item.fee_category)}')">
                        <i class="fas fa-rupee-sign"></i> View Fee
                    </button>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
    
    elements.results.innerHTML = cards;
}

// Render pagination controls
function renderPagination(total, currentPage, totalPages) {
    if (totalPages <= 1) {
        elements.pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Previous button
    if (currentPage > 1) {
        html += `<button onclick="goToPage(${currentPage - 1})" class="pagination-btn" title="Previous page">
                    <i class="fas fa-chevron-left"></i>
                 </button>`;
    }
    
    // Page numbers
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    // Adjust start if we're near the end
    if (endPage - startPage + 1 < maxVisible) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    // First page and ellipsis
    if (startPage > 1) {
        html += `<button onclick="goToPage(1)" class="pagination-btn">1</button>`;
        if (startPage > 2) {
            html += `<span class="pagination-ellipsis">...</span>`;
        }
    }
    
    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
        html += `<button onclick="goToPage(${i})" class="pagination-btn ${i === currentPage ? 'active' : ''}">
                    ${i}
                 </button>`;
    }
    
    // Last page and ellipsis
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            html += `<span class="pagination-ellipsis">...</span>`;
        }
        html += `<button onclick="goToPage(${totalPages})" class="pagination-btn">${totalPages}</button>`;
    }
    
    // Next button
    if (currentPage < totalPages) {
        html += `<button onclick="goToPage(${currentPage + 1})" class="pagination-btn" title="Next page">
                    <i class="fas fa-chevron-right"></i>
                 </button>`;
    }
    
    elements.pagination.innerHTML = html;
}

// View college details
async function viewDetails(collegeId) {
    console.log("Viewing details for college:", collegeId);
    
    try {
        // Show loading in modal
        elements.detailBody.innerHTML = `
            <div class="loading-modal">
                <div class="spinner"></div>
                <p>Loading college details...</p>
            </div>
        `;
        
        // Show modal
        elements.detailModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        
        // Fetch college data
        const response = await fetch(`${API_ROOT}/colleges/${collegeId}`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch college details: ${response.status} ${response.statusText}`);
        }
        
        const college = await response.json();
        console.log("College details:", college);
        
        // Generate HTML for the details
        const detailsHtml = generateDetailsHtml(college);
        elements.detailBody.innerHTML = detailsHtml;
        
    } catch (error) {
        console.error("Error loading details:", error);
        elements.detailBody.innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-circle"></i>
                <h3>Failed to load details</h3>
                <p>${escapeHtml(error.message)}</p>
                <button onclick="viewDetails('${collegeId}')" class="btn-retry">
                    <i class="fas fa-redo"></i> Retry
                </button>
            </div>
        `;
    }
}

// Generate detailed HTML for modal
function generateDetailsHtml(college) {
    const branches = Array.isArray(college.branches) ? college.branches : [];
    const cutoffData = college.cutoff_data || {};
    const feeDetails = college.fee_details;
    
    return `
        <div class="detail-content">
            <!-- College Basic Info -->
            <div class="info-section">
                <h2>${escapeHtml(college.name || 'Unknown College')}</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Type:</span>
                        <span class="info-value">${escapeHtml(college.type || 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Location:</span>
                        <span class="info-value">${escapeHtml(college.location || 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Affiliation:</span>
                        <span class="info-value">${escapeHtml(college.affiliation || 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Hostel:</span>
                        <span class="info-value ${college.hostel_available ? 'available' : 'unavailable'}">
                            <i class="fas fa-${college.hostel_available ? 'check' : 'times'}"></i>
                            ${college.hostel_available ? 'Available' : 'Not Available'}
                        </span>
                    </div>
                    ${college.fee_category ? `
                    <div class="info-item">
                        <span class="info-label">Fee Category:</span>
                        <span class="info-value">${escapeHtml(college.fee_category)}</span>
                    </div>
                    ` : ''}
                </div>
            </div>
            
            <!-- Branches -->
            ${branches.length > 0 ? `
            <div class="info-section">
                <h3><i class="fas fa-code-branch"></i> Branches Offered (${branches.length})</h3>
                <div class="branches-list">
                    ${branches.map(branch => 
                        `<span class="branch-badge">${escapeHtml(branch)}</span>`
                    ).join('')}
                </div>
            </div>
            ` : ''}
            
            <!-- Fee Structure -->
            <div class="info-section">
                <h3><i class="fas fa-rupee-sign"></i> Fee Structure</h3>
                ${feeDetails ? `
                <div class="fee-info">
                    <p><strong>Category:</strong> ${escapeHtml(feeDetails.category || college.fee_category || 'N/A')}</p>
                    <table class="fee-table">
                        <thead>
                            <tr>
                                <th>Fee Category</th>
                                <th>Amount (₹)</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${feeDetails.gm_and_others_above_income_limit !== undefined ? `
                            <tr>
                                <td>GM & Others (Above Income Limit)</td>
                                <td class="fee-amount">${formatCurrency(feeDetails.gm_and_others_above_income_limit)}</td>
                            </tr>
                            ` : ''}
                            
                            ${feeDetails.snq_quota !== undefined ? `
                            <tr>
                                <td>SNQ Quota</td>
                                <td class="fee-amount">${formatCurrency(feeDetails.snq_quota)}</td>
                            </tr>
                            ` : ''}
                            
                            ${feeDetails.sc_st_concession !== undefined ? `
                            <tr>
                                <td>SC/ST Concession</td>
                                <td class="fee-amount">${formatCurrency(feeDetails.sc_st_concession)}</td>
                            </tr>
                            ` : ''}
                            
                            ${feeDetails.cat1_upto_2_5_lakhs !== undefined ? `
                            <tr>
                                <td>Cat-1 (Upto 2.5 Lakhs)</td>
                                <td class="fee-amount">${formatCurrency(feeDetails.cat1_upto_2_5_lakhs)}</td>
                            </tr>
                            ` : ''}
                            
                            ${feeDetails.others_upto_10_lakhs !== undefined ? `
                            <tr>
                                <td>Others (Upto 10 Lakhs)</td>
                                <td class="fee-amount">${formatCurrency(feeDetails.others_upto_10_lakhs)}</td>
                            </tr>
                            ` : ''}
                            
                            ${feeDetails.cat1_above_2_5_lakhs !== undefined ? `
                            <tr>
                                <td>Cat-1 (Above 2.5 Lakhs)</td>
                                <td class="fee-amount">${formatCurrency(feeDetails.cat1_above_2_5_lakhs)}</td>
                            </tr>
                            ` : ''}
                        </tbody>
                    </table>
                </div>
                ` : `
                <div class="no-data">
                    <i class="fas fa-info-circle"></i>
                    <p>Fee information not available for this college.</p>
                </div>
                `}
            </div>
            
            <!-- Cutoff Data -->
            ${Object.keys(cutoffData).length > 0 ? `
            <div class="info-section">
                <h3><i class="fas fa-chart-line"></i> Cutoff Data</h3>
                <table class="cutoff-table">
                    <thead>
                        <tr>
                            <th>Branch</th>
                            <th>Cutoff Rank</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${Object.entries(cutoffData).map(([branch, cutoff]) => `
                            <tr>
                                <td>${escapeHtml(branch)}</td>
                                <td>${escapeHtml(String(cutoff))}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            ` : ''}
        </div>
    `;
}

// View fee separately
async function viewFee(feeCategory) {
    if (!feeCategory) {
        alert('Fee category not specified for this college.');
        return;
    }
    
    try {
        const response = await fetch(`${API_ROOT}/fees/${encodeURIComponent(feeCategory)}`);
        
        if (!response.ok) {
            throw new Error('Fee information not found');
        }
        
        const fee = await response.json();
        
        // Create a modal for fee display
        const feeModal = document.createElement('div');
        feeModal.className = 'modal';
        feeModal.innerHTML = `
            <div class="modal-overlay" onclick="this.parentElement.remove()"></div>
            <div class="modal-container" style="max-width: 500px;">
                <div class="modal-header">
                    <h2>Fee Details: ${escapeHtml(feeCategory)}</h2>
                    <button class="close-modal" onclick="this.closest('.modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="fee-summary">
                        <table class="fee-table">
                            <thead>
                                <tr>
                                    <th>Category</th>
                                    <th>Amount</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${fee.gm_and_others_above_income_limit !== undefined ? `
                                <tr>
                                    <td>GM & Others (Above Income Limit)</td>
                                    <td>${formatCurrency(fee.gm_and_others_above_income_limit)}</td>
                                </tr>
                                ` : ''}
                                
                                ${fee.snq_quota !== undefined ? `
                                <tr>
                                    <td>SNQ Quota</td>
                                    <td>${formatCurrency(fee.snq_quota)}</td>
                                </tr>
                                ` : ''}
                                
                                ${fee.sc_st_concession !== undefined ? `
                                <tr>
                                    <td>SC/ST Concession</td>
                                    <td>${formatCurrency(fee.sc_st_concession)}</td>
                                </tr>
                                ` : ''}
                                
                                ${fee.cat1_upto_2_5_lakhs !== undefined ? `
                                <tr>
                                    <td>Cat-1 (Upto 2.5 Lakhs)</td>
                                    <td>${formatCurrency(fee.cat1_upto_2_5_lakhs)}</td>
                                </tr>
                                ` : ''}
                                
                                ${fee.others_upto_10_lakhs !== undefined ? `
                                <tr>
                                    <td>Others (Upto 10 Lakhs)</td>
                                    <td>${formatCurrency(fee.others_upto_10_lakhs)}</td>
                                </tr>
                                ` : ''}
                                
                                ${fee.cat1_above_2_5_lakhs !== undefined ? `
                                <tr>
                                    <td>Cat-1 (Above 2.5 Lakhs)</td>
                                    <td>${formatCurrency(fee.cat1_above_2_5_lakhs)}</td>
                                </tr>
                                ` : ''}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(feeModal);
        
    } catch (error) {
        console.error("Error loading fee:", error);
        alert('Fee information not available for this college.');
    }
}

// Utility functions
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatCurrency(amount) {
    if (amount === null || amount === undefined || amount === '') return 'N/A';
    return '₹' + amount.toLocaleString('en-IN');
}

function goToPage(page) {
    search(page);
}

function showError(message) {
    elements.results.innerHTML = `
        <div class="error-card full-width">
            <i class="fas fa-exclamation-triangle"></i>
            <h3>Application Error</h3>
            <p>${escapeHtml(message)}</p>
            <div class="error-actions">
                <button onclick="initializeApp()" class="btn-retry">
                    <i class="fas fa-redo"></i> Reload Application
                </button>
                <button onclick="checkBackend()" class="btn-secondary">
                    <i class="fas fa-server"></i> Check Backend
                </button>
            </div>
        </div>
    `;
}

async function fetchSuggestions(q) {
    if (!elements.suggestions || !q || q.length < 2) return;
    try {
        const response = await fetch(`${API_ROOT}/search/suggestions?q=${encodeURIComponent(q)}`);
        if (!response.ok) return;
        const list = await response.json();
        if (!Array.isArray(list) || list.length === 0) {
            hideSuggestions();
            return;
        }
        elements.suggestions.innerHTML = list.map(s => 
            `<div class="suggestion-item" data-name="${escapeHtml(s.name)}" data-location="${escapeHtml(s.location || '')}">${escapeHtml(s.name)}${s.location ? ` — ${escapeHtml(s.location)}` : ''}</div>`
        ).join('');
        elements.suggestions.style.display = 'block';
        elements.suggestions.querySelectorAll('.suggestion-item').forEach(el => {
            el.addEventListener('click', () => {
                elements.searchBox.value = el.getAttribute('data-name');
                currentState.query = el.getAttribute('data-name');
                currentState.page = 1;
                hideSuggestions();
                search();
            });
        });
    } catch (_) {
        hideSuggestions();
    }
}

function hideSuggestions() {
    if (elements.suggestions) {
        elements.suggestions.innerHTML = '';
        elements.suggestions.style.display = 'none';
    }
}

async function checkBackend() {
    try {
        const response = await fetch(`${API_ROOT}/health`);
        if (response.ok) {
            alert('✅ Backend is running!');
            initializeApp();
        } else {
            alert('❌ Backend is not responding properly.');
        }
    } catch (error) {
        alert(`❌ Cannot connect to backend: ${error.message}`);
    }
}

// Setup event listeners
function setupEventListeners() {
    console.log("Setting up event listeners...");
    
    // Search box with debouncing and suggestions
    let searchTimeout;
    let suggestionTimeout;
    elements.searchBox.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        clearTimeout(suggestionTimeout);
        currentState.query = e.target.value.trim();
        if (currentState.query.length >= 2) {
            suggestionTimeout = setTimeout(() => fetchSuggestions(currentState.query), 200);
        } else {
            hideSuggestions();
        }
        searchTimeout = setTimeout(() => {
            currentState.page = 1;
            search();
        }, 300);
    });
    elements.searchBox.addEventListener('focus', () => {
        if (currentState.query.length >= 2 && elements.suggestions.innerHTML) {
            elements.suggestions.style.display = 'block';
        }
    });
    document.addEventListener('click', (e) => {
        if (elements.suggestions && !elements.searchBox.contains(e.target) && !elements.suggestions.contains(e.target)) {
            hideSuggestions();
        }
    });
    
    // Branch filter
    elements.branchFilter.addEventListener('change', (e) => {
        currentState.branch = e.target.value;
        currentState.page = 1;
        search();
    });
    
    // Location filter
    elements.locationFilter.addEventListener('change', (e) => {
        currentState.location = e.target.value;
        currentState.page = 1;
        search();
    });
    
    // College type filter
    elements.collegeType.addEventListener('change', (e) => {
        currentState.type = e.target.value;
        currentState.page = 1;
        search();
    });
    
    // Clear button
    elements.clearBtn.addEventListener('click', () => {
        console.log("Clearing all filters...");
        
        // Reset form values
        elements.searchBox.value = '';
        elements.branchFilter.value = '';
        elements.locationFilter.value = '';
        elements.collegeType.value = '';
        
        // Reset state
        currentState.query = '';
        currentState.branch = '';
        currentState.location = '';
        currentState.type = '';
        currentState.page = 1;
        
        // Perform search
        search();
    });
    
    // Close modal button
    elements.closeModal.addEventListener('click', () => {
        elements.detailModal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    });
    
    // Close modal on overlay click
    elements.detailModal.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) {
            elements.detailModal.classList.add('hidden');
            document.body.style.overflow = 'auto';
        }
    });
    
    // Close modal on ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !elements.detailModal.classList.contains('hidden')) {
            elements.detailModal.classList.add('hidden');
            document.body.style.overflow = 'auto';
        }
    });
    
    console.log("Event listeners set up successfully!");
}

// Make functions available globally
window.viewDetails = viewDetails;
window.viewFee = viewFee;
window.goToPage = goToPage;
window.initializeApp = initializeApp;
window.checkBackend = checkBackend;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initializeApp);