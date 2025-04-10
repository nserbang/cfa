const comments = document.querySelectorAll("[class*=comment-]")

comments.forEach(comment => {
    comment.addEventListener('click', function updateComment(event) {
        let caseID = event.target.getAttribute('data-bs-target').split("-")[1]
        showHideCommentAndHistory(caseID)
    });
  });


let caseHistories = document.querySelectorAll("[class*=case-history-]")

caseHistories.forEach(history => {
    history.addEventListener('click', function updateHistory(event) {
        event.preventDefault()
        let caseID = event.target.getAttribute('data-bs-target').split("-")[1]
        getCaseHistory(caseID)
    });
  });


function showHideCommentAndHistory(id) {
    let comment = document.getElementById("comment-" + id)
    let history = document.getElementById("history-" + id)
    if (comment.classList.contains('d-none')) {
        comment.classList.remove('d-none')
        // history.classList.remove('d-flex')
    } else if (!comment.classList.contains('d-none')){
        comment.classList.add('d-none')
    }
    if (!history.classList.contains('d-none')) {
        history.classList.add('d-none')
    }
}


function changeStatus() {
    fetch('/change-status/', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(response => location.reload())
}


function getCaseHistory(caseId) {
    let comment = document.getElementById("comment-" + caseId)
    let history = document.getElementById("history-" + caseId)
    if (history.classList.contains('d-none')) {
        history.classList.remove('d-none')
    } else if (!history.classList.contains('d-none')){
        history.classList.add('d-none')
    }
    if (!comment.classList.contains('d-none')) {
        comment.classList.add('d-none')
    }
    historyContainer = document.getElementById('history-' + caseId);
    fetch(`/get/case-history/${caseId}/`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(response => {
        historyContainer.innerHTML = response['html']
    })
}

function openVenobox(e){
    this.event.preventDefault();
    vobx = new VenoBox({
        selector: '.image',
        numeration: true,
        infinigall: true,
        share: true,
        spinner: 'rotating-plane'
    });
    vobx.open()
}

function openMap(destLat, destLong, placeName) {
    // Retrieve user latitude and longitude from hidden input fields
    const userLat = document.getElementById('user_lat').value;
    const userLong = document.getElementById('user_long').value;

    // Check if user location is available
    if (!userLat || !userLong) {
        alert("Please allow location access to use this feature.");
        return;
    }

    // Construct the Google Maps URL
    const url = `https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLong}&destination=${destLat},${destLong}&travelmode=driving`;

    // Open the URL in a new tab
    window.open(url, '_blank');
}