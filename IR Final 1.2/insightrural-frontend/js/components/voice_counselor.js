// Voice-First AI Counselor Component
// Hands-free voice conversation with AI using Web Speech API

const VoiceCounselorComponent = {
    isListening: false,
    isSpeaking: false,
    recognition: null,
    synthesis: window.speechSynthesis,
    currentLanguage: 'en-IN',
    conversationHistory: [],

    // Supported languages
    languages: {
        'en-IN': { name: 'English', voice: 'en-IN', greeting: 'Hello! I am your AI counselor. How can I help you today?' },
        'hi-IN': { name: 'हिंदी', voice: 'hi-IN', greeting: 'नमस्ते! मैं आपका AI काउंसलर हूं। आज मैं आपकी कैसे मदद कर सकता हूं?' },
        'kn-IN': { name: 'ಕನ್ನಡ', voice: 'kn-IN', greeting: 'ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ AI ಸಲಹೆಗಾರ. ನಾನು ಇಂದು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?' }
    },

    init() {
        this.setupSpeechRecognition();
        this.injectStyles();
        console.log('🎙️ Voice Counselor initialized');
    },

    setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.warn('Speech Recognition not supported in this browser');
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = this.currentLanguage;

        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateUI('listening');
        };

        this.recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0].transcript)
                .join('');

            this.updateTranscript(transcript, event.results[0].isFinal);

            if (event.results[0].isFinal) {
                this.processVoiceInput(transcript);
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            this.updateUI('error', event.error);
        };

        this.recognition.onend = () => {
            this.isListening = false;
            if (!this.isSpeaking) {
                this.updateUI('idle');
            }
        };
    },

    render() {
        const container = document.getElementById('voice-section');
        if (!container) return;

        container.innerHTML = `
            <div class="voice-counselor">
                <div class="voice-header">
                    <h2>🎙️ Voice AI Counselor</h2>
                    <p class="voice-subtitle">Speak naturally in your language</p>
                </div>

                <div class="language-selector">
                    ${Object.entries(this.languages).map(([code, lang]) => `
                        <button class="lang-btn ${code === this.currentLanguage ? 'active' : ''}" 
                                data-lang="${code}">
                            ${lang.name}
                        </button>
                    `).join('')}
                </div>

                <div class="voice-avatar">
                    <div class="avatar-circle" id="voice-avatar">
                        <div class="avatar-icon">🤖</div>
                        <div class="pulse-ring"></div>
                        <div class="pulse-ring delay"></div>
                    </div>
                    <div class="voice-status" id="voice-status">
                        Tap the microphone to start
                    </div>
                </div>

                <div class="voice-waveform" id="voice-waveform">
                    ${Array(20).fill().map(() => '<div class="wave-bar"></div>').join('')}
                </div>

                <div class="transcript-box" id="transcript-box">
                    <div class="transcript-label">You said:</div>
                    <div class="transcript-text" id="transcript-text"></div>
                </div>

                <div class="response-box" id="response-box">
                    <div class="response-label">AI Response:</div>
                    <div class="response-text" id="response-text"></div>
                </div>

                <div class="voice-controls">
                    <button class="mic-btn" id="mic-btn" title="Click to speak">
                        <svg class="mic-icon" viewBox="0 0 24 24" fill="none">
                            <path d="M12 1C10.34 1 9 2.34 9 4V12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12V4C15 2.34 13.66 1 12 1Z" 
                                  fill="currentColor"/>
                            <path d="M17 12C17 14.76 14.76 17 12 17C9.24 17 7 14.76 7 12H5C5 15.53 7.61 18.43 11 18.93V22H13V18.93C16.39 18.43 19 15.53 19 12H17Z" 
                                  fill="currentColor"/>
                        </svg>
                        <svg class="stop-icon" viewBox="0 0 24 24" fill="none" style="display:none">
                            <rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor"/>
                        </svg>
                    </button>
                    <button class="speaker-btn" id="speaker-btn" title="Stop speaking">
                        🔊
                    </button>
                </div>

                <div class="voice-history" id="voice-history">
                    <h3>Conversation History</h3>
                    <div class="history-list" id="history-list"></div>
                </div>

                <div class="voice-tips">
                    <h4>💡 Try asking:</h4>
                    <div class="tip-chips">
                        <span class="tip-chip" data-query="What colleges can I get with 15000 rank?">🎓 College options</span>
                        <span class="tip-chip" data-query="Tell me about scholarships for SC students">💰 Scholarships</span>
                        <span class="tip-chip" data-query="How to apply for education loan?">🏦 Education loans</span>
                        <span class="tip-chip" data-query="What is the KCET counselling process?">📋 Counselling process</span>
                    </div>
                </div>
            </div>
        `;

        this.setupEventListeners();
    },

    setupEventListeners() {
        // Microphone button
        const micBtn = document.getElementById('mic-btn');
        if (micBtn) {
            micBtn.addEventListener('click', () => this.toggleListening());
        }

        // Speaker button
        const speakerBtn = document.getElementById('speaker-btn');
        if (speakerBtn) {
            speakerBtn.addEventListener('click', () => this.stopSpeaking());
        }

        // Language buttons
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.changeLanguage(e.target.dataset.lang);
            });
        });

        // Tip chips
        document.querySelectorAll('.tip-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                const query = e.target.dataset.query;
                this.processVoiceInput(query);
            });
        });
    },

    toggleListening() {
        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.stopSpeaking();
            try {
                this.recognition.start();
            } catch (e) {
                console.error('Recognition start error:', e);
            }
        }
    },

    changeLanguage(langCode) {
        this.currentLanguage = langCode;
        if (this.recognition) {
            this.recognition.lang = langCode;
        }

        // Update UI
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === langCode);
        });

        // Greet in new language
        const greeting = this.languages[langCode].greeting;
        this.speak(greeting);
        this.updateResponseBox(greeting);
    },

    updateTranscript(text, isFinal) {
        const transcriptBox = document.getElementById('transcript-box');
        const transcriptText = document.getElementById('transcript-text');

        if (transcriptBox && transcriptText) {
            transcriptBox.classList.add('active');
            transcriptText.textContent = text;
            transcriptText.classList.toggle('final', isFinal);
        }
    },

    updateResponseBox(text) {
        const responseBox = document.getElementById('response-box');
        const responseText = document.getElementById('response-text');

        if (responseBox && responseText) {
            responseBox.classList.add('active');
            responseText.textContent = text;
        }
    },

    updateUI(state, data = '') {
        const avatar = document.getElementById('voice-avatar');
        const status = document.getElementById('voice-status');
        const micBtn = document.getElementById('mic-btn');
        const waveform = document.getElementById('voice-waveform');

        if (!avatar || !status) return;

        // Remove all state classes
        avatar.classList.remove('listening', 'speaking', 'processing', 'error');
        waveform?.classList.remove('active', 'speaking');

        switch (state) {
            case 'listening':
                avatar.classList.add('listening');
                waveform?.classList.add('active');
                status.textContent = '🎤 Listening...';
                micBtn?.querySelector('.mic-icon').style.display = 'none';
                micBtn?.querySelector('.stop-icon').style.display = 'block';
                break;

            case 'processing':
                avatar.classList.add('processing');
                status.textContent = '🧠 Thinking...';
                break;

            case 'speaking':
                avatar.classList.add('speaking');
                waveform?.classList.add('speaking');
                status.textContent = '🔊 Speaking...';
                break;

            case 'error':
                avatar.classList.add('error');
                status.textContent = `❌ Error: ${data}`;
                break;

            default:
                status.textContent = 'Tap the microphone to start';
                micBtn?.querySelector('.mic-icon').style.display = 'block';
                micBtn?.querySelector('.stop-icon').style.display = 'none';
        }
    },

    async processVoiceInput(text) {
        if (!text.trim()) return;

        this.updateUI('processing');

        // Add to history
        this.addToHistory('user', text);

        try {
            const response = await fetch(`${API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    feature: 'voice',
                    language: this.currentLanguage
                })
            });

            const data = await response.json();
            const aiResponse = data.response || 'Sorry, I could not process that.';

            // Display and speak response
            this.updateResponseBox(aiResponse);
            this.addToHistory('assistant', aiResponse);
            this.speak(aiResponse);

            // Award XP for using voice
            if (window.ProgressComponent) {
                ProgressComponent.addXP(15, 'voice_query');
                ProgressComponent.unlockBadge('voice_pioneer');
            }

        } catch (error) {
            console.error('Voice processing error:', error);
            const errorMsg = 'Sorry, there was an error processing your request.';
            this.updateResponseBox(errorMsg);
            this.speak(errorMsg);
            this.updateUI('error', 'Connection failed');
        }
    },

    speak(text) {
        if (!this.synthesis) return;

        // Cancel any ongoing speech
        this.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = this.currentLanguage;
        utterance.rate = 0.9;
        utterance.pitch = 1;

        // Try to find a voice for the language
        const voices = this.synthesis.getVoices();
        const langVoice = voices.find(v => v.lang.startsWith(this.currentLanguage.split('-')[0]));
        if (langVoice) {
            utterance.voice = langVoice;
        }

        utterance.onstart = () => {
            this.isSpeaking = true;
            this.updateUI('speaking');
        };

        utterance.onend = () => {
            this.isSpeaking = false;
            this.updateUI('idle');
        };

        utterance.onerror = (e) => {
            console.error('Speech error:', e);
            this.isSpeaking = false;
            this.updateUI('idle');
        };

        this.synthesis.speak(utterance);
    },

    stopSpeaking() {
        if (this.synthesis) {
            this.synthesis.cancel();
            this.isSpeaking = false;
            this.updateUI('idle');
        }
    },

    addToHistory(role, text) {
        this.conversationHistory.push({ role, text, time: new Date() });
        this.updateHistoryUI();
    },

    updateHistoryUI() {
        const historyList = document.getElementById('history-list');
        if (!historyList) return;

        historyList.innerHTML = this.conversationHistory
            .slice(-10) // Last 10 messages
            .map(msg => `
                <div class="history-item ${msg.role}">
                    <span class="history-icon">${msg.role === 'user' ? '👤' : '🤖'}</span>
                    <span class="history-text">${msg.text.substring(0, 100)}${msg.text.length > 100 ? '...' : ''}</span>
                </div>
            `).join('');
    },

    injectStyles() {
        if (document.getElementById('voice-counselor-styles')) return;

        const style = document.createElement('style');
        style.id = 'voice-counselor-styles';
        style.textContent = `
            .voice-counselor {
                padding: 1.5rem;
                max-width: 600px;
                margin: 0 auto;
            }

            .voice-header {
                text-align: center;
                margin-bottom: 1.5rem;
            }

            .voice-header h2 {
                font-size: 1.8rem;
                margin-bottom: 0.5rem;
                background: linear-gradient(135deg, #10a37f 0%, #1e90ff 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .voice-subtitle {
                color: var(--text-secondary, #888);
                font-size: 0.9rem;
            }

            .language-selector {
                display: flex;
                justify-content: center;
                gap: 0.5rem;
                margin-bottom: 2rem;
            }

            .lang-btn {
                padding: 0.5rem 1rem;
                border: 2px solid var(--border-color, #333);
                border-radius: 20px;
                background: transparent;
                color: var(--text-primary, #fff);
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .lang-btn.active {
                background: linear-gradient(135deg, #10a37f 0%, #1e90ff 100%);
                border-color: transparent;
            }

            .voice-avatar {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 1rem;
                margin-bottom: 1.5rem;
            }

            .avatar-circle {
                width: 120px;
                height: 120px;
                border-radius: 50%;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                border: 3px solid var(--border-color, #333);
                transition: all 0.3s ease;
            }

            .avatar-icon {
                font-size: 3rem;
                z-index: 2;
            }

            .pulse-ring {
                position: absolute;
                width: 100%;
                height: 100%;
                border-radius: 50%;
                border: 3px solid #10a37f;
                opacity: 0;
            }

            .avatar-circle.listening .pulse-ring {
                animation: pulse 1.5s infinite;
            }

            .avatar-circle.listening .pulse-ring.delay {
                animation-delay: 0.5s;
            }

            .avatar-circle.speaking {
                border-color: #1e90ff;
                box-shadow: 0 0 30px rgba(30, 144, 255, 0.5);
            }

            .avatar-circle.processing {
                animation: rotate 2s linear infinite;
            }

            @keyframes pulse {
                0% { transform: scale(1); opacity: 0.8; }
                100% { transform: scale(1.5); opacity: 0; }
            }

            @keyframes rotate {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .voice-status {
                font-size: 1rem;
                color: var(--text-secondary, #888);
            }

            .voice-waveform {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 3px;
                height: 40px;
                margin-bottom: 1.5rem;
                opacity: 0.3;
                transition: opacity 0.3s;
            }

            .voice-waveform.active,
            .voice-waveform.speaking {
                opacity: 1;
            }

            .wave-bar {
                width: 4px;
                height: 10px;
                background: linear-gradient(to top, #10a37f, #1e90ff);
                border-radius: 2px;
                transition: height 0.1s ease;
            }

            .voice-waveform.active .wave-bar {
                animation: wave 0.5s infinite;
            }

            .voice-waveform.speaking .wave-bar {
                animation: wave 0.3s infinite;
                background: linear-gradient(to top, #1e90ff, #8b5cf6);
            }

            @keyframes wave {
                0%, 100% { height: 10px; }
                50% { height: 30px; }
            }

            .wave-bar:nth-child(1) { animation-delay: 0.05s; }
            .wave-bar:nth-child(2) { animation-delay: 0.1s; }
            .wave-bar:nth-child(3) { animation-delay: 0.15s; }
            .wave-bar:nth-child(4) { animation-delay: 0.2s; }
            .wave-bar:nth-child(5) { animation-delay: 0.25s; }
            .wave-bar:nth-child(6) { animation-delay: 0.3s; }
            .wave-bar:nth-child(7) { animation-delay: 0.35s; }
            .wave-bar:nth-child(8) { animation-delay: 0.4s; }
            .wave-bar:nth-child(9) { animation-delay: 0.45s; }
            .wave-bar:nth-child(10) { animation-delay: 0.5s; }

            .transcript-box,
            .response-box {
                background: var(--card-bg, #1a1a2e);
                border: 1px solid var(--border-color, #333);
                border-radius: 12px;
                padding: 1rem;
                margin-bottom: 1rem;
                opacity: 0.5;
                transition: opacity 0.3s;
            }

            .transcript-box.active,
            .response-box.active {
                opacity: 1;
            }

            .transcript-label,
            .response-label {
                font-size: 0.75rem;
                color: var(--text-secondary, #888);
                margin-bottom: 0.5rem;
                text-transform: uppercase;
            }

            .transcript-text {
                color: var(--text-primary, #fff);
                font-style: italic;
            }

            .transcript-text.final {
                font-style: normal;
            }

            .response-text {
                color: var(--text-primary, #fff);
                line-height: 1.6;
            }

            .voice-controls {
                display: flex;
                justify-content: center;
                gap: 1rem;
                margin-bottom: 2rem;
            }

            .mic-btn {
                width: 70px;
                height: 70px;
                border-radius: 50%;
                background: linear-gradient(135deg, #10a37f 0%, #1e90ff 100%);
                border: none;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
                box-shadow: 0 4px 20px rgba(16, 163, 127, 0.4);
            }

            .mic-btn:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 30px rgba(16, 163, 127, 0.6);
            }

            .mic-btn svg {
                width: 32px;
                height: 32px;
                color: white;
            }

            .speaker-btn {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: var(--card-bg, #1a1a2e);
                border: 2px solid var(--border-color, #333);
                cursor: pointer;
                font-size: 1.5rem;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
            }

            .speaker-btn:hover {
                background: var(--border-color, #333);
            }

            .voice-history {
                margin-top: 2rem;
                padding-top: 1.5rem;
                border-top: 1px solid var(--border-color, #333);
            }

            .voice-history h3 {
                font-size: 1rem;
                color: var(--text-secondary, #888);
                margin-bottom: 1rem;
            }

            .history-list {
                max-height: 200px;
                overflow-y: auto;
            }

            .history-item {
                display: flex;
                align-items: flex-start;
                gap: 0.5rem;
                padding: 0.5rem;
                border-radius: 8px;
                margin-bottom: 0.5rem;
                font-size: 0.85rem;
            }

            .history-item.user {
                background: rgba(16, 163, 127, 0.1);
            }

            .history-item.assistant {
                background: rgba(30, 144, 255, 0.1);
            }

            .history-icon {
                flex-shrink: 0;
            }

            .history-text {
                color: var(--text-primary, #fff);
            }

            .voice-tips {
                margin-top: 2rem;
            }

            .voice-tips h4 {
                font-size: 0.9rem;
                color: var(--text-secondary, #888);
                margin-bottom: 0.75rem;
            }

            .tip-chips {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
            }

            .tip-chip {
                padding: 0.5rem 1rem;
                background: var(--card-bg, #1a1a2e);
                border: 1px solid var(--border-color, #333);
                border-radius: 20px;
                font-size: 0.85rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .tip-chip:hover {
                background: linear-gradient(135deg, #10a37f 0%, #1e90ff 100%);
                border-color: transparent;
            }
        `;
        document.head.appendChild(style);
    },

    activate() {
        this.render();
        // Speak greeting
        setTimeout(() => {
            this.speak(this.languages[this.currentLanguage].greeting);
            this.updateResponseBox(this.languages[this.currentLanguage].greeting);
        }, 500);
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    VoiceCounselorComponent.init();
});

// Export
window.VoiceCounselorComponent = VoiceCounselorComponent;
