function showHideCommentAndHistory(id) {
    console.log('skdfjsdklfjklsdf', id)
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


function getCaseHistory(event, caseId) {
    event.preventDefault();
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
    .then(response => historyContainer.innerHTML = response['html'])
}

