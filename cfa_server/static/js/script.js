/**
 * Main script file for Arunachal Pradesh Crime Report
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize VenoBox
    initializeVenoBox();
    
    // Initialize description toggles
    initializeDescriptionToggles();
    
    // Initialize comment buttons
    initializeCommentButtons();
    
    // Initialize case history buttons
    initializeCaseHistoryButtons();
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
 * Toggle comment section visibility
 */
function initializeCommentButtons() {
    document.querySelectorAll('[data-bs-target^="#comment-"]').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('data-bs-target');
            const commentSection = document.querySelector(targetId);
            if (commentSection) {
                commentSection.classList.toggle('d-none');
            }
        });
    });
}

/**
 * Toggle case history section visibility
 */
function initializeCaseHistoryButtons() {
    document.querySelectorAll('[data-bs-target^="#history-"]').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('data-bs-target');
            const historySection = document.querySelector(targetId);
            if (historySection) {
                historySection.classList.toggle('d-none');
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

document.addEventListener('DOMContentLoaded', function () {
    // Attach event listeners to all "Case History" buttons
    const caseHistoryButtons = document.querySelectorAll('.case-history-btn');
    caseHistoryButtons.forEach(button => {
        button.addEventListener('click', function () {
            const caseId = button.getAttribute('data-case-id');
            getCaseHistory(caseId);
        });
    });
});

function getCaseHistory(caseId) {
    const historyContainer = document.getElementById('history-' + caseId);

    // Fetch the case history from the server
    fetch(`/get/case-history/${caseId}/`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(response => {
        // Update the history container with the fetched HTML
        historyContainer.innerHTML = response['html'];
        historyContainer.classList.remove('d-none');
    })
    .catch(error => {
        console.error('Error fetching case history:', error);
    });
}

document.addEventListener('DOMContentLoaded', function () {
    // Attach event listeners to all "History" buttons
    const historyButtons = document.querySelectorAll('.history-btn');
    historyButtons.forEach(button => {
        button.addEventListener('click', function () {
            const caseId = button.getAttribute('data-case-id');
            const historyContainer = document.getElementById('history-' + caseId);

            // Toggle visibility
            if (!historyContainer.classList.contains('d-none')) {
                historyContainer.classList.add('d-none');
                return;
            }

            // Fetch case history via AJAX
            fetch(`/get/case-history/${caseId}/`)
                .then(response => response.json())
                .then(data => {
                    const historyList = historyContainer.querySelector('.case-history-list');
                    historyList.innerHTML = data.html; // Populate the history list
                    historyContainer.classList.remove('d-none'); // Show the container
                })
                .catch(error => {
                    console.error('Error fetching case history:', error);
                });
        });
    });
});
/**
 * Add any custom JavaScript for the application here
 */