// Main JavaScript for Data Analytics Platform

document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Auto-close alerts after 4 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 4000);
    
    // Add animation to cards
    const animateCards = () => {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            if (isElementInViewport(card) && !card.classList.contains('animated')) {
                card.classList.add('fade-in', 'animated');
            }
        });
    };
    
    // Helper function to check if element is in viewport
    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
    
    // Run animation on load
    animateCards();
    
    // Run animation on scroll
    window.addEventListener('scroll', animateCards);
    
    // File input enhancement
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const fileName = this.files[0]?.name;
            if (fileName) {
                const fileLabel = this.nextElementSibling;
                if (fileLabel && fileLabel.classList.contains('form-label')) {
                    const uploadIcon = '<i class="fas fa-check-circle me-2 text-success"></i>';
                    fileLabel.innerHTML = `${uploadIcon} ${fileName}`;
                }
            }
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// Function for data sharing UI enhancements
function setupDataSharingUI() {
    const datasetSelect = document.getElementById('dataset_id');
    const userSelect = document.getElementById('user_id');
    
    if (datasetSelect && userSelect) {
        // Add search functionality to selects with many options
        if (userSelect.options.length > 10) {
            // Here you could initialize a select2 or similar library
            console.log('Many users available for sharing');
        }
        
        // Preview selected dataset information
        datasetSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const datasetId = selectedOption.value;
            console.log(`Dataset ${datasetId} selected`);
            // In a real app, you would fetch dataset details via AJAX here
        });
    }
}

// Function for data visualization enhancements
function setupDataVisualizationUI() {
    const visualizationContainer = document.getElementById('visualization');
    
    if (visualizationContainer) {
        console.log('Visualization container found in the DOM');
        // Additional visualization-specific setup would go here
    }
}

// Execute page-specific code based on current URL
function executePageSpecificCode() {
    const path = window.location.pathname;
    
    if (path.includes('/share')) {
        setupDataSharingUI();
    } else if (path.includes('/visualize')) {
        setupDataVisualizationUI();
    }
}

// Run page-specific code after DOM is ready
document.addEventListener('DOMContentLoaded', executePageSpecificCode);

// Enhanced Basketball Analytics Interactions
document.addEventListener('DOMContentLoaded', function() {
    // Initialize counters with animation
    const counterElements = document.querySelectorAll('.counter-wrapper');
    counterElements.forEach((element, index) => {
        element.style.setProperty('--animation-order', index);
    });
    
    // Add animation to analysis cards
    const analysisCards = document.querySelectorAll('.analysis-card');
    analysisCards.forEach((card) => {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        observer.observe(card);
    });
    
    // Initialize skill bars with animation
    const skillBars = document.querySelectorAll('.skill-bar');
    skillBars.forEach((bar) => {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const width = bar.style.width;
                    bar.style.width = '0%';
                    setTimeout(() => {
                        bar.style.width = width;
                    }, 100);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        observer.observe(bar);
    });
});