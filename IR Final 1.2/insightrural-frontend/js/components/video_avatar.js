// AI Video Avatar Component
// Animated AI counselor avatar with text-to-speech

const VideoAvatarComponent = {
    isSpeaking: false,
    synthesis: window.speechSynthesis,
    currentMessage: '',
    messageQueue: [],

    // Avatar expressions
    expressions: {
        neutral: '🤖',
        happy: '😊',
        thinking: '🤔',
        excited: '🤩',
        concerned: '😟',
        explaining: '👨‍🏫'
    },

    init() {
        this.injectStyles();
        console.log('🎬 Video Avatar initialized');
    },

    render() {
        const container = document.getElementById('avatar-section');
        if (!container) return;

        container.innerHTML = `
            <div class="video-avatar-container">
                <div class="avatar-header">
                    <h2>🎬 AI Video Counselor</h2>
                    <p class="avatar-subtitle">Your personal AI counselor speaks to you</p>
                </div>

                <div class="avatar-stage">
                    <div class="avatar-background">
                        <div class="bg-circle"></div>
                        <div class="bg-circle delay"></div>
                    </div>

                    <div class="avatar-figure" id="avatar-figure">
                        <div class="avatar-head">
                            <div class="avatar-face" id="avatar-face">
                                <div class="avatar-eyes">
                                    <div class="eye left" id="eye-left"></div>
                                    <div class="eye right" id="eye-right"></div>
                                </div>
                                <div class="avatar-mouth" id="avatar-mouth"></div>
                            </div>
                        </div>
                        <div class="avatar-body">
                            <div class="avatar-tie"></div>
                        </div>
                    </div>

                    <div class="sound-waves" id="sound-waves">
                        ${Array(12).fill().map(() => '<div class="sound-wave"></div>').join('')}
                    </div>
                </div>

                <div class="avatar-speech-bubble" id="speech-bubble">
                    <div class="bubble-content" id="bubble-content">
                        Click "Generate Greeting" to hear your AI counselor!
                    </div>
                </div>

                <div class="avatar-controls">
                    <div class="topic-selector">
                        <label>Choose a topic:</label>
                        <select id="avatar-topic">
                            <option value="greeting">👋 Welcome Greeting</option>
                            <option value="college">🎓 College Guidance</option>
                            <option value="scholarship">💰 Scholarship Info</option>
                            <option value="motivation">💪 Motivational Message</option>
                            <option value="deadlines">⏰ Important Deadlines</option>
                            <option value="tips">💡 Application Tips</option>
                        </select>
                    </div>

                    <div class="language-selector">
                        <button class="lang-btn active" data-lang="en-IN">English</button>
                        <button class="lang-btn" data-lang="hi-IN">हिंदी</button>
                        <button class="lang-btn" data-lang="kn-IN">ಕನ್ನಡ</button>
                    </div>

                    <div class="action-buttons">
                        <button class="avatar-btn primary" id="generate-video">
                            ✨ Generate Message
                        </button>
                        <button class="avatar-btn secondary" id="stop-avatar">
                            ⏹️ Stop
                        </button>
                    </div>
                </div>

                <div class="personalization-box">
                    <h4>📝 Personalize Your Message</h4>
                    <div class="personal-inputs">
                        <input type="text" id="student-name" placeholder="Your name" value="">
                        <input type="number" id="student-rank" placeholder="Your KCET rank">
                    </div>
                </div>

                <div class="sample-videos">
                    <h4>📺 Quick Messages</h4>
                    <div class="video-cards">
                        <div class="video-card" data-topic="greeting">
                            <span class="card-emoji">👋</span>
                            <span class="card-title">Welcome</span>
                        </div>
                        <div class="video-card" data-topic="motivation">
                            <span class="card-emoji">🔥</span>
                            <span class="card-title">Stay Motivated</span>
                        </div>
                        <div class="video-card" data-topic="deadlines">
                            <span class="card-emoji">⏰</span>
                            <span class="card-title">Deadlines</span>
                        </div>
                        <div class="video-card" data-topic="tips">
                            <span class="card-emoji">🎯</span>
                            <span class="card-title">Pro Tips</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.setupEventListeners();
        this.startBlinking();
    },

    setupEventListeners() {
        const generateBtn = document.getElementById('generate-video');
        const stopBtn = document.getElementById('stop-avatar');

        generateBtn?.addEventListener('click', () => this.generateMessage());
        stopBtn?.addEventListener('click', () => this.stopSpeaking());

        // Language buttons
        document.querySelectorAll('.video-avatar-container .lang-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.video-avatar-container .lang-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        // Video cards
        document.querySelectorAll('.video-card').forEach(card => {
            card.addEventListener('click', () => {
                document.getElementById('avatar-topic').value = card.dataset.topic;
                this.generateMessage();
            });
        });
    },

    startBlinking() {
        setInterval(() => {
            if (!this.isSpeaking) {
                const leftEye = document.getElementById('eye-left');
                const rightEye = document.getElementById('eye-right');
                if (leftEye && rightEye) {
                    leftEye.classList.add('blink');
                    rightEye.classList.add('blink');
                    setTimeout(() => {
                        leftEye.classList.remove('blink');
                        rightEye.classList.remove('blink');
                    }, 150);
                }
            }
        }, 3000);
    },

    async generateMessage() {
        const topic = document.getElementById('avatar-topic').value;
        const name = document.getElementById('student-name').value || 'Student';
        const rank = document.getElementById('student-rank').value || '';
        const langBtn = document.querySelector('.video-avatar-container .lang-btn.active');
        const language = langBtn?.dataset.lang || 'en-IN';

        // Get message from AI or use pre-written
        let message = await this.getMessageForTopic(topic, name, rank, language);

        // Display and speak
        this.displayMessage(message);
        this.speak(message, language);
    },

    async getMessageForTopic(topic, name, rank, language) {
        // Pre-written messages for each topic
        const messages = {
            'en-IN': {
                greeting: `Hello ${name}! Welcome to InsightRural, your AI-powered educational counselor. I'm here to help you navigate your KCET journey and find the perfect college for your future. Whether you need guidance on colleges, scholarships, or career paths, I've got you covered. Let's make your dreams come true together!`,
                college: rank
                    ? `${name}, with your KCET rank of ${rank}, you have some excellent options. Based on my analysis, you could target colleges like RV College, BMS College, or NIE Mysore. Remember, the best college is one that aligns with your interests and career goals. Would you like me to help you explore specific branches?`
                    : `${name}, choosing the right college is a crucial decision. Consider factors like placement records, faculty quality, infrastructure, and location. I recommend looking at top colleges like RVCE, BMSCE, and NIE. Tell me your rank, and I can give you personalized recommendations!`,
                scholarship: `Listen carefully, ${name}! There are many scholarships waiting for bright students like you. The Post-Matric Scholarship provides up to 100% fee waiver for SC/ST students. The Central Sector Scholarship offers ₹20,000 per year. Karnataka also has the Vidyasiri scholarship. Make sure you apply before the deadlines. I can help you check your eligibility!`,
                motivation: `${name}, I believe in you! This KCET journey might seem challenging, but remember - every great engineer, doctor, and leader once stood where you are now. Your rank is just a number; your determination defines your destiny. Work hard, stay focused, and never give up. The best colleges are waiting for students who dare to dream big!`,
                deadlines: `Important reminder, ${name}! The KCET counselling dates are crucial. First round usually starts in late August. Document verification begins in September. Don't miss the option entry dates! Keep all your documents ready - marksheets, category certificates, and income proof. I'll help you stay on track!`,
                tips: `Here are my top tips for you, ${name}! First, always keep multiple college options ready. Second, verify your documents early. Third, understand the fee structure before choosing. Fourth, talk to current students of colleges you're interested in. Fifth, don't just follow the crowd - choose a branch you're passionate about. Your career success depends on your choices today!`
            },
            'hi-IN': {
                greeting: `नमस्ते ${name}! InsightRural में आपका स्वागत है। मैं आपका AI शिक्षा सलाहकार हूं। KCET की इस यात्रा में मैं आपकी मदद करने के लिए यहां हूं। कॉलेज, स्कॉलरशिप, या करियर - किसी भी सवाल के लिए मुझसे पूछें!`,
                college: `${name}, कॉलेज चुनना एक महत्वपूर्ण निर्णय है। प्लेसमेंट रिकॉर्ड, फैकल्टी, और इंफ्रास्ट्रक्चर पर ध्यान दें। TOP कॉलेज जैसे RVCE, BMSCE, NIE देखें।`,
                motivation: `${name}, मुझे आप पर विश्वास है! हर महान इंजीनियर कभी वहीं खड़ा था जहां आप आज हैं। मेहनत करें, फोकस रहें, कभी हार न मानें!`,
                scholarship: `${name}, SC/ST छात्रों के लिए Post-Matric Scholarship 100% फीस माफी देती है। Central Sector Scholarship ₹20,000 सालाना देती है।`,
                deadlines: `${name}, KCET काउंसलिंग की तारीखें महत्वपूर्ण हैं! सभी दस्तावेज तैयार रखें।`,
                tips: `${name}, मेरी टिप्स: कई कॉलेज विकल्प रखें, दस्तावेज़ जल्दी वेरीफाई करें, फीस समझें, और अपने पसंद की ब्रांच चुनें!`
            },
            'kn-IN': {
                greeting: `ನಮಸ್ಕಾರ ${name}! InsightRural ಗೆ ಸ್ವಾಗತ. ನಾನು ನಿಮ್ಮ AI ಶಿಕ್ಷಣ ಸಲಹೆಗಾರ. KCET ಪ್ರಯಾಣದಲ್ಲಿ ನಿಮಗೆ ಸಹಾಯ ಮಾಡಲು ನಾನು ಇಲ್ಲಿದ್ದೇನೆ!`,
                college: `${name}, ಕಾಲೇಜು ಆಯ್ಕೆ ಮಹತ್ವದ ನಿರ್ಧಾರ. RVCE, BMSCE, NIE ಮುಂತಾದ ಉನ್ನತ ಕಾಲೇಜುಗಳನ್ನು ನೋಡಿ.`,
                motivation: `${name}, ನನಗೆ ನಿಮ್ಮ ಮೇಲೆ ನಂಬಿಕೆ ಇದೆ! ಕಠಿಣ ಪರಿಶ್ರಮ ಮಾಡಿ, ಎಂದಿಗೂ ಬಿಟ್ಟುಕೊಡಬೇಡಿ!`,
                scholarship: `${name}, SC/ST ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ 100% ಶುಲ್ಕ ಮನ್ನಾ ಇದೆ. Vidyasiri ವಿದ್ಯಾರ್ಥಿವೇತನಕ್ಕೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ!`,
                deadlines: `${name}, KCET ಕೌನ್ಸೆಲಿಂಗ್ ದಿನಾಂಕಗಳು ಮುಖ್ಯ! ಎಲ್ಲಾ ದಾಖಲೆಗಳನ್ನು ಸಿದ್ಧವಾಗಿ ಇಟ್ಟುಕೊಳ್ಳಿ.`,
                tips: `${name}, ನನ್ನ ಸಲಹೆಗಳು: ಹಲವು ಕಾಲೇಜು ಆಯ್ಕೆಗಳನ್ನು ಇಟ್ಟುಕೊಳ್ಳಿ, ದಾಖಲೆಗಳನ್ನು ಬೇಗ ಪರಿಶೀಲಿಸಿ!`
            }
        };

        const lang = messages[language] ? language : 'en-IN';
        return messages[lang][topic] || messages[lang].greeting;
    },

    displayMessage(text) {
        const bubble = document.getElementById('bubble-content');
        if (bubble) {
            bubble.textContent = '';
            // Typewriter effect
            let i = 0;
            const typeWriter = () => {
                if (i < text.length) {
                    bubble.textContent += text.charAt(i);
                    i++;
                    setTimeout(typeWriter, 30);
                }
            };
            typeWriter();
        }
    },

    speak(text, language) {
        if (!this.synthesis) return;

        this.synthesis.cancel();
        this.startSpeakingAnimation();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = language;
        utterance.rate = 0.85;
        utterance.pitch = 1;

        // Try to find a voice for the language
        const voices = this.synthesis.getVoices();
        const langVoice = voices.find(v => v.lang.startsWith(language.split('-')[0]));
        if (langVoice) {
            utterance.voice = langVoice;
        }

        utterance.onstart = () => {
            this.isSpeaking = true;
            this.startSpeakingAnimation();
        };

        utterance.onend = () => {
            this.isSpeaking = false;
            this.stopSpeakingAnimation();

            // Award XP
            if (window.ProgressComponent) {
                ProgressComponent.addXP(15, 'video_avatar');
            }
        };

        utterance.onerror = () => {
            this.isSpeaking = false;
            this.stopSpeakingAnimation();
        };

        this.synthesis.speak(utterance);
    },

    startSpeakingAnimation() {
        const avatarFigure = document.getElementById('avatar-figure');
        const soundWaves = document.getElementById('sound-waves');
        const mouth = document.getElementById('avatar-mouth');

        avatarFigure?.classList.add('speaking');
        soundWaves?.classList.add('active');
        mouth?.classList.add('talking');
    },

    stopSpeakingAnimation() {
        const avatarFigure = document.getElementById('avatar-figure');
        const soundWaves = document.getElementById('sound-waves');
        const mouth = document.getElementById('avatar-mouth');

        avatarFigure?.classList.remove('speaking');
        soundWaves?.classList.remove('active');
        mouth?.classList.remove('talking');
    },

    stopSpeaking() {
        if (this.synthesis) {
            this.synthesis.cancel();
            this.isSpeaking = false;
            this.stopSpeakingAnimation();
        }
    },

    injectStyles() {
        if (document.getElementById('video-avatar-styles')) return;

        const style = document.createElement('style');
        style.id = 'video-avatar-styles';
        style.textContent = `
            .video-avatar-container {
                padding: 1.5rem;
                max-width: 600px;
                margin: 0 auto;
            }

            .avatar-header {
                text-align: center;
                margin-bottom: 1.5rem;
            }

            .avatar-header h2 {
                font-size: 1.8rem;
                margin-bottom: 0.5rem;
                background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .avatar-stage {
                position: relative;
                height: 250px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 1rem;
            }

            .avatar-background {
                position: absolute;
                width: 200px;
                height: 200px;
            }

            .bg-circle {
                position: absolute;
                width: 100%;
                height: 100%;
                border-radius: 50%;
                background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(168, 85, 247, 0.1) 100%);
                animation: pulse-bg 3s ease-in-out infinite;
            }

            .bg-circle.delay {
                animation-delay: 1.5s;
            }

            @keyframes pulse-bg {
                0%, 100% { transform: scale(1); opacity: 0.5; }
                50% { transform: scale(1.2); opacity: 0.2; }
            }

            .avatar-figure {
                position: relative;
                z-index: 10;
                transition: all 0.3s ease;
            }

            .avatar-figure.speaking {
                animation: avatar-bounce 0.5s ease-in-out infinite;
            }

            @keyframes avatar-bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-5px); }
            }

            .avatar-head {
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                box-shadow: 0 10px 30px rgba(251, 191, 36, 0.3);
            }

            .avatar-face {
                width: 80%;
                height: 80%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }

            .avatar-eyes {
                display: flex;
                gap: 20px;
                margin-bottom: 10px;
            }

            .eye {
                width: 12px;
                height: 12px;
                background: #1a1a2e;
                border-radius: 50%;
                position: relative;
            }

            .eye::after {
                content: '';
                position: absolute;
                top: 2px;
                left: 2px;
                width: 4px;
                height: 4px;
                background: white;
                border-radius: 50%;
            }

            .eye.blink {
                height: 2px;
            }

            .avatar-mouth {
                width: 30px;
                height: 6px;
                background: #8b4513;
                border-radius: 0 0 15px 15px;
                transition: all 0.1s ease;
            }

            .avatar-mouth.talking {
                animation: talk 0.2s infinite;
            }

            @keyframes talk {
                0%, 100% { height: 6px; border-radius: 0 0 15px 15px; }
                50% { height: 15px; border-radius: 50%; }
            }

            .avatar-body {
                width: 80px;
                height: 60px;
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                border-radius: 0 0 40px 40px;
                margin: -10px auto 0;
                position: relative;
            }

            .avatar-tie {
                width: 15px;
                height: 30px;
                background: #ef4444;
                position: absolute;
                left: 50%;
                transform: translateX(-50%);
                top: 5px;
                clip-path: polygon(50% 0%, 100% 15%, 80% 100%, 50% 85%, 20% 100%, 0% 15%);
            }

            .sound-waves {
                position: absolute;
                display: flex;
                gap: 4px;
                align-items: center;
                height: 60px;
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .sound-waves.active {
                opacity: 1;
            }

            .sound-wave {
                width: 4px;
                height: 20px;
                background: linear-gradient(to top, #6366f1, #a855f7);
                border-radius: 2px;
            }

            .sound-waves.active .sound-wave {
                animation: wave-anim 0.3s ease-in-out infinite;
            }

            @keyframes wave-anim {
                0%, 100% { height: 10px; }
                50% { height: 40px; }
            }

            .sound-wave:nth-child(1) { animation-delay: 0.05s; }
            .sound-wave:nth-child(2) { animation-delay: 0.1s; }
            .sound-wave:nth-child(3) { animation-delay: 0.15s; }
            .sound-wave:nth-child(4) { animation-delay: 0.2s; }
            .sound-wave:nth-child(5) { animation-delay: 0.25s; }
            .sound-wave:nth-child(6) { animation-delay: 0.3s; }
            .sound-wave:nth-child(7) { animation-delay: 0.25s; }
            .sound-wave:nth-child(8) { animation-delay: 0.2s; }
            .sound-wave:nth-child(9) { animation-delay: 0.15s; }
            .sound-wave:nth-child(10) { animation-delay: 0.1s; }
            .sound-wave:nth-child(11) { animation-delay: 0.05s; }
            .sound-wave:nth-child(12) { animation-delay: 0s; }

            .avatar-speech-bubble {
                background: var(--card-bg, #1a1a2e);
                border: 1px solid var(--border-color, #333);
                border-radius: 16px;
                padding: 1rem 1.5rem;
                margin-bottom: 1.5rem;
                position: relative;
                min-height: 80px;
            }

            .avatar-speech-bubble::before {
                content: '';
                position: absolute;
                top: -10px;
                left: 50%;
                transform: translateX(-50%);
                border-left: 10px solid transparent;
                border-right: 10px solid transparent;
                border-bottom: 10px solid var(--border-color, #333);
            }

            .bubble-content {
                color: var(--text-primary, #fff);
                line-height: 1.6;
                font-size: 0.95rem;
            }

            .avatar-controls {
                display: flex;
                flex-direction: column;
                gap: 1rem;
                margin-bottom: 1.5rem;
            }

            .topic-selector {
                display: flex;
                gap: 1rem;
                align-items: center;
            }

            .topic-selector label {
                color: var(--text-secondary, #888);
                font-size: 0.9rem;
            }

            .topic-selector select {
                flex: 1;
                padding: 0.75rem;
                border: 1px solid var(--border-color, #333);
                border-radius: 8px;
                background: var(--bg-color, #0a0a0f);
                color: var(--text-primary, #fff);
            }

            .video-avatar-container .language-selector {
                display: flex;
                justify-content: center;
                gap: 0.5rem;
            }

            .video-avatar-container .lang-btn {
                padding: 0.5rem 1rem;
                border: 1px solid var(--border-color, #333);
                border-radius: 20px;
                background: transparent;
                color: var(--text-primary, #fff);
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .video-avatar-container .lang-btn.active {
                background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
                border-color: transparent;
            }

            .action-buttons {
                display: flex;
                gap: 1rem;
            }

            .avatar-btn {
                flex: 1;
                padding: 1rem;
                border: none;
                border-radius: 12px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .avatar-btn.primary {
                background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
                color: white;
            }

            .avatar-btn.secondary {
                background: var(--card-bg, #1a1a2e);
                border: 1px solid var(--border-color, #333);
                color: var(--text-primary, #fff);
            }

            .personalization-box {
                background: var(--card-bg, #1a1a2e);
                border-radius: 12px;
                padding: 1rem;
                margin-bottom: 1.5rem;
            }

            .personalization-box h4 {
                margin: 0 0 0.75rem 0;
                color: var(--text-secondary, #888);
                font-size: 0.9rem;
            }

            .personal-inputs {
                display: flex;
                gap: 1rem;
            }

            .personal-inputs input {
                flex: 1;
                padding: 0.75rem;
                border: 1px solid var(--border-color, #333);
                border-radius: 8px;
                background: var(--bg-color, #0a0a0f);
                color: var(--text-primary, #fff);
            }

            .sample-videos h4 {
                margin: 0 0 0.75rem 0;
                color: var(--text-secondary, #888);
            }

            .video-cards {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 0.5rem;
            }

            .video-card {
                background: var(--card-bg, #1a1a2e);
                border: 1px solid var(--border-color, #333);
                border-radius: 12px;
                padding: 1rem 0.5rem;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .video-card:hover {
                border-color: #a855f7;
                transform: translateY(-2px);
            }

            .card-emoji {
                font-size: 1.5rem;
                display: block;
                margin-bottom: 0.25rem;
            }

            .card-title {
                font-size: 0.75rem;
                color: var(--text-secondary, #888);
            }

            @media (max-width: 600px) {
                .video-cards {
                    grid-template-columns: repeat(2, 1fr);
                }

                .personal-inputs {
                    flex-direction: column;
                }

                .topic-selector {
                    flex-direction: column;
                    align-items: stretch;
                }
            }
        `;
        document.head.appendChild(style);
    },

    activate() {
        this.render();
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    VideoAvatarComponent.init();
});

// Export
window.VideoAvatarComponent = VideoAvatarComponent;
