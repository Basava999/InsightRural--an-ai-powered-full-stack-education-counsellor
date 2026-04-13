// Main Application Initialization
document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 InsightRural Frontend Initializing...');

    // Initialize state
    AppState.init();

    // Initialize core components
    SidebarComponent.init();
    ChatComponent.init();

    // Initialize new startup components (they self-initialize, just log)
    console.log('📱 PWA utilities loaded');
    console.log('📊 Dashboard component loaded');
    console.log('📁 Documents component loaded');
    console.log('🏆 Progress/Gamification component loaded');

    console.log('✅ InsightRural Frontend Ready!');
});