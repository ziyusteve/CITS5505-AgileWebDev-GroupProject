/**
 * Scout Report Analysis Visualization
 * This script handles the display of scout report analysis data
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a page with scout report analysis
    const scoutReportContainer = document.getElementById('scout-report-analysis');
    if (!scoutReportContainer) return;

    const datasetId = scoutReportContainer.dataset.datasetId;
    if (!datasetId) return;

    // Dynamically load jsPDF library
    const jsPDFScript = document.createElement('script');
    jsPDFScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
    jsPDFScript.onload = function() {
        // Load html2canvas library for screenshots
        const html2canvasScript = document.createElement('script');
        html2canvasScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
        document.head.appendChild(html2canvasScript);
    };
    document.head.appendChild(jsPDFScript);

    // Fetch the scout report analysis data
    fetchScoutAnalysis(datasetId);
});

/**
 * Export PDF report
 */
function exportToPDF() {
    const reportContainer = document.querySelector('.court-bg');
    if (!reportContainer) return;

    // Show loading toast
    const loadingToast = document.createElement('div');
    loadingToast.className = 'export-toast';
    loadingToast.innerHTML = `<div class="toast-content"><i class="fas fa-spinner fa-spin me-2"></i>Generating PDF report, please wait...</div>`;
    document.body.appendChild(loadingToast);

    // Use html2canvas for screenshot
    html2canvas(reportContainer, {
        scale: 2, // Higher scale for better quality
        useCORS: true,
        logging: false,
        backgroundColor: '#111111',
        onclone: function(clonedDoc) {
            // Remove export button in the cloned document
            const exportBtn = clonedDoc.querySelector('.export-btn');
            if (exportBtn) exportBtn.style.display = 'none';
        }
    }).then(canvas => {
        const imgData = canvas.toDataURL('image/jpeg', 1.0);
        const pdf = new jspdf.jsPDF({
            orientation: 'portrait',
            unit: 'mm',
            format: 'a4'
        });

        const imgWidth = 210; // A4 width
        const pageHeight = 295;  // A4 height
        const imgHeight = canvas.height * imgWidth / canvas.width;
        let heightLeft = imgHeight;
        let position = 0;

        pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;

        // If content spans multiple pages, create new pages
        while (heightLeft > 0) {
            position = heightLeft - imgHeight;
            pdf.addPage();
            pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight);
            heightLeft -= pageHeight;
        }

        // Download PDF file
        const playerName = document.querySelector('.theme-accent-gold') ?
            document.querySelector('.theme-accent-gold').textContent : 'Scout_Report';
        const filename = `${playerName.replace(/\s+/g, '_')}_Scout_Report.pdf`;
        pdf.save(filename);

        // Remove loading toast
        document.body.removeChild(loadingToast);

        // Show success toast
        const successToast = document.createElement('div');
        successToast.className = 'export-toast success';
        successToast.innerHTML = `<div class="toast-content"><i class="fas fa-check-circle me-2"></i>PDF report successfully exported</div>`;
        document.body.appendChild(successToast);

        // Remove success toast after 3 seconds
        setTimeout(() => {
            document.body.removeChild(successToast);
        }, 3000);
    });
}

/**
 * Fetch scout report analysis data from the API
 */
function fetchScoutAnalysis(datasetId) {
    const endpoint = `/api/scout-analysis/${datasetId}`;

    fetch(endpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load scout report analysis');
            }
            return response.json();
        })
        .then(data => {
            console.log("API response data:", data); // Debug log
            renderScoutAnalysis(data);
        })
        .catch(error => {            console.error('Error loading scout analysis:', error);
            // Check if response is 401 - authentication error
            if (error.message.includes('401') || error.message.includes('Authentication')) {
                document.getElementById('scout-report-analysis').innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Authentication required. Please ensure you are logged in and try refreshing the page.
                    </div>
                `;
            } else {
                document.getElementById('scout-report-analysis').innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        Failed to load scout report analysis: ${error.message}
                    </div>
                `;
            }
        });
}

/**
 * Render the scout report analysis data
 */
function renderScoutAnalysis(data) {
    const container = document.getElementById('scout-report-analysis');

    // Check processing status
    if (data.processing_status === 'pending' || data.processing_status === 'processing') {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-spinner fa-spin"></i> The scout report is currently being analyzed. Please check back in a moment.
            </div>
        `;
        // Refresh after 5 seconds if still processing
        setTimeout(() => fetchScoutAnalysis(data.dataset_id), 5000);
        return;
    }

    if (data.processing_status === 'failed') {
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i> Failed to analyze the scout report. Please try uploading the file again.
            </div>
        `;
        return;
    }

    // Process player information - get directly from root object or use player_info
    const playerInfo = data.player_info || {};
    const playerName = playerInfo.name || data.player_name || "Dyson Daniels"; // Extract player name from text
    const playerPosition = playerInfo.position || data.position || "Guard";
    const playerTeam = playerInfo.team || data.team || "Atlanta Hawks";

    // Player card - NBA professional style
    const playerInfoHTML = `
        <div class="card mb-4 shadow-lg border-0">
            <div class="card-header bg-gradient-primary text-white border-0 py-3">
                <div class="d-flex align-items-center">
                    <div class="basketball-icon me-2"></div>
                    <h5 class="mb-0">Scout Report: ${playerName}</h5>
                </div>
            </div>
            <div class="card-body bg-dark text-white">
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-user-circle text-primary me-2" style="font-size: 2.5rem;"></i>
                            <div>
                                <h2 class="h4 mb-0 fw-bold theme-accent-gold">${playerName}</h2>
                                <p class="text-muted mb-0"><i class="fas fa-hashtag me-1"></i>Elite Defender</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <div class="row">
                            <div class="col-md-4 col-6 mb-3">
                                <div class="stat-box bg-dark border border-secondary rounded p-2 text-center">
                                    <div class="small text-muted">POSITION</div>
                                    <div class="fw-bold">${playerPosition}</div>
                                </div>
                            </div>
                            <div class="col-md-4 col-6 mb-3">
                                <div class="stat-box bg-dark border border-secondary rounded p-2 text-center">
                                    <div class="small text-muted">TEAM</div>
                                    <div class="fw-bold">${playerTeam}</div>
                                </div>
                            </div>
                            <div class="col-md-4 col-6 mb-3">
                                <div class="stat-box bg-dark border border-secondary rounded p-2 text-center">
                                    <div class="small text-muted">STATUS</div>
                                    <div class="fw-bold theme-accent-gold">Active</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Process rating data - collect all rating fields into ratings object
    const ratings = {};
    const possibleRatings = [
        'offensive_rating', 'defensive_rating', 'physical_rating',
        'technical_rating', 'potential_rating', 'overall_rating'
    ];

    // Collect all ratings from data
    possibleRatings.forEach(rating => {
        if (data[rating] !== undefined && data[rating] !== null) {
            ratings[rating] = data[rating];
        }
    });

    // If there's an old ratings object, merge it too
    if (data.ratings) {
        Object.assign(ratings, data.ratings);
    }

    const ratingKeys = Object.keys(ratings);

    // Rating level text
    function getRatingText(score) {
        if (score >= 90) return 'Superstar';
        if (score >= 85) return 'All-Star';
        if (score >= 80) return 'Starter';
        if (score >= 75) return 'Rotation';
        if (score >= 70) return 'Bench';
        return 'Development';
    }

    // Rating level color
    function getRatingColor(score) {
        if (score >= 90) return '#FDB927'; // Gold
        if (score >= 85) return '#1e88e5'; // Blue
        if (score >= 80) return '#43a047'; // Green
        if (score >= 75) return '#7cb342'; // Light Green
        if (score >= 70) return '#fb8c00'; // Orange
        return '#e53935'; // Red
    }

    let ratingsHTML = '';
    if (ratingKeys.length > 0) {
        // Calculate overall rating level
        const overallScore = ratings['overall_rating'] || 0;
        const overallCategory = getRatingText(overallScore);
        const overallColor = getRatingColor(overallScore);

        ratingsHTML = `
            <div class="card mb-4 shadow-lg border-0">
                <div class="card-header bg-gradient-dark text-white border-0 py-3">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-chart-radar me-2"></i>
                        <h5 class="mb-0">Performance Ratings</h5>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-7 mb-4">
                            <div class="radar-chart-container mb-2">
                                <canvas id="ratings-chart" width="100%" height="320"></canvas>
                            </div>
                            <div class="text-center">
                                <span class="badge bg-dark text-white px-3 py-2" style="border: 2px solid ${overallColor};">
                                    Overall Rating: <span class="fw-bold" style="color: ${overallColor};">${overallScore}</span>
                                    <span class="ms-2 small">(${overallCategory})</span>
                                </span>
                            </div>
                        </div>
                        <div class="col-md-5">
                            <h5 class="mb-3 border-bottom pb-2">Skill Breakdown</h5>
                            ${ratingKeys.map(key => {
                                if (key === 'overall_rating') return '';
                                const score = ratings[key];
                                const label = key.replace('_rating', '');
                                const color = getRatingColor(score);
                                const category = getRatingText(score);
                                return `
                                    <div class="mb-3">
                                        <div class="d-flex justify-content-between mb-1">
                                            <span class="text-capitalize">${label}</span>
                                            <span class="fw-bold" style="color: ${color};">${score} <small class="text-muted">${category}</small></span>
                                        </div>
                                        <div class="tech-progress">
                                            <div class="tech-progress-bar" style="width: ${score}%; background: ${color};"></div>
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Process analysis details - get from root object or full_analysis
    // First try root object
    let strengths = data.strengths || [];
    let weaknesses = data.weaknesses || [];
    let developmentAreas = data.development_areas || [];
    let summary = data.summary || "";

    // If root object doesn't have these, try full_analysis
    if ((!strengths.length && !weaknesses.length && !developmentAreas.length) && data.full_analysis) {
        const fullAnalysis = data.full_analysis;
        strengths = fullAnalysis.strengths || [];
        weaknesses = fullAnalysis.weaknesses || [];
        developmentAreas = fullAnalysis.development_areas || [];
        summary = fullAnalysis.summary || summary;
    }

    // Advanced analysis details section
    const analysisDetailsHTML = `
        <div class="card mb-4 shadow-lg border-0">
            <div class="card-header bg-gradient-purple text-white border-0 py-3">
                <div class="d-flex align-items-center">
                    <i class="fas fa-clipboard-list me-2"></i>
                    <h5 class="mb-0">Detailed Scouting Report</h5>
                </div>
            </div>
            <div class="card-body">
                ${summary ? `
                    <div class="mb-4">
                        <h5 class="section-title theme-accent-gold">Executive Summary</h5>
                        <p class="lead">${summary}</p>
                    </div>
                ` : ''}

                <div class="row g-4">
                    <div class="col-md-4">
                        <div class="card h-100 bg-dark text-white border-0">
                            <div class="card-header bg-success text-white py-2">
                                <h5 class="mb-0"><i class="fas fa-plus-circle me-2"></i>Strengths</h5>
                            </div>
                            <div class="card-body">
                                ${strengths.length > 0 ? `
                                    <ul class="list-group list-group-flush bg-transparent">
                                        ${strengths.map((strength, index) => `
                                            <li class="list-group-item bg-transparent text-white border-bottom border-secondary">
                                                <div class="d-flex">
                                                    <div class="skill-icon skill-icon-primary me-3">${index + 1}</div>
                                                    <div>${strength}</div>
                                                </div>
                                            </li>
                                        `).join('')}
                                    </ul>
                                ` : '<p class="text-muted">No strengths identified</p>'}
                            </div>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <div class="card h-100 bg-dark text-white border-0">
                            <div class="card-header bg-danger text-white py-2">
                                <h5 class="mb-0"><i class="fas fa-minus-circle me-2"></i>Weaknesses</h5>
                            </div>
                            <div class="card-body">
                                ${weaknesses.length > 0 ? `
                                    <ul class="list-group list-group-flush bg-transparent">
                                        ${weaknesses.map((weakness, index) => `
                                            <li class="list-group-item bg-transparent text-white border-bottom border-secondary">
                                                <div class="d-flex">
                                                    <div class="skill-icon skill-icon-danger me-3">${index + 1}</div>
                                                    <div>${weakness}</div>
                                                </div>
                                            </li>
                                        `).join('')}
                                    </ul>
                                ` : '<p class="text-muted">No weaknesses identified</p>'}
                            </div>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <div class="card h-100 bg-dark text-white border-0">
                            <div class="card-header bg-info text-white py-2">
                                <h5 class="mb-0"><i class="fas fa-arrow-circle-up me-2"></i>Development Areas</h5>
                            </div>
                            <div class="card-body">
                                ${developmentAreas.length > 0 ? `
                                    <ul class="list-group list-group-flush bg-transparent">
                                        ${developmentAreas.map((area, index) => `
                                            <li class="list-group-item bg-transparent text-white border-bottom border-secondary">
                                                <div class="d-flex">
                                                    <div class="skill-icon skill-icon-success me-3">${index + 1}</div>
                                                    <div>${area}</div>
                                                </div>
                                            </li>
                                        `).join('')}
                                    </ul>
                                ` : '<p class="text-muted">No development areas identified</p>'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Process analysis date
    let analysisDate = "Unknown";
    if (data.analysis_date) {
        try {
            // Try to parse date string or timestamp
            const date = new Date(data.analysis_date);
            if (!isNaN(date.getTime())) {
                analysisDate = date.toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
            }
        } catch (e) {
            console.error("Error parsing date:", e);
        }
    }

    // Add CSS styles
    const customStyles = `
        <style>
            .bg-gradient-primary {
                background: linear-gradient(135deg, #552583, #7D3AC1);
            }
            .bg-gradient-dark {
                background: linear-gradient(135deg, #111111, #333333);
            }
            .bg-gradient-purple {
                background: linear-gradient(135deg, #552583, #814ac3);
            }
            .text-primary {
                color: #552583 !important;
            }
            .skill-icon {
                width: 28px;
                height: 28px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                flex-shrink: 0;
            }
            .skill-icon-primary {
                background-color: #FDB927;
            }
            .skill-icon-danger {
                background-color: #e53935;
            }
            .skill-icon-success {
                background-color: #43a047;
            }
            .radar-chart-container {
                padding: 15px;
                border-radius: 5px;
                background-color: rgba(20, 20, 20, 0.8);
            }
            .section-title {
                position: relative;
                padding-bottom: 8px;
                margin-bottom: 16px;
                font-weight: 600;
                letter-spacing: -0.5px;
            }
            .section-title::after {
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                width: 60px;
                height: 3px;
                background: linear-gradient(90deg, #552583, #FDB927);
            }
            .tech-progress {
                height: 8px;
                border-radius: 4px;
                background-color: #2d2d2d;
                overflow: hidden;
            }
            .tech-progress-bar {
                height: 100%;
                border-radius: 4px;
            }
            .export-btn {
                position: fixed;
                bottom: 30px;
                right: 30px;
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: linear-gradient(135deg, #552583, #7D3AC1);
                color: white;
                border: none;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                cursor: pointer;
                z-index: 1000;
                transition: all 0.3s ease;
            }
            .export-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 15px rgba(0,0,0,0.4);
            }
            .export-btn i {
                font-size: 1.2rem;
            }
            .export-btn::after {
                content: 'Export PDF';
                position: absolute;
                bottom: -30px;
                left: 50%;
                transform: translateX(-50%);
                background-color: #333;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.7rem;
                opacity: 0;
                transition: opacity 0.2s ease;
                white-space: nowrap;
            }
            .export-btn:hover::after {
                opacity: 1;
            }
            .export-toast {
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(33, 33, 33, 0.9);
                color: white;
                border-left: 4px solid #552583;
                padding: 12px 20px;
                border-radius: 4px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                z-index: 2000;
                animation: fadeInRight 0.3s ease;
            }
            .export-toast.success {
                border-left: 4px solid #43a047;
            }
            @keyframes fadeInRight {
                from { opacity: 0; transform: translateX(50px); }
                to { opacity: 1; transform: translateX(0); }
            }
        </style>
    `;

    // Combine all sections
    container.innerHTML = customStyles + `
        <div class="court-bg p-2 p-md-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="theme-accent-gold mb-0"><i class="fas fa-basketball-ball me-2"></i>Professional Scout Report</h2>
                <span class="badge bg-dark text-white p-2">Report Date: ${analysisDate}</span>
            </div>

            ${playerInfoHTML}
            ${ratingsHTML}
            ${analysisDetailsHTML}

            <div class="text-center mt-4">
                <div class="small text-muted">
                    <i class="fas fa-shield-alt me-1"></i> Generated by NBA Analytics Platform
                </div>
            </div>
        </div>

        <!-- Export button -->
        <button class="export-btn" onclick="exportToPDF()">
            <i class="fas fa-file-pdf"></i>
        </button>
    `;

    // Initialize radar chart
    if (ratingKeys.length > 0) {
        const filteredRatingKeys = ratingKeys.filter(key => key !== 'overall_rating');
        if (filteredRatingKeys.length > 0) {
            const ctx = document.getElementById('ratings-chart').getContext('2d');

            // Create gradient colors
            const purpleGold = ctx.createLinearGradient(0, 0, 0, 400);
            purpleGold.addColorStop(0, 'rgba(85, 37, 131, 0.7)');    // Lakers Purple
            purpleGold.addColorStop(1, 'rgba(253, 185, 39, 0.7)');   // Lakers Gold

            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: filteredRatingKeys.map(key =>
                        key.replace('_rating', '')
                           .split('_')
                           .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                           .join(' ')
                    ),
                    datasets: [{
                        label: 'Player Ratings',
                        data: filteredRatingKeys.map(key => ratings[key]),
                        backgroundColor: purpleGold,
                        borderColor: '#FDB927',
                        borderWidth: 2,
                        pointBackgroundColor: '#552583',
                        pointBorderColor: '#FDB927',
                        pointHoverBackgroundColor: '#FDB927',
                        pointHoverBorderColor: '#552583',
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                stepSize: 20,
                                backdropColor: 'rgba(0, 0, 0, 0)'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            angleLines: {
                                color: 'rgba(255, 255, 255, 0.15)'
                            },
                            pointLabels: {
                                color: '#FDB927',
                                font: {
                                    weight: 'bold'
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
    }
}
