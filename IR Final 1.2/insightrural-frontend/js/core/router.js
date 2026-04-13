// Feature Router - Handles navigation between features
const FeatureRouter = {
    // Initialize router
    init() {
        this.setupNavigation();
    },
    
    // Setup sidebar navigation
    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item[data-feature]');
        
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const feature = item.dataset.feature;
                if (feature) {
                    this.navigateToFeature(feature);
                    // Close sidebar on mobile after selection
                    if (window.innerWidth <= 1024) {
                        SidebarComponent.closeSidebar();
                    }
                }
            });
        });
    },
    
    // Navigate to a specific feature
    navigateToFeature(feature) {
        // Use SidebarComponent.showSection which handles all section
        // switching correctly (hides others, shows target, dispatches events)
        if (typeof SidebarComponent !== 'undefined' && SidebarComponent.showSection) {
            SidebarComponent.showSection(feature);
        }

        // Update active nav item
        this.updateActiveNavItem(feature);
    },
    
    // Update active navigation item
    updateActiveNavItem(feature) {
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            if (item.dataset.feature === feature) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }
};