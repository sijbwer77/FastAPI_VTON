window.addEventListener('DOMContentLoaded', () => {
    const authSection = document.getElementById('auth-section');
    const userInfoSection = document.getElementById('user-info');
    const userDetails = document.getElementById('user-details');
    const logoutBtn = document.getElementById('logout-btn');

    const token = localStorage.getItem('vton-token');

    // Handle redirect from OAuth
    // e.g. http://localhost:8000/#token=...
    if (window.location.hash.startsWith('#token=')) {
        const hash = window.location.hash.substring(7); // Remove #token=
        localStorage.setItem('vton-token', hash);
        // Clean the URL
        window.history.replaceState(null, null, ' ');
        // Reload to reflect logged-in state
        window.location.reload();
        return;
    }

    if (token) {
        // User is logged in
        authSection.classList.add('hidden');
        userInfoSection.classList.remove('hidden');
        fetchUserInfo(token);
    } else {
        // User is not logged in
        authSection.classList.remove('hidden');
        userInfoSection.classList.add('hidden');
    }

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('vton-token');
        window.location.reload();
    });

    async function fetchUserInfo(token) {
        try {
            const response = await fetch('/users/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.status === 401) {
                // Token is invalid or expired
                localStorage.removeItem('vton-token');
                window.location.reload();
                return;
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const user = await response.json();
            userDetails.textContent = JSON.stringify(user, null, 2);

        } catch (error) {
            userDetails.textContent = `사용자 정보를 가져오는 데 실패했습니다: ${error}`;
        }
    }
});
