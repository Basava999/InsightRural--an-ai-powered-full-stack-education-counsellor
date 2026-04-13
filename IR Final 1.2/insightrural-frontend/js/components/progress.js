// Progress & Gamification Component
// XP system, badges, and achievement tracking

const ProgressComponent = {
    // User progress data
    userData: {
        xp: 0,
        level: 1,
        badges: [],
        lastLogin: null,
        streak: 0,
        predictionsCount: 0,
        chatMessagesCount: 0
    },

    // XP thresholds for levels
    levelThresholds: [0, 100, 250, 500, 1000, 2000, 4000, 7500, 12000, 20000],

    // Available badges
    badges: {
        first_prediction: {
            id: 'first_prediction',
            name: 'First Steps',
            description: 'Made your first college prediction',
            icon: '🎯',
            xp: 25
        },
        explorer: {
            id: 'explorer',
            name: 'Explorer',
            description: 'Explored 10 different colleges',
            icon: '🔍',
            xp: 50
        },
        document_master: {
            id: 'document_master',
            name: 'Document Master',
            description: 'Completed all document verification',
            icon: '📁',
            xp: 100
        },
        chat_champion: {
            id: 'chat_champion',
            name: 'Chat Champion',
            description: 'Asked 25 questions to AI counselor',
            icon: '💬',
            xp: 75
        },
        streak_3: {
            id: 'streak_3',
            name: 'Consistent',
            description: 'Logged in 3 days in a row',
            icon: '🔥',
            xp: 30
        },
        streak_7: {
            id: 'streak_7',
            name: 'Dedicated',
            description: 'Logged in 7 days in a row',
            icon: '⭐',
            xp: 70
        },
        voice_user: {
            id: 'voice_user',
            name: 'Voice Pioneer',
            description: 'Used voice input feature',
            icon: '🎤',
            xp: 20
        },
        pdf_download: {
            id: 'pdf_download',
            name: 'Report Generator',
            description: 'Downloaded a prediction report',
            icon: '📄',
            xp: 15
        },
        early_bird: {
            id: 'early_bird',
            name: 'Early Bird',
            description: 'Started preparation before counselling',
            icon: '🌅',
            xp: 40
        }
    },

    init() {
        this.loadProgress();
        this.checkStreak();
        this.setupEventListeners();
        this.renderProgressBar();
        console.log('🏆 Progress component initialized');
    },

    setupEventListeners() {
        // Listen for various events
        document.addEventListener('prediction_complete', () => {
            this.addXP(20);
            this.incrementPredictions();
        });

        document.addEventListener('chat_message', () => {
            this.incrementChatMessages();
        });
    },

    loadProgress() {
        try {
            const saved = localStorage.getItem('insightrural_progress');
            if (saved) {
                this.userData = { ...this.userData, ...JSON.parse(saved) };
            }
        } catch (e) {
            console.log('No saved progress');
        }
    },

    saveProgress() {
        try {
            localStorage.setItem('insightrural_progress', JSON.stringify(this.userData));
        } catch (e) {
            console.log('Could not save progress');
        }
    },

    checkStreak() {
        const today = new Date().toDateString();
        const lastLogin = this.userData.lastLogin;

        if (lastLogin) {
            const yesterday = new Date();
            yesterday.setDate(yesterday.getDate() - 1);

            if (lastLogin === yesterday.toDateString()) {
                this.userData.streak++;
                this.checkStreakBadges();
            } else if (lastLogin !== today) {
                this.userData.streak = 1;
            }
        } else {
            this.userData.streak = 1;
        }

        this.userData.lastLogin = today;
        this.saveProgress();
    },

    checkStreakBadges() {
        if (this.userData.streak >= 3 && !this.hasBadge('streak_3')) {
            this.unlockBadge('streak_3');
        }
        if (this.userData.streak >= 7 && !this.hasBadge('streak_7')) {
            this.unlockBadge('streak_7');
        }
    },

    addXP(amount) {
        const oldLevel = this.getLevel();
        this.userData.xp += amount;
        const newLevel = this.getLevel();

        if (newLevel > oldLevel) {
            this.showLevelUp(newLevel);
        }

        this.saveProgress();
        this.updateXPDisplay();

        // Show XP gain notification
        if (amount > 0) {
            this.showXPGain(amount);
        }
    },

    getLevel() {
        for (let i = this.levelThresholds.length - 1; i >= 0; i--) {
            if (this.userData.xp >= this.levelThresholds[i]) {
                return i + 1;
            }
        }
        return 1;
    },

    getXPForCurrentLevel() {
        const level = this.getLevel();
        return this.userData.xp - this.levelThresholds[level - 1];
    },

    getXPForNextLevel() {
        const level = this.getLevel();
        if (level >= this.levelThresholds.length) return 0;
        return this.levelThresholds[level] - this.levelThresholds[level - 1];
    },

    hasBadge(badgeId) {
        return this.userData.badges.includes(badgeId);
    },

    unlockBadge(badgeId) {
        if (this.hasBadge(badgeId)) return;

        const badge = this.badges[badgeId];
        if (!badge) return;

        this.userData.badges.push(badgeId);
        this.addXP(badge.xp);
        this.showBadgeUnlock(badge);
        this.saveProgress();
    },

    incrementPredictions() {
        this.userData.predictionsCount++;

        if (this.userData.predictionsCount === 1 && !this.hasBadge('first_prediction')) {
            this.unlockBadge('first_prediction');
        }

        this.saveProgress();
    },

    incrementChatMessages() {
        this.userData.chatMessagesCount++;

        if (this.userData.chatMessagesCount >= 25 && !this.hasBadge('chat_champion')) {
            this.unlockBadge('chat_champion');
        }

        this.saveProgress();
    },

    showXPGain(amount) {
        const toast = document.createElement('div');
        toast.className = 'xp-toast';
        toast.innerHTML = `+${amount} XP`;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('visible');
        }, 10);

        setTimeout(() => {
            toast.classList.remove('visible');
            setTimeout(() => toast.remove(), 300);
        }, 1500);
    },

    showLevelUp(level) {
        const modal = document.createElement('div');
        modal.className = 'level-up-modal';
        modal.innerHTML = `
            <div class="level-up-content">
                <div class="level-up-icon">🎉</div>
                <h2>Level Up!</h2>
                <div class="new-level">Level ${level}</div>
                <p>Keep exploring to unlock more features!</p>
                <button onclick="this.parentElement.parentElement.remove()">Continue</button>
            </div>
        `;
        document.body.appendChild(modal);

        setTimeout(() => modal.classList.add('visible'), 10);
    },

    showBadgeUnlock(badge) {
        const modal = document.createElement('div');
        modal.className = 'badge-unlock-modal';
        modal.innerHTML = `
            <div class="badge-unlock-content">
                <div class="badge-icon">${badge.icon}</div>
                <h3>Badge Unlocked!</h3>
                <div class="badge-name">${badge.name}</div>
                <p>${badge.description}</p>
                <div class="badge-xp">+${badge.xp} XP</div>
                <button onclick="this.parentElement.parentElement.remove()">Awesome!</button>
            </div>
        `;
        document.body.appendChild(modal);

        setTimeout(() => modal.classList.add('visible'), 10);
    },

    updateXPDisplay() {
        const xpBar = document.getElementById('xp-bar-fill');
        const xpText = document.getElementById('xp-text');
        const levelText = document.getElementById('level-text');

        if (xpBar) {
            const current = this.getXPForCurrentLevel();
            const needed = this.getXPForNextLevel();
            const percent = needed > 0 ? (current / needed) * 100 : 100;
            xpBar.style.width = `${percent}%`;
        }

        if (xpText) {
            xpText.textContent = `${this.getXPForCurrentLevel()} / ${this.getXPForNextLevel()} XP`;
        }

        if (levelText) {
            levelText.textContent = `Level ${this.getLevel()}`;
        }
    },

    renderProgressBar() {
        // Add progress bar to sidebar or nav
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;

        // Find profile section or create progress widget
        let progressWidget = document.getElementById('progress-widget');

        if (!progressWidget) {
            progressWidget = document.createElement('div');
            progressWidget.id = 'progress-widget';
            progressWidget.className = 'progress-widget';

            const profileSection = sidebar.querySelector('.profile-section');
            if (profileSection) {
                profileSection.insertAdjacentElement('beforebegin', progressWidget);
            }
        }

        const level = this.getLevel();
        const currentXP = this.getXPForCurrentLevel();
        const neededXP = this.getXPForNextLevel();
        const percent = neededXP > 0 ? (currentXP / neededXP) * 100 : 100;

        progressWidget.innerHTML = `
            <div class="progress-header">
                <span class="level-badge" id="level-text">Level ${level}</span>
                <span class="streak-badge">🔥 ${this.userData.streak}</span>
            </div>
            <div class="xp-bar">
                <div class="xp-bar-fill" id="xp-bar-fill" style="width: ${percent}%"></div>
            </div>
            <div class="xp-text" id="xp-text">${currentXP} / ${neededXP} XP</div>
            <div class="badges-preview">
                ${this.userData.badges.slice(-3).map(id => `
                    <span class="mini-badge" title="${this.badges[id]?.name}">${this.badges[id]?.icon}</span>
                `).join('')}
                ${this.userData.badges.length > 3 ? `<span class="more-badges">+${this.userData.badges.length - 3}</span>` : ''}
            </div>
        `;

        this.addProgressStyles();
    },

    addProgressStyles() {
        if (document.getElementById('progress-styles')) return;

        const style = document.createElement('style');
        style.id = 'progress-styles';
        style.textContent = `
            .progress-widget {
                padding: 1rem;
                margin: 1rem;
                background: linear-gradient(135deg, rgba(16, 163, 127, 0.1) 0%, rgba(30, 144, 255, 0.1) 100%);
                border-radius: 12px;
                border: 1px solid rgba(16, 163, 127, 0.2);
            }
            
            .progress-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.5rem;
            }
            
            .level-badge {
                background: linear-gradient(135deg, #10a37f 0%, #1e90ff 100%);
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 600;
            }
            
            .streak-badge {
                font-size: 0.8rem;
            }
            
            .xp-bar {
                height: 6px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
                overflow: hidden;
                margin-bottom: 0.5rem;
            }
            
            .xp-bar-fill {
                height: 100%;
                background: linear-gradient(90deg, #10a37f 0%, #1e90ff 100%);
                border-radius: 3px;
                transition: width 0.5s ease;
            }
            
            .xp-text {
                font-size: 0.7rem;
                color: var(--text-secondary);
                text-align: center;
                margin-bottom: 0.5rem;
            }
            
            .badges-preview {
                display: flex;
                justify-content: center;
                gap: 0.5rem;
            }
            
            .mini-badge {
                font-size: 1rem;
                cursor: pointer;
            }
            
            .more-badges {
                font-size: 0.7rem;
                color: var(--text-secondary);
            }
            
            /* XP Toast */
            .xp-toast {
                position: fixed;
                top: 80px;
                right: 20px;
                background: linear-gradient(135deg, #10a37f 0%, #1e90ff 100%);
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 50px;
                font-weight: 700;
                font-size: 1rem;
                opacity: 0;
                transform: translateY(-20px);
                transition: all 0.3s ease;
                z-index: 9999;
            }
            
            .xp-toast.visible {
                opacity: 1;
                transform: translateY(0);
            }
            
            /* Level Up Modal */
            .level-up-modal {
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                opacity: 0;
                transition: opacity 0.3s;
            }
            
            .level-up-modal.visible {
                opacity: 1;
            }
            
            .level-up-content {
                background: var(--bg-secondary);
                padding: 3rem;
                border-radius: 24px;
                text-align: center;
                animation: bounceIn 0.5s ease;
            }
            
            @keyframes bounceIn {
                0% { transform: scale(0.5); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
            
            .level-up-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
            }
            
            .level-up-content h2 {
                font-size: 2rem;
                background: linear-gradient(135deg, #10a37f 0%, #1e90ff 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .new-level {
                font-size: 3rem;
                font-weight: 700;
                margin: 1rem 0;
            }
            
            .level-up-content button {
                margin-top: 1.5rem;
                padding: 1rem 3rem;
                background: linear-gradient(135deg, #10a37f 0%, #1e90ff 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
            }
            
            /* Badge Unlock Modal */
            .badge-unlock-modal {
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                opacity: 0;
                transition: opacity 0.3s;
            }
            
            .badge-unlock-modal.visible {
                opacity: 1;
            }
            
            .badge-unlock-content {
                background: var(--bg-secondary);
                padding: 2rem;
                border-radius: 20px;
                text-align: center;
                animation: bounceIn 0.5s ease;
            }
            
            .badge-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
            }
            
            .badge-name {
                font-size: 1.5rem;
                font-weight: 700;
                margin: 0.5rem 0;
            }
            
            .badge-xp {
                color: #10a37f;
                font-weight: 600;
                margin-top: 1rem;
            }
            
            .badge-unlock-content button {
                margin-top: 1.5rem;
                padding: 0.75rem 2rem;
                background: linear-gradient(135deg, #10a37f 0%, #1e90ff 100%);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                cursor: pointer;
            }
        `;
        document.head.appendChild(style);
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    ProgressComponent.init();
});

window.ProgressComponent = ProgressComponent;
