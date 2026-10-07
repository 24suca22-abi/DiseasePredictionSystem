/**
 * Care Nova | Intelligent AI Clinical Health Assistant
 * Interactive Client-Side JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
    // -------------------------------------------------------------
    // 1. Symptom Selection & Live Counter
    // -------------------------------------------------------------
    const symptomCards = document.querySelectorAll('.symptom-card');
    const selectedCountEl = document.getElementById('selected-count');
    const symptomForm = document.getElementById('symptom-form');
    const searchInput = document.getElementById('symptom-search');

    function updateSelectedCount() {
        const checkedBoxes = document.querySelectorAll('.symptom-checkbox:checked');
        if (selectedCountEl) {
            selectedCountEl.textContent = checkedBoxes.length;
        }

        // Highlight selected cards
        symptomCards.forEach(card => {
            const checkbox = card.querySelector('.symptom-checkbox');
            if (checkbox && checkbox.checked) {
                card.classList.add('selected');
            } else if (checkbox) {
                card.classList.remove('selected');
            }
        });
    }

    // Toggle on card click
    symptomCards.forEach(card => {
        card.addEventListener('click', function (e) {
            // Avoid double toggle if direct click was on checkbox
            if (e.target.tagName.toLowerCase() !== 'input') {
                const checkbox = card.querySelector('.symptom-checkbox');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    updateSelectedCount();
                }
            }
        });

        const checkbox = card.querySelector('.symptom-checkbox');
        if (checkbox) {
            checkbox.addEventListener('change', updateSelectedCount);
        }
    });

    // Initial counter check
    updateSelectedCount();

    // -------------------------------------------------------------
    // 2. Real-time Symptom Search / Filter
    // -------------------------------------------------------------
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const query = this.value.trim().toLowerCase();

            symptomCards.forEach(card => {
                const text = card.textContent.trim().toLowerCase();
                if (text.includes(query)) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });

            // Hide empty category sections
            const categorySections = document.querySelectorAll('.symptom-category-section');
            categorySections.forEach(section => {
                const visibleCards = section.querySelectorAll('.symptom-card:not([style*="display: none"])');
                if (visibleCards.length === 0) {
                    section.style.display = 'none';
                } else {
                    section.style.display = 'block';
                }
            });
        });
    }

    // -------------------------------------------------------------
    // 3. Select / Clear All Helpers
    // -------------------------------------------------------------
    const clearAllBtn = document.getElementById('clear-all-btn');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelectorAll('.symptom-checkbox').forEach(cb => {
                cb.checked = false;
            });
            updateSelectedCount();
        });
    }

    // Form Submission Validation
    if (symptomForm) {
        symptomForm.addEventListener('submit', function (e) {
            const checkedBoxes = document.querySelectorAll('.symptom-checkbox:checked');
            if (checkedBoxes.length === 0) {
                e.preventDefault();
                alert('Please select at least one symptom before running the Care Nova prediction.');
            }
        });
    }

    // -------------------------------------------------------------
    // 4. Alert Auto-dismiss or Close Button
    // -------------------------------------------------------------
    const alertCloseButtons = document.querySelectorAll('.alert-close');
    alertCloseButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 200);
            }
        });
    });

    // -------------------------------------------------------------
    // 5. Smooth Scroll for In-Page Anchor Links (Header & Footer)
    // -------------------------------------------------------------
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            const targetEl = document.querySelector(targetId);
            if (targetEl) {
                e.preventDefault();
                const navHeight = document.querySelector('.navbar') ? document.querySelector('.navbar').offsetHeight : 70;
                const elementPosition = targetEl.getBoundingClientRect().top + window.pageYOffset;
                const offsetPosition = elementPosition - navHeight - 16;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
});

/**
 * Global Helper for Geolocation Specialist Lookup
 */
function detectLocationAndFind(specialistTitle) {
    const statusMsg = document.getElementById('geo-status');
    const specialist = specialistTitle || 'General Physician';

    if (!navigator.geolocation) {
        if (statusMsg) {
            statusMsg.textContent = 'Geolocation is not supported by your browser. Please type your location manually.';
            statusMsg.style.display = 'block';
        } else {
            alert('Geolocation is not supported by your browser.');
        }
        return;
    }

    if (statusMsg) {
        statusMsg.textContent = 'Detecting current location...';
        statusMsg.style.display = 'block';
    }

    navigator.geolocation.getCurrentPosition(
        function (position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            if (statusMsg) {
                statusMsg.textContent = 'Location detected! Opening Google Maps...';
            }
            const mapUrl = `https://www.google.com/maps/search/${encodeURIComponent(specialist)}/@${lat},${lng},14z`;
            window.open(mapUrl, '_blank');
        },
        function (error) {
            let msg = 'Could not retrieve your location. Please enter your city/locality manually.';
            if (error.code === error.PERMISSION_DENIED) {
                msg = 'Location permission was denied. Please enter your city manually.';
            }
            if (statusMsg) {
                statusMsg.textContent = msg;
            } else {
                alert(msg);
            }
        },
        { timeout: 10000, enableHighAccuracy: true }
    );
}
