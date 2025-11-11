// --- State ---
let authToken = null;
let currentUser = null;

// --- DOM Elements ---
const loginBtn = document.getElementById('loginBtn');
const userProfile = document.getElementById('userProfile');

// --- Functions ---
async function fetchUserProfile() {
    if (!authToken) return;
    try {
        const response = await fetch('/users/me', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (!response.ok) {
            localStorage.removeItem('vton_token');
            authToken = null;
            handleAuthentication(); // Re-run to update UI
            return null;
        }
        currentUser = await response.json();

        if (loginBtn) loginBtn.classList.add('hidden');
        if (userProfile) {
            userProfile.classList.remove('hidden');
            userProfile.innerHTML = `<img src="${currentUser.profile_image}" alt="${currentUser.name}" title="${currentUser.name}" class="user-avatar">`;
        }
        return currentUser;
    } catch (error)
        {
        console.error("Failed to fetch user profile:", error);
        return null;
    }
}

function handleAuthentication(callback) {
    const hash = window.location.hash;
    if (hash.startsWith('#token=')) {
        const token = hash.substring(7);
        localStorage.setItem('vton_token', token);
        window.location.hash = '';
    }
    authToken = localStorage.getItem('vton_token');

    if (authToken) {
        fetchUserProfile().then(user => {
            if (callback) callback(user, authToken);
        });
    } else {
        if (loginBtn) loginBtn.classList.remove('hidden');
        if (userProfile) userProfile.classList.add('hidden');
        if (callback) callback(null, null);
    }
}

function setupAuth() {
    if (loginBtn) {
        loginBtn.addEventListener('click', () => {
            window.location.href = '/auth/google/login';
        });
    }
}

export { handleAuthentication, setupAuth };
