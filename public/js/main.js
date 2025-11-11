import { handleAuthentication, setupAuth } from './auth.js';
import { setupGallery } from './gallery.js';
import { setupTryOnPanel, handleClothSelection, loadPersonPhotos } from './tryon.js';

document.addEventListener('DOMContentLoaded', () => {
    let currentUser = null;
    let authToken = null;

    // 1. Setup authentication
    setupAuth();

    // 2. Handle authentication and then initialize other modules
    handleAuthentication((user, token) => {
        currentUser = user;
        authToken = token;

        // After auth, load user-specific content
        if (user) {
            loadPersonPhotos(token);
        }
        
        // Pass getters for state to avoid circular dependencies or global state
        const getAuthToken = () => authToken;
        const getCurrentUser = () => currentUser;
        
        // 3. Setup the try-on panel
        // It's mostly independent but needs auth info for generation
        setupTryOnPanel(getAuthToken, getCurrentUser);
    });

    // 4. Setup the gallery and connect it to the try-on panel
    setupGallery(handleClothSelection);
});
