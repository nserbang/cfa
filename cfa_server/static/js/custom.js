function showCommentArea(id) {
    let comment = document.getElementById("comment-" + id)
    if (comment.classList.contains('d-none')) {
        comment.classList.remove('d-none')
    } else {
        comment.classList.add('d-none')
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


function getCaseHistory(event, caseId) {
    event.preventDefault();
    historyContainer = document.getElementById('history-' + caseId);
    fetch(`/get/case-history/${caseId}/`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(response => historyContainer.innerHTML = response['html'])
}