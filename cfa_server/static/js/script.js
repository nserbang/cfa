/**
 * Main script file for Arunachal Pradesh Crime Report
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize VenoBox
    initializeVenoBox();
    
    // Initialize description toggles
    initializeDescriptionToggles();

    // Initialize comment and history fetch/toggle
    initializeCommentButtons();
    initializeCaseHistoryButtons();

    // Initialize media fetch/toggle
    initializeMediaButtons();
});

/**
 * Initialize VenoBox lightbox
 */
function initializeVenoBox() {
    if (typeof VenoBox !== 'undefined') {
        new VenoBox({
            selector: '.image',
            numeration: true,
            infinigall: true,
            share: true,
            spinner: 'rotating-plane'
        });
    }
}

/**
 * Toggle between short and full description
 */
function initializeDescriptionToggles() {
    document.querySelectorAll('.toggle-description').forEach(function(button) {
        button.addEventListener('click', function() {
            // Find the parent <p> element
            const parent = button.closest('p');
            if (!parent) return;

            // Find the short and full description elements
            const shortDesc = parent.querySelector('.short-description');
            const fullDesc = parent.querySelector('.full-description');

            // Ensure both elements exist
            if (shortDesc && fullDesc) {
                // Toggle visibility
                if (shortDesc.classList.contains('d-none')) {
                    shortDesc.classList.remove('d-none');
                    fullDesc.classList.add('d-none');
                    button.textContent = 'More';
                } else {
                    shortDesc.classList.add('d-none');
                    fullDesc.classList.remove('d-none');
                    button.textContent = 'Less';
                }
            }
        });
    });
}

/**
 * Fetch and toggle comments for a case
 */
function initializeCommentButtons() {
    document.querySelectorAll('.comment-btn').forEach(function(button) {
        if (button.dataset.listenerAttached === "true") return;
        button.addEventListener('click', function () {
            const caseId = button.getAttribute('data-case-id');
            const commentContainer = document.getElementById('comment-' + caseId);
            const commentList = commentContainer.querySelector('.case-comment-list');
            const historyContainer = document.getElementById('history-' + caseId);

            // If already visible, hide and return
            if (!commentContainer.classList.contains('d-none')) {
                commentContainer.classList.add('d-none');
                return;
            }

            // Hide history if open
            if (historyContainer && !historyContainer.classList.contains('d-none')) {
                historyContainer.classList.add('d-none');
            }

            // Fetch comments from server
            fetch(`/get/case-comments/${caseId}/`)
                .then(response => response.json())
                .then(data => {
                    commentList.innerHTML = data.html;
                    commentContainer.classList.remove('d-none');
                })
                .catch(error => {
                    commentList.innerHTML = "<div class='text-danger'>Error loading comments.</div>";
                    commentContainer.classList.remove('d-none');
                });
        });
        button.dataset.listenerAttached = "true";
    });
}

/**
 * Fetch and toggle history for a case
 */
function initializeCaseHistoryButtons() {
    document.querySelectorAll('.history-btn').forEach(function(button) {
        if (button.dataset.listenerAttached === "true") return;
        button.addEventListener('click', function () {
            const caseId = button.getAttribute('data-case-id');
            const historyContainer = document.getElementById('history-' + caseId);
            const historyList = historyContainer.querySelector('.case-history-list');
            const commentContainer = document.getElementById('comment-' + caseId);

            // If already visible, hide and return
            if (!historyContainer.classList.contains('d-none')) {
                historyContainer.classList.add('d-none');
                return;
            }

            // Hide comment if open
            if (commentContainer && !commentContainer.classList.contains('d-none')) {
                commentContainer.classList.add('d-none');
            }

            // Fetch history from server
            fetch(`/get/case-history/${caseId}/`)
                .then(response => response.json())
                .then(data => {
                    historyList.innerHTML = data.html;
                    historyContainer.classList.remove('d-none');
                })
                .catch(error => {
                    historyList.innerHTML = "<div class='text-danger'>Error loading history.</div>";
                    historyContainer.classList.remove('d-none');
                });
        });
        button.dataset.listenerAttached = "true";
    });
}

/**
 * Initialize media fetch/toggle for a case
 */
function initializeMediaButtons() {
    document.querySelectorAll('.toggle-media').forEach(function(button) {
        button.addEventListener('click', async function() {
            const source = button.getAttribute('data-source') || 'case';
            const cid = button.getAttribute('data-cid');
            let mediaSectionId = '';
            if (source === 'case') {
                mediaSectionId = 'media-' + cid;
            } else {
                mediaSectionId = `media-${source}-${cid}`;
            }
            const mediaSection = document.getElementById(mediaSectionId);
            if (!mediaSection) return;

            const isHidden = mediaSection.classList.contains('d-none');
            mediaSection.classList.toggle('d-none');

            if (isHidden && mediaSection.getAttribute('data-loaded') !== 'true') {
                const spinner = mediaSection.querySelector('.media-spinner');
                const mediaList = mediaSection.querySelector('.case-media-list');
                const sourceVal = mediaSection.querySelector('.media-source').value;
                const cidVal = mediaSection.querySelector('.media-cid').value;

                if (spinner) spinner.classList.remove('d-none');
                if (mediaList) mediaList.innerHTML = '';

                try {
                    const params = new URLSearchParams({ source: sourceVal, cid: cidVal });
                    const response = await fetch(`/get/media/?${params.toString()}`);
                    const data = await response.json();
                    if (mediaList) mediaList.innerHTML = data.html;
                    mediaSection.setAttribute('data-loaded', 'true');
                } catch (e) {
                    if (mediaList) mediaList.innerHTML = "<div class='text-danger'>Failed to load media.</div>";
                } finally {
                    if (spinner) spinner.classList.add('d-none');
                }
            }
        });
    });
}

/**
 * Initialize dashboard charts with provided data
 * @param {Object} caseData - The data for all charts
 */
function initializeDashboardCharts(caseData) {
    if (!caseData) return;
    console.log('Initializing dashboard charts with data:', caseData);

    // Define state color mapping to ensure consistency across all charts
    const stateColorMap = {
        'Pending': '#FF9800',
        'Accepted': '#4CAF50',
        'Found': '#2196F3',
        'Assign': '#9C27B0',
        'Visited': '#FF5722',
        'Inprogress': '#03A9F4',
        'Transfer': '#795548',
        'Resolved': '#8BC34A',
        'Info': '#607D8B',
        'Rejected': '#F44336'
    };
    
    // For case types in overall chart
    const caseTypeColors = {
        'Drug': '#2196F3',
        'Vehicle': '#4CAF50',
        'Extortion': '#FFC107'
    };

    // Common chart options
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    padding: 20,
                    boxWidth: 12
                }
            },
            tooltip: {
                callbacks: {
                    // Display consistent color squares in tooltips
                    labelColor: function(context) {
                        const label = context.label;
                        // If it's a case type chart, use case type color
                        if (caseTypeColors[label]) {
                            return {
                                backgroundColor: caseTypeColors[label],
                                borderColor: caseTypeColors[label]
                            };
                        }
                        // Otherwise assume it's a state and use state color
                        return {
                            backgroundColor: stateColorMap[label] || '#999999',
                            borderColor: stateColorMap[label] || '#999999'
                        };
                    }
                }
            }
        }
    };
    
    // Helper function to map case states to consistent colors
    function getStateColors(states) {
        return states.map(state => stateColorMap[state] || '#999999');
    }

    // Create the overall cases pie chart
    if (document.getElementById('casePieChart')) {
        new Chart(document.getElementById('casePieChart').getContext('2d'), {
            type: 'pie',
            data: {
                labels: caseData.overall.labels,
                datasets: [{
                    data: caseData.overall.data,
                    backgroundColor: caseData.overall.labels.map(label => caseTypeColors[label] || '#999999'),
                }]
            },
            options: chartOptions
        });
    }
    
    // Create case status distribution charts with consistent colors
    if (document.getElementById('drugCaseChart')) {
        new Chart(document.getElementById('drugCaseChart').getContext('2d'), {
            type: 'pie',
            data: {
                labels: caseData.drug.labels,
                datasets: [{
                    data: caseData.drug.data,
                    backgroundColor: getStateColors(caseData.drug.labels),
                }]
            },
            options: chartOptions
        });
    }
    
    if (document.getElementById('extortionCaseChart')) {
        new Chart(document.getElementById('extortionCaseChart').getContext('2d'), {
            type: 'pie',
            data: {
                labels: caseData.extortion.labels,
                datasets: [{
                    data: caseData.extortion.data,
                    backgroundColor: getStateColors(caseData.extortion.labels),
                }]
            },
            options: chartOptions
        });
    }
    
    if (document.getElementById('vehicleCaseChart')) {
        new Chart(document.getElementById('vehicleCaseChart').getContext('2d'), {
            type: 'pie',
            data: {
                labels: caseData.vehicle.labels,
                datasets: [{
                    data: caseData.vehicle.data,
                    backgroundColor: getStateColors(caseData.vehicle.labels),
                }]
            },
            options: chartOptions
        });
    }
    
    // Create the time chart
    let timeChart = null;
    const timeChartElement = document.getElementById('timeChart');
    
    if (timeChartElement) {
        const timeChartCtx = timeChartElement.getContext('2d');
        timeChart = new Chart(timeChartCtx, {
            type: 'line',
            data: {
                labels: caseData.timeData.daily.labels,
                datasets: [{
                    label: 'Cases',
                    data: caseData.timeData.daily.data,
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33, 150, 243, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Number of Cases'
                        },
                        beginAtZero: true
                    }
                }
            }
        });
        
        // Update time chart on dropdown change
        const timeRangeSelector = document.getElementById('timeRange');
        if (timeRangeSelector) {
            timeRangeSelector.addEventListener('change', function() {
                const timeRange = this.value;
                timeChart.data.labels = caseData.timeData[timeRange].labels;
                timeChart.data.datasets[0].data = caseData.timeData[timeRange].data;
                timeChart.update();
            });
        }
    }
}

/**
 * Add any custom JavaScript for the application here
 */