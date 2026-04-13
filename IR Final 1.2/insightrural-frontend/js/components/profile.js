// Profile Component
const ProfileComponent = {
    init() {
        this.editProfileBtn = document.getElementById('edit-profile-btn');
        this.profileModal = document.getElementById('profile-modal');
        this.profileForm = document.getElementById('profile-form');
        
        this.setupEventListeners();
    },
    
    setupEventListeners() {
        // Edit profile button
        this.editProfileBtn.addEventListener('click', () => {
            this.showProfileModal();
        });
        
        // Close modal
        const closeBtn = this.profileModal.querySelector('.close-modal');
        closeBtn.addEventListener('click', () => {
            this.hideProfileModal();
        });
        
        // Cancel button
        const cancelBtn = this.profileModal.querySelector('.cancel-btn');
        cancelBtn.addEventListener('click', () => {
            this.hideProfileModal();
        });
        
        // Form submission
        this.profileForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveProfile();
        });
        
        // Close when clicking outside
        this.profileModal.addEventListener('click', (e) => {
            if (e.target === this.profileModal) {
                this.hideProfileModal();
            }
        });
    },
    
    showProfileModal() {
        this.profileModal.classList.add('active');
    },
    
    hideProfileModal() {
        this.profileModal.classList.remove('active');
    },
    
    saveProfile() {
        const name = document.getElementById('edit-name').value;
        const location = document.getElementById('edit-location').value;
        const stream = document.getElementById('edit-stream').value;
        const finance = document.getElementById('edit-finance').value;
        
        // Update profile display
        document.getElementById('student-name').textContent = name;
        document.querySelector('.location').textContent = `📍 ${location}`;
        document.querySelectorAll('.profile-tag')[0].innerHTML = 
            `<span class="tag-icon">🎓</span><span>${stream}</span>`;
        document.querySelectorAll('.profile-tag')[1].innerHTML = 
            `<span class="tag-icon">💰</span><span>${finance}</span>`;
        
        // Update avatar initials
        const initials = name.split(' ').map(n => n[0]).join('').toUpperCase();
        document.querySelector('.avatar').textContent = initials;
        
        this.hideProfileModal();
        alert('Profile updated successfully!');
    }
};