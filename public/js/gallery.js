// --- DOM Elements ---
const itemGallery = document.getElementById('item-gallery');
const sentinel = document.getElementById('sentinel');

// --- State ---
let allClothes = [];

// --- Functions ---
function appendClothes() {
    if (!allClothes || allClothes.length === 0) return;
    allClothes.forEach(cloth => {
        const card = document.createElement('div');
        card.className = 'item-card';
        card.innerHTML = `
            <div class="item-card-image-wrapper">
                <img src="/images/clothes/${cloth.filename}" alt="Cloth item" class="item-card-image item-clickable" data-id="${cloth.id}" data-filename="${cloth.filename}">
            </div>
            <div class="item-card-content">
                <h5>Stylish Cloth #${cloth.id}</h5>
            </div>
        `;
        if (itemGallery && sentinel) {
            itemGallery.insertBefore(card, sentinel);
        }
    });
}

function initialContentCheck() {
    let safeguard = 0;
    const maxAppends = 10;

    const checkAndAppend = () => {
        if (safeguard >= maxAppends || !sentinel) {
            if (safeguard >= maxAppends) console.warn("Initial content check reached safeguard limit.");
            return;
        }

        const sentinelRect = sentinel.getBoundingClientRect();
        if (sentinelRect.top < window.innerHeight && sentinelRect.bottom > 0) {
            appendClothes();
            safeguard++;
            setTimeout(checkAndAppend, 100);
        }
    };
    checkAndAppend();
}

async function loadInitialClothes() {
    if (!itemGallery) return;
    try {
        const response = await fetch('/images/shop-clothes');
        if (!response.ok) throw new Error('Failed to load clothes.');
        allClothes = await response.json();

        if (!allClothes || allClothes.length === 0) {
            itemGallery.innerHTML = '<p>No items to display.</p>';
            return;
        }
        appendClothes();
        setTimeout(initialContentCheck, 100);
    } catch (error) {
        console.error("Error loading clothes:", error);
        itemGallery.innerHTML = '<p>Failed to load items.</p>';
    }
}

function setupInfiniteScroll() {
    if (!sentinel) return;
    const observer = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting) {
            appendClothes();
        }
    });
    observer.observe(sentinel);
}

function setupGallery(onClothSelect) {
    if (itemGallery) {
        itemGallery.addEventListener('click', (e) => {
            if (e.target && e.target.classList.contains('item-clickable')) {
                const id = e.target.dataset.id;
                const filename = e.target.dataset.filename;
                if (onClothSelect) {
                    onClothSelect({ id, filename });
                }
            }
        });
    }
    loadInitialClothes();
    setupInfiniteScroll();
}

export { setupGallery };
