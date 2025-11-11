// --- DOM Elements ---
const personImageDisplay = document.getElementById('person-image-display');
const personPhotoSelector = document.getElementById('person-photo-selector');
const clothImageDisplay = document.getElementById('cloth-image-display');
const resultImageDisplay = document.getElementById('result-image-display');
const generateBtn = document.getElementById('generateBtn');

// --- State ---
let selectedPerson = null;
let selectedCloth = null;

// --- Functions ---
function updateGenerateButtonState() {
    if (generateBtn) {
        generateBtn.disabled = !(selectedPerson && selectedCloth);
    }
}

async function loadPersonPhotos(authToken) {
    if (!authToken) {
        if (personPhotoSelector) personPhotoSelector.innerHTML = '<small>로그인 후 이용 가능합니다.</small>';
        return;
    }
    if (!personPhotoSelector || !personImageDisplay) return;

    try {
        const response = await fetch('/images/persons', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (!response.ok) throw new Error('Failed to load person photos.');
        const photos = await response.json();

        personPhotoSelector.innerHTML = '';
        personImageDisplay.innerHTML = '';

        if (photos.length > 0) {
            const firstPhoto = photos[0];
            selectedPerson = { id: firstPhoto.id, filename: firstPhoto.filename };
            personImageDisplay.innerHTML = `<img src="/images/persons/${firstPhoto.filename}" alt="${firstPhoto.filename}">`;
        }

        photos.forEach((photo, index) => {
            const img = document.createElement('img');
            img.src = `/images/persons/${photo.filename}`;
            img.alt = photo.filename;
            img.className = 'thumbnail';
            img.dataset.id = photo.id;
            img.dataset.filename = photo.filename;

            if (index === 0) {
                img.classList.add('selected');
            }
            personPhotoSelector.appendChild(img);
        });
        updateGenerateButtonState();
    } catch (error) {
        console.error("Error loading person photos:", error);
        personPhotoSelector.innerHTML = '<small>사진 로딩 실패</small>';
    }
}

function setupTryOnPanel(getAuthToken, getCurrentUser) {
    // This function is called after authentication is handled.
    const authToken = getAuthToken();
    if (authToken) {
        loadPersonPhotos(authToken);
    }

    if (personPhotoSelector) {
        personPhotoSelector.addEventListener('click', (e) => {
            if (e.target && e.target.classList.contains('thumbnail')) {
                document.querySelectorAll('.thumbnail-container .thumbnail').forEach(thumb => {
                    thumb.classList.remove('selected');
                });
                e.target.classList.add('selected');

                const id = e.target.dataset.id;
                const filename = e.target.dataset.filename;
                selectedPerson = { id, filename };
                if (personImageDisplay) {
                    personImageDisplay.innerHTML = `<img src="/images/persons/${filename}" alt="${filename}">`;
                }
                updateGenerateButtonState();
            }
        });
    }

    if (generateBtn) {
        generateBtn.addEventListener('click', async () => {
            const currentUser = getCurrentUser();
            const authToken = getAuthToken();
            if (!selectedPerson || !selectedCloth || !authToken || !currentUser) {
                alert('Please log in, then select your photo and a cloth item.');
                return;
            }

            if (resultImageDisplay) resultImageDisplay.innerHTML = '<p>Generating...</p>';

            try {
                const response = await fetch('/tryon', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify({
                        user_id: currentUser.id,
                        // Ensure IDs are sent as integers
                        person_photo_id: parseInt(selectedPerson.id, 10),
                        cloth_photo_id: parseInt(selectedCloth.id, 10),
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Failed to generate try-on image.');
                }

                const result = await response.json();
                const resultSection = document.getElementById('result-section');
                if (resultSection) resultSection.classList.remove('hidden');
                if (resultImageDisplay) resultImageDisplay.innerHTML = `<img src="/images/results/${result.result_filename}" alt="Try-on result">`;

            } catch (error) {
                console.error("Error generating try-on:", error);
                if (resultImageDisplay) resultImageDisplay.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            }
        });
    }
}

function handleClothSelection(cloth) {
    selectedCloth = cloth;
    if (clothImageDisplay) {
        clothImageDisplay.innerHTML = `<img src="/images/clothes/${cloth.filename}" alt="${cloth.filename}">`;
    }
    updateGenerateButtonState();
}

export { setupTryOnPanel, handleClothSelection, loadPersonPhotos };
