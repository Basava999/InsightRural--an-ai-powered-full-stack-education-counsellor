// Modal Component
// Handles login and profile modals

const ModalComponent = {
    init() {
        this.createLoginModal();
        this.createProfileModal();
        this.setupEventListeners();
        console.log('🔐 Modal component initialized');
    },

    setupEventListeners() {
        // Close login modal
        const closeLogin = document.getElementById('close-login-modal');
        if (closeLogin) {
            closeLogin.addEventListener('click', () => this.hideModal('login-modal'));
        }

        // Close profile modal
        const closeProfile = document.getElementById('close-profile-modal');
        if (closeProfile) {
            closeProfile.addEventListener('click', () => this.hideModal('profile-modal'));
        }

        // Demo login button
        const demoLogin = document.getElementById('demo-login');
        if (demoLogin) {
            demoLogin.addEventListener('click', () => this.handleLogin());
        }

        // Demo signup button
        const demoSignup = document.getElementById('demo-signup');
        if (demoSignup) {
            demoSignup.addEventListener('click', () => this.handleSignup());
        }

        // Profile form save
        const profileForm = document.getElementById('profile-form');
        if (profileForm) {
            profileForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleProfileSave();
            });

            // Cancel button in profile
            const cancelBtn = profileForm.querySelector('.cancel-btn');
            if (cancelBtn) {
                cancelBtn.addEventListener('click', () => this.hideModal('profile-modal'));
            }
        }

        // Click outside modal to close
        ['login-modal', 'profile-modal'].forEach(id => {
            const modal = document.getElementById(id);
            if (modal) {
                modal.addEventListener('click', (e) => {
                    if (e.target === modal) {
                        this.hideModal(id);
                    }
                });
            }
        });
    },

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            modal.style.display = 'flex';
            // Pre-fill profile form with saved data
            if (modalId === 'profile-modal' && typeof AppState !== 'undefined') {
                const profile = AppState.getProfile();
                const nameInput = document.getElementById('name');
                const locationInput = document.getElementById('location');
                const educationInput = document.getElementById('education');
                const financeInput = document.getElementById('finance');
                const interestsInput = document.getElementById('interests');
                if (nameInput && profile.name) nameInput.value = profile.name;
                if (locationInput && profile.location) locationInput.value = profile.location;
                if (educationInput && profile.education) educationInput.value = profile.education;
                if (financeInput && profile.finance) financeInput.value = profile.finance;
                if (interestsInput && profile.interests) interestsInput.value = profile.interests;
            }
        }
    },

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            modal.style.display = 'none';
        }
    },

    handleLogin() {
        const email = document.getElementById('auth-email')?.value?.trim();
        if (!email) {
            alert('Please enter your email or phone number');
            return;
        }
        // Store login state
        localStorage.setItem('insightrural-user', JSON.stringify({
            email: email,
            loggedIn: true,
            loginTime: new Date().toISOString()
        }));
        this.hideModal('login-modal');
        // Update UI
        const loginBtn = document.getElementById('login-sidebar-btn');
        if (loginBtn) {
            loginBtn.querySelector('span').textContent = email.split('@')[0] || email;
        }
        if (typeof ChatComponent !== 'undefined') {
            ChatComponent.addMessage('ai', `✅ Welcome! You're now logged in. Your progress will be saved.`);
        }
    },

    handleSignup() {
        const email = document.getElementById('auth-email')?.value?.trim();
        const password = document.getElementById('auth-password')?.value?.trim();
        if (!email || !password) {
            alert('Please fill in all fields');
            return;
        }
        localStorage.setItem('insightrural-user', JSON.stringify({
            email: email,
            loggedIn: true,
            loginTime: new Date().toISOString()
        }));
        this.hideModal('login-modal');
        if (typeof ChatComponent !== 'undefined') {
            ChatComponent.addMessage('ai', `✅ Account created! Welcome to InsightRural.`);
        }
    },

    handleProfileSave() {
        const name = document.getElementById('name')?.value?.trim();
        const location = document.getElementById('location')?.value?.trim();
        const education = document.getElementById('education')?.value;
        const finance = document.getElementById('finance')?.value;
        const interests = document.getElementById('interests')?.value?.trim();

        const profileData = {
            name: name || '',
            location: location || '',
            education: education || '',
            finance: finance || '',
            interests: interests || ''
        };

        if (typeof AppState !== 'undefined') {
            AppState.saveProfile(profileData);
        }

        // Close the modal
        this.hideModal('profile-modal');

        // Show success feedback
        console.log('✅ Profile saved:', profileData);
    },

    createLoginModal() {
        const modal = document.getElementById('login-modal');
        if (!modal) return;

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Welcome to InsightRural</h2>
                    <button class="close-btn" id="close-login-modal">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
                
                <div class="modal-body">
                    <p class="modal-subtitle">Login or create an account to save your progress</p>
                    
                    <div class="auth-tabs">
                        <button class="auth-tab active" data-tab="login">Login</button>
                        <button class="auth-tab" data-tab="signup">Sign Up</button>
                    </div>
                    
                    <form class="auth-form" id="auth-form">
                        <div class="form-group">
                            <label for="auth-email">Email or Phone</label>
                            <input type="text" id="auth-email" placeholder="Enter email or phone number">
                        </div>
                        
                        <div class="form-group">
                            <label for="auth-password">Password</label>
                            <input type="password" id="auth-password" placeholder="Enter password">
                        </div>
                        
                        <button type="button" class="btn-primary" id="demo-login">Login</button>
                        <button type="button" class="btn-secondary" id="demo-signup" style="display:none;">Create Account</button>
                    </form>
                    
                    <div class="auth-divider">
                        <span>or continue with</span>
                    </div>
                    
                    <div class="social-login">
                        <button class="social-btn google">
                            <svg width="20" height="20" viewBox="0 0 24 24">
                                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                            </svg>
                            Google
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Tab switching
        modal.querySelectorAll('.auth-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                modal.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                const isLogin = tab.dataset.tab === 'login';
                document.getElementById('demo-login').style.display = isLogin ? 'block' : 'none';
                document.getElementById('demo-signup').style.display = isLogin ? 'none' : 'block';
            });
        });
    },

    createProfileModal() {
        const modal = document.getElementById('profile-modal');
        if (!modal) return;

        // Ensure modal is hidden initially
        modal.style.display = 'none';

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Your Profile</h2>
                    <button class="close-btn" id="close-profile-modal">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
                
                <div class="modal-body">
                    <form id="profile-form">
                        <div class="form-group">
                            <label for="name">Full Name</label>
                            <input type="text" id="name" placeholder="Enter your name">
                        </div>
                        
                        <div class="form-group">
                            <label for="location">Location</label>
                            <input type="text" id="location" placeholder="District, State">
                        </div>
                        
                        <div class="form-group">
                            <label for="education">Current Education</label>
                            <select id="education">
                                <option value="10th">10th Standard</option>
                                <option value="12th" selected>12th Standard</option>
                                <option value="diploma">Diploma</option>
                                <option value="graduate">Graduate</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="finance">Financial Situation</label>
                            <select id="finance">
                                <option value="Low">Low Income</option>
                                <option value="Medium" selected>Medium Income</option>
                                <option value="High">High Income</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="interests">Interests & Goals</label>
                            <textarea id="interests" rows="3" placeholder="What are your career goals?"></textarea>
                        </div>
                        
                        <div class="form-actions">
                            <button type="button" class="cancel-btn">Cancel</button>
                            <button type="submit" class="save-btn">Save Profile</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    ModalComponent.init();
});

window.ModalComponent = ModalComponent;
