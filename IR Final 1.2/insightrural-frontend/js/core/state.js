// Application State Management - Enhanced for KEA AI Counselor

// Global API Base URL - shared across all components
const API_BASE_URL = (
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.protocol === 'file:'
)
    ? 'http://127.0.0.1:5000'
    : 'https://insightrural-backend.onrender.com';

const AppState = {
    currentFeature: 'colleges',
    chatHistory: [],
    sessionId: null,

    // Enhanced profile for KEA students
    profile: {
        name: '',
        kcet_rank: null,
        branch: 'CSE',
        category: 'GM',  // GM, OBC, SC, ST
        income: null,    // Annual family income
        location: '',
        preferred_location: 'Bangalore',
        hostel_needed: null,
        budget: null
    },

    init() {
        // Generate session ID
        this.sessionId = localStorage.getItem('insightrural-session') || this.generateSessionId();
        localStorage.setItem('insightrural-session', this.sessionId);

        // Load theme
        const savedTheme = localStorage.getItem('insightrural-theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);

        // Load profile if exists
        const savedProfile = localStorage.getItem('insightrural-profile');
        if (savedProfile) {
            try {
                this.profile = { ...this.profile, ...JSON.parse(savedProfile) };
            } catch (e) {
                console.log('Could not load profile');
            }
        }

        // Load chat history
        const savedHistory = localStorage.getItem('insightrural-chat');
        if (savedHistory) {
            try {
                this.chatHistory = JSON.parse(savedHistory);
            } catch (e) {
                console.log('Could not load chat history');
            }
        }
    },

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    },

    getSessionId() {
        return this.sessionId;
    },


    setFeature(feature) {
        this.currentFeature = feature;

        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.feature === feature) {
                item.classList.add('active');
            }
        });

        return true;
    },

    addMessage(sender, content) {
        const message = {
            id: Date.now(),
            sender,
            content,
            timestamp: new Date().toISOString(),
            feature: this.currentFeature
        };

        this.chatHistory.push(message);
        this.saveChatHistory();
        return message;
    },

    getChatHistory(feature = null) {
        if (feature) {
            return this.chatHistory.filter(msg => msg.feature === feature);
        }
        return this.chatHistory;
    },

    clearChatHistory() {
        this.chatHistory = [];
        localStorage.removeItem('insightrural-chat');
    },

    saveChatHistory() {
        try {
            // Keep only last 50 messages to avoid storage limits
            const historyToSave = this.chatHistory.slice(-50);
            localStorage.setItem('insightrural-chat', JSON.stringify(historyToSave));
        } catch (e) {
            console.log('Could not save chat history');
        }
    },

    getProfile() {
        return this.profile;
    },

    saveProfile(profileData) {
        this.profile = { ...this.profile, ...profileData };
        localStorage.setItem('insightrural-profile', JSON.stringify(this.profile));

        // Sync with backend
        this.syncProfileToBackend();

        // Show success message
        if (typeof ChatComponent !== 'undefined') {
            ChatComponent.addMessage('ai', `✅ Profile updated! I'll now provide personalized guidance based on your information.`);
        }
    },

    async syncProfileToBackend() {
        try {
            await fetch(`${API_BASE_URL}/api/profile?session_id=` + this.sessionId, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.profile)
            });
        } catch (e) {
            console.log('Could not sync profile to backend');
        }
    },

    // Quick profile update methods
    setKCETRank(rank) {
        this.saveProfile({ kcet_rank: parseInt(rank) });
    },

    setCategory(category) {
        this.saveProfile({ category: category.toUpperCase() });
    },

    setBranch(branch) {
        this.saveProfile({ branch: branch.toUpperCase() });
    },

    setIncome(income) {
        this.saveProfile({ income: parseInt(income) });
    },

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('insightrural-theme', newTheme);
    },

    // Check if profile is complete for recommendations
    isProfileComplete() {
        return this.profile.kcet_rank && this.profile.branch && this.profile.category;
    },

    // Get profile completion status message
    getProfileStatus() {
        const missing = [];
        if (!this.profile.kcet_rank) missing.push('KCET Rank');
        if (!this.profile.branch) missing.push('Preferred Branch');
        if (!this.profile.category) missing.push('Category');
        if (!this.profile.income) missing.push('Family Income');

        if (missing.length === 0) {
            return { complete: true, message: 'Profile complete!' };
        }
        return { complete: false, message: `Please provide: ${missing.join(', ')}` };
    }
};