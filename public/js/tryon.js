// --- DOM Elements ---
const personImageDisplay = document.getElementById('person-image-display');
const personPhotoSelector = document.getElementById('person-photo-selector');
const clothImageDisplay = document.getElementById('cloth-image-display');
const clothPhotoSelector = document.getElementById('cloth-photo-selector'); // New DOM element
const resultImageDisplay = document.getElementById('result-image-display');
const generateBtn = document.getElementById('generateBtn');
const viewToggle = document.getElementById('view-toggle');
const tryOnContainer = document.getElementById('try-on-container');
const resultsContainer = document.getElementById('results-container');


// --- State ---
let selectedPerson = null;
let selectedCloth = null;
let sessionResults = []; // Store session result filenames

// --- Functions ---
function updateGenerateButtonState() {
    if (generateBtn) {
        generateBtn.disabled = !(selectedPerson && selectedCloth);
    }
}

function displaySessionResults() {
    resultsContainer.innerHTML = ''; // Clear previous results
    if (sessionResults.length === 0) {
        resultsContainer.innerHTML = '<p class="no-results">No results generated in this session yet.</p>';
        return;
    }

    sessionResults.forEach(filename => {
        const img = document.createElement('img');
        img.src = `/images/results/${filename}`;
        img.alt = `Result image ${filename}`;
        resultsContainer.appendChild(img);
    });
}

async function loadPersonPhotos(authToken) {
    if (!authToken) {
        if (personPhotoSelector) personPhotoSelector.innerHTML = '<small>Please log in to use.</small>';
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
        selectedPerson = null; // Reset selection

        if (photos.length > 0) {
            const firstPhoto = photos[0];
            selectedPerson = { id: firstPhoto.id, filename: firstPhoto.filename };
            personImageDisplay.innerHTML = `<img src="/images/persons/${firstPhoto.filename}" alt="${firstPhoto.filename}">`;
            
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
        } else {
            // If no photos, ensure the main display is clear or shows a generic placeholder
            personImageDisplay.innerHTML = `
                <div class="person-image-placeholder">
                    <p>Upload a person image</p>
                </div>
            `;
        }

        // Always add the upload button to the selector
        const uploadContainer = document.createElement('div');
        uploadContainer.className = 'thumbnail-upload';
        uploadContainer.innerHTML = `
            <label for="person-photo-upload-selector" class="upload-label">+</label>
            <input type="file" id="person-photo-upload-selector" accept="image/*" style="display: none;">
        `;
        personPhotoSelector.appendChild(uploadContainer);

        const fileInputSelector = document.getElementById('person-photo-upload-selector');
        if (fileInputSelector) {
            fileInputSelector.addEventListener('change', (event) => handlePersonPhotoUpload(event, authToken));
        }
        updateGenerateButtonState();
    } catch (error) {
        console.error("Error loading person photos:", error);
        personPhotoSelector.innerHTML = '<small>Failed to load photos.</small>';
    }
}

async function loadClothPhotos(authToken) {
    if (!authToken) {
        if (clothPhotoSelector) clothPhotoSelector.innerHTML = '<small>Please log in to use.</small>';
        return;
    }
    if (!clothPhotoSelector || !clothImageDisplay) return;

    try {
        const response = await fetch('/images/my-clothes', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (!response.ok) throw new Error('Failed to load cloth photos.');
        const photos = await response.json();

        clothPhotoSelector.innerHTML = '';
        clothImageDisplay.innerHTML = '';
        selectedCloth = null; // Reset selection

        if (photos.length > 0) {
            const firstPhoto = photos[0];
            selectedCloth = { id: firstPhoto.id, filename: firstPhoto.filename };
            clothImageDisplay.innerHTML = `<img src="/images/clothes/${firstPhoto.filename}" alt="${firstPhoto.filename}">`;
            
            photos.forEach((photo, index) => {
                const img = document.createElement('img');
                img.src = `/images/clothes/${photo.filename}`;
                img.alt = photo.filename;
                img.className = 'thumbnail';
                img.dataset.id = photo.id;
                img.dataset.filename = photo.filename;

                if (index === 0) {
                    img.classList.add('selected');
                }
                clothPhotoSelector.appendChild(img);
            });
        } else {
            // If no photos, ensure the main display is clear or shows a generic placeholder
            clothImageDisplay.innerHTML = `
                <div class="cloth-image-placeholder">
                    <p>Upload a cloth image</p>
                </div>
            `;
        }

        // Always add the upload button to the selector
        const uploadContainer = document.createElement('div');
        uploadContainer.className = 'thumbnail-upload';
        uploadContainer.innerHTML = `
            <label for="cloth-photo-upload-selector" class="upload-label">+</label>
            <input type="file" id="cloth-photo-upload-selector" accept="image/*" style="display: none;">
        `;
        clothPhotoSelector.appendChild(uploadContainer);

        const fileInputSelector = document.getElementById('cloth-photo-upload-selector');
        if (fileInputSelector) {
            fileInputSelector.addEventListener('change', (event) => handleClothPhotoUpload(event, authToken));
        }
        updateGenerateButtonState();
    } catch (error) {
        console.error("Error loading cloth photos:", error);
        clothPhotoSelector.innerHTML = '<small>Failed to load clothes.</small>';
    }
}

async function handlePersonPhotoUpload(event, authToken) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload/person', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'File upload failed.');
        }

        // Reload photos to show the newly uploaded one
        await loadPersonPhotos(authToken);

    } catch (error) {
        console.error('Upload error:', error);
        alert(`Error uploading file: ${error.message}`);
    }
}

async function handleClothPhotoUpload(event, authToken) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload/cloth', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'File upload failed.');
        }

        // Reload photos to show the newly uploaded one
        await loadClothPhotos(authToken);

    } catch (error) {
        console.error('Upload error:', error);
        alert(`Error uploading file: ${error.message}`);
    }
}

function setupTryOnPanel(getAuthToken, getCurrentUser) {
    // This function is called after authentication is handled.
    const authToken = getAuthToken();
    if (authToken) {
        loadPersonPhotos(authToken);
        loadClothPhotos(authToken); // Load user's clothes
    }

    if (personPhotoSelector) {
        personPhotoSelector.addEventListener('click', (e) => {
            if (e.target && e.target.classList.contains('thumbnail')) {
                document.querySelectorAll('#person-photo-selector .thumbnail').forEach(thumb => {
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

    if (clothPhotoSelector) { // New event listener for cloth selector
        clothPhotoSelector.addEventListener('click', (e) => {
            if (e.target && e.target.classList.contains('thumbnail')) {
                document.querySelectorAll('#cloth-photo-selector .thumbnail').forEach(thumb => {
                    thumb.classList.remove('selected');
                });
                e.target.classList.add('selected');

                const id = e.target.dataset.id;
                const filename = e.target.dataset.filename;
                selectedCloth = { id, filename };
                if (clothImageDisplay) {
                    clothImageDisplay.innerHTML = `<img src="/images/clothes/${filename}" alt="${filename}">`;
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
            const resultSection = document.getElementById('result-section');
            if (resultSection) resultSection.classList.remove('hidden');


            try {
                const response = await fetch('/tryon', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify({
                        user_id: currentUser.id,
                        person_photo_id: parseInt(selectedPerson.id, 10),
                        cloth_photo_id: parseInt(selectedCloth.id, 10),
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Failed to generate try-on image.');
                }

                const result = await response.json();
                if (resultImageDisplay) resultImageDisplay.innerHTML = `<img src="/images/results/${result.result_filename}" alt="Try-on result">`;
                
                // Add to session results
                sessionResults.push(result.result_filename);

            } catch (error) {
                console.error("Error generating try-on:", error);
                if (resultImageDisplay) resultImageDisplay.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            }
        });
    }

    if (viewToggle) {
        viewToggle.addEventListener('change', () => {
            if (viewToggle.checked) {
                // Show Results
                tryOnContainer.classList.add('hidden');
                resultsContainer.classList.remove('hidden');
                displaySessionResults();
            } else {
                // Show Try-on
                tryOnContainer.classList.remove('hidden');
                resultsContainer.classList.add('hidden');
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
