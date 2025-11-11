document.addEventListener('DOMContentLoaded', () => {
    const showUsersBtn = document.getElementById('showUsersBtn');
    const showPhotosBtn = document.getElementById('showPhotosBtn');
    const usersSection = document.getElementById('usersSection');
    const photosSection = document.getElementById('photosSection');
    const usersTableBody = document.getElementById('usersTableBody');
    const photosTableBody = document.getElementById('photosTableBody');
    const photoCategorySelect = document.getElementById('photoCategory');
    const loadPhotosBtn = document.getElementById('loadPhotosBtn');

    let currentToken = null; // Store the JWT token

    // Function to get JWT token (e.g., from localStorage or a cookie)
    function getAuthToken() {
        // For simplicity, let's assume the token is stored in localStorage
        // In a real app, you'd have a proper login flow for the admin panel
        return localStorage.getItem('admin_token');
    }

    // Function to set JWT token
    function setAuthToken(token) {
        localStorage.setItem('admin_token', token);
        currentToken = token;
    }

    // Basic admin login (for demonstration purposes)
    async function adminLogin() {
        const username = prompt("관리자 사용자 이름을 입력하세요:");
        const password = prompt("관리자 비밀번호를 입력하세요:");

        try {
            const response = await fetch('/auth/token', { // Assuming a /token endpoint for admin login
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    username: username,
                    password: password,
                }),
            });

            if (!response.ok) {
                throw new Error('관리자 로그인 실패');
            }

            const data = await response.json();
            setAuthToken(data.access_token);
            alert('관리자 로그인 성공!');
            // After successful login, load initial data
            loadUsers();
        } catch (error) {
            console.error('Login error:', error);
            alert(error.message);
        }
    }

    // Check if token exists, if not, prompt for login
    currentToken = getAuthToken();
    if (!currentToken) {
        adminLogin();
    } else {
        loadUsers(); // Load users if token exists
    }


    // --- Section Switching ---
    showUsersBtn.addEventListener('click', () => {
        usersSection.classList.add('active');
        photosSection.classList.remove('active');
        loadUsers();
    });

    showPhotosBtn.addEventListener('click', () => {
        photosSection.classList.add('active');
        usersSection.classList.remove('active');
        loadPhotos();
    });

    // --- User Management ---
    async function loadUsers() {
        if (!currentToken) {
            alert("관리자 토큰이 없습니다. 로그인해주세요.");
            return;
        }
        try {
            const response = await fetch('/admin/users', {
                headers: {
                    'Authorization': `Bearer ${currentToken}`
                }
            });
            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                    alert("인증 실패 또는 권한이 없습니다. 다시 로그인해주세요.");
                    setAuthToken(null); // Clear invalid token
                    adminLogin();
                    return;
                }
                throw new Error('사용자 데이터를 불러오는데 실패했습니다.');
            }
            const users = await response.json();
            renderUsers(users);
        } catch (error) {
            console.error('Error loading users:', error);
            alert('사용자 데이터를 불러오는 중 오류가 발생했습니다.');
        }
    }

    function renderUsers(users) {
        usersTableBody.innerHTML = '';
        users.forEach(user => {
            const row = usersTableBody.insertRow();
            row.insertCell().textContent = user.id;
            row.insertCell().textContent = user.email;
            row.insertCell().textContent = user.name;
            
            const activeCell = row.insertCell();
            const activeToggle = document.createElement('input');
            activeToggle.type = 'checkbox';
            activeToggle.checked = user.is_active;
            activeToggle.addEventListener('change', () => updateUserStatus(user.id, 'is_active', activeToggle.checked));
            activeCell.appendChild(activeToggle);

            const superuserCell = row.insertCell();
            const superuserToggle = document.createElement('input');
            superuserToggle.type = 'checkbox';
            superuserToggle.checked = user.is_superuser;
            superuserToggle.addEventListener('change', () => updateUserStatus(user.id, 'is_superuser', superuserToggle.checked));
            superuserCell.appendChild(superuserToggle);

            row.insertCell().textContent = new Date(user.created_at).toLocaleString();
            
            const actionsCell = row.insertCell();
            const deleteBtn = document.createElement('button');
            deleteBtn.textContent = '삭제';
            deleteBtn.classList.add('delete-btn');
            deleteBtn.addEventListener('click', () => deleteUser(user.id));
            actionsCell.appendChild(deleteBtn);
        });
    }

    async function updateUserStatus(userId, field, value) {
        if (!currentToken) {
            alert("관리자 토큰이 없습니다. 로그인해주세요.");
            return;
        }
        try {
            const response = await fetch(`/admin/users/${userId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${currentToken}`
                },
                body: JSON.stringify({ [field]: value }),
            });
            if (!response.ok) {
                throw new Error('사용자 상태 업데이트 실패');
            }
            alert('사용자 상태가 업데이트되었습니다.');
            loadUsers(); // Reload users to reflect changes
        } catch (error) {
            console.error('Error updating user status:', error);
            alert('사용자 상태 업데이트 중 오류가 발생했습니다.');
        }
    }

    async function deleteUser(userId) {
        if (!confirm(`정말로 사용자 ID ${userId}를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.`)) {
            return;
        }
        if (!currentToken) {
            alert("관리자 토큰이 없습니다. 로그인해주세요.");
            return;
        }
        try {
            const response = await fetch(`/admin/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${currentToken}`
                },
            });
            if (!response.ok) {
                throw new Error('사용자 삭제 실패');
            }
            alert('사용자가 삭제되었습니다.');
            loadUsers(); // Reload users
        } catch (error) {
            console.error('Error deleting user:', error);
            alert('사용자 삭제 중 오류가 발생했습니다.');
        }
    }

    // --- Photo Management ---
    loadPhotosBtn.addEventListener('click', loadPhotos);

    async function loadPhotos() {
        if (!currentToken) {
            alert("관리자 토큰이 없습니다. 로그인해주세요.");
            return;
        }
        const category = photoCategorySelect.value;
        try {
            const response = await fetch(`/admin/photos/${category}`, {
                headers: {
                    'Authorization': `Bearer ${currentToken}`
                }
            });
            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                    alert("인증 실패 또는 권한이 없습니다. 다시 로그인해주세요.");
                    setAuthToken(null);
                    adminLogin();
                    return;
                }
                throw new Error('사진 데이터를 불러오는데 실패했습니다.');
            }
            const photos = await response.json();
            renderPhotos(photos, category);
        } catch (error) {
            console.error('Error loading photos:', error);
            alert('사진 데이터를 불러오는 중 오류가 발생했습니다.');
        }
    }

    function renderPhotos(photos, category) {
        photosTableBody.innerHTML = '';
        photos.forEach(photo => {
            const row = photosTableBody.insertRow();
            row.insertCell().textContent = photo.id;
            row.insertCell().textContent = photo.filename;
            row.insertCell().textContent = photo.user_id; // Assuming user_id is available
            row.insertCell().textContent = new Date(photo.uploaded_at || photo.created_at).toLocaleString();
            
            const previewCell = row.insertCell();
            const img = document.createElement('img');
            img.src = `/images/${category}/${photo.filename}`; // Use the public image endpoint
            img.alt = photo.filename;
            img.style.maxWidth = '100px';
            img.style.maxHeight = '100px';
            previewCell.appendChild(img);

            const actionsCell = row.insertCell();
            const deleteBtn = document.createElement('button');
            deleteBtn.textContent = '삭제';
            deleteBtn.classList.add('delete-btn');
            deleteBtn.addEventListener('click', () => deletePhoto(category, photo.id));
            actionsCell.appendChild(deleteBtn);
        });
    }

    async function deletePhoto(category, photoId) {
        if (!confirm(`정말로 ${category} 카테고리의 사진 ID ${photoId}를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.`)) {
            return;
        }
        if (!currentToken) {
            alert("관리자 토큰이 없습니다. 로그인해주세요.");
            return;
        }
        try {
            const response = await fetch(`/admin/photos/${category}/${photoId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${currentToken}`
                },
            });
            if (!response.ok) {
                throw new Error('사진 삭제 실패');
            }
            alert('사진이 삭제되었습니다.');
            loadPhotos(); // Reload photos
        } catch (error) {
            console.error('Error deleting photo:', error);
            alert('사진 삭제 중 오류가 발생했습니다.');
        }
    }
});
