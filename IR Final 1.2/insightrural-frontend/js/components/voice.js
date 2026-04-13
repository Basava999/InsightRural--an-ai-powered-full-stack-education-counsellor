// Voice Input Component
// Supports English and Kannada speech recognition using Web Speech API

const VoiceInput = {
    recognition: null,
    isListening: false,
    currentLanguage: 'en-IN', // Default to Indian English

    languages: {
        'en-IN': { name: 'English', flag: '🇬🇧' },
        'kn-IN': { name: 'ಕನ್ನಡ (Kannada)', flag: '🇮🇳' },
        'hi-IN': { name: 'हिंदी (Hindi)', flag: '🇮🇳' },
        'te-IN': { name: 'తెలుగు (Telugu)', flag: '🇮🇳' }
    },

    // Initialize voice recognition
    init() {
        // Check browser support
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Speech recognition not supported in this browser');
            this.hideVoiceButton();
            return false;
        }

        // Create recognition instance
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();

        // Configure
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = this.currentLanguage;

        // Set up event handlers
        this.setupEventHandlers();

        // Render UI
        this.renderVoiceButton();
        this.renderLanguageSelector();

        console.log('🎤 Voice input initialized with language:', this.currentLanguage);
        return true;
    },

    setupEventHandlers() {
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateButtonState();
            this.showListeningIndicator();
            console.log('🎤 Listening...');
        };

        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            // Show interim results in input
            const chatInput = document.getElementById('chat-input');
            if (chatInput) {
                if (finalTranscript) {
                    chatInput.value = finalTranscript;
                    // Trigger input event for send button enable
                    chatInput.dispatchEvent(new Event('input'));
                } else if (interimTranscript) {
                    chatInput.value = interimTranscript;
                    chatInput.placeholder = 'Listening...';
                }
            }

            // Update live transcript display
            this.updateLiveTranscript(interimTranscript || finalTranscript, !finalTranscript);
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateButtonState();
            this.hideListeningIndicator();
            console.log('🎤 Stopped listening');
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            this.updateButtonState();
            this.hideListeningIndicator();

            // User-friendly error messages
            const errorMessages = {
                'no-speech': 'ಮಾತು ಕೇಳಿಸಲಿಲ್ಲ / No speech detected. Please try again.',
                'audio-capture': 'ಮೈಕ್ರೋಫೋನ್ ಸಿಗಲಿಲ್ಲ / Microphone not found.',
                'not-allowed': 'ಮೈಕ್ರೋಫೋನ್ ಅನುಮತಿ ಬೇಕು / Microphone permission denied.',
                'network': 'ನೆಟ್ವರ್ಕ್ ಸಮಸ್ಯೆ / Network error. Check connection.'
            };

            this.showError(errorMessages[event.error] || `Error: ${event.error}`);
        };
    },

    renderVoiceButton() {
        const inputWrapper = document.querySelector('.input-wrapper');
        if (!inputWrapper) return;

        // Check if button already exists
        if (document.getElementById('voice-btn')) return;

        const voiceBtn = document.createElement('button');
        voiceBtn.id = 'voice-btn';
        voiceBtn.className = 'voice-btn';
        voiceBtn.title = 'Voice Input (Kannada/English)';
        voiceBtn.innerHTML = `
            <svg class="mic-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M12 1C10.34 1 9 2.34 9 4V12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12V4C15 2.34 13.66 1 12 1Z" stroke="currentColor" stroke-width="2"/>
                <path d="M19 10V12C19 15.866 15.866 19 12 19M5 10V12C5 15.866 8.134 19 12 19M12 19V23M8 23H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <svg class="stop-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" style="display:none;">
                <rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor"/>
            </svg>
        `;

        voiceBtn.addEventListener('click', () => this.toggleListening());

        // Insert before send button
        const sendBtn = document.getElementById('send-btn');
        if (sendBtn) {
            inputWrapper.insertBefore(voiceBtn, sendBtn);
        } else {
            inputWrapper.appendChild(voiceBtn);
        }
    },

    renderLanguageSelector() {
        const inputContainer = document.querySelector('.input-container');
        if (!inputContainer) return;

        // Check if selector already exists
        if (document.getElementById('voice-lang-selector')) return;

        const langSelector = document.createElement('div');
        langSelector.id = 'voice-lang-selector';
        langSelector.className = 'voice-lang-selector';
        langSelector.innerHTML = `
            <span class="lang-label">🎤 Voice:</span>
            <select id="voice-language">
                ${Object.entries(this.languages).map(([code, lang]) =>
            `<option value="${code}" ${code === this.currentLanguage ? 'selected' : ''}>
                        ${lang.flag} ${lang.name}
                    </option>`
        ).join('')}
            </select>
        `;

        inputContainer.insertBefore(langSelector, inputContainer.firstChild);

        // Language change handler
        document.getElementById('voice-language').addEventListener('change', (e) => {
            this.setLanguage(e.target.value);
        });
    },

    setLanguage(langCode) {
        this.currentLanguage = langCode;
        if (this.recognition) {
            this.recognition.lang = langCode;
        }
        console.log('🌐 Voice language set to:', this.languages[langCode].name);

        // Show language change notification
        this.showNotification(`Voice: ${this.languages[langCode].name}`);
    },

    toggleListening() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    },

    startListening() {
        if (!this.recognition) {
            this.showError('Voice input not available');
            return;
        }

        try {
            this.recognition.start();
        } catch (error) {
            console.error('Failed to start recognition:', error);
            this.showError('Could not start voice input');
        }
    },

    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    },

    updateButtonState() {
        const voiceBtn = document.getElementById('voice-btn');
        if (!voiceBtn) return;

        const micIcon = voiceBtn.querySelector('.mic-icon');
        const stopIcon = voiceBtn.querySelector('.stop-icon');

        if (this.isListening) {
            voiceBtn.classList.add('listening');
            micIcon.style.display = 'none';
            stopIcon.style.display = 'block';
        } else {
            voiceBtn.classList.remove('listening');
            micIcon.style.display = 'block';
            stopIcon.style.display = 'none';
        }
    },

    showListeningIndicator() {
        // Add listening indicator to chat input
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.dataset.originalPlaceholder = chatInput.placeholder;
            chatInput.placeholder = `🎤 ${this.languages[this.currentLanguage].name} - Listening...`;
        }

        // Show live transcript container
        let liveTranscript = document.getElementById('live-transcript');
        if (!liveTranscript) {
            liveTranscript = document.createElement('div');
            liveTranscript.id = 'live-transcript';
            liveTranscript.className = 'live-transcript';
            const inputContainer = document.querySelector('.input-container');
            if (inputContainer) {
                inputContainer.insertBefore(liveTranscript, inputContainer.firstChild);
            }
        }
        liveTranscript.style.display = 'block';
        liveTranscript.innerHTML = '<span class="pulse-dot"></span> Listening...';
    },

    hideListeningIndicator() {
        const chatInput = document.getElementById('chat-input');
        if (chatInput && chatInput.dataset.originalPlaceholder) {
            chatInput.placeholder = chatInput.dataset.originalPlaceholder;
        }

        const liveTranscript = document.getElementById('live-transcript');
        if (liveTranscript) {
            setTimeout(() => {
                liveTranscript.style.display = 'none';
            }, 1000);
        }
    },

    updateLiveTranscript(text, isInterim) {
        const liveTranscript = document.getElementById('live-transcript');
        if (liveTranscript) {
            liveTranscript.innerHTML = `
                <span class="pulse-dot"></span>
                <span class="${isInterim ? 'interim' : 'final'}">${text}</span>
            `;
        }
    },

    hideVoiceButton() {
        const voiceBtn = document.getElementById('voice-btn');
        if (voiceBtn) voiceBtn.style.display = 'none';

        const langSelector = document.getElementById('voice-lang-selector');
        if (langSelector) langSelector.style.display = 'none';
    },

    showError(message) {
        const liveTranscript = document.getElementById('live-transcript');
        if (liveTranscript) {
            liveTranscript.innerHTML = `<span class="error">❌ ${message}</span>`;
            liveTranscript.style.display = 'block';
            setTimeout(() => {
                liveTranscript.style.display = 'none';
            }, 3000);
        }
    },

    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'voice-notification';
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    VoiceInput.init();
});

// Export for use in other modules
window.VoiceInput = VoiceInput;
