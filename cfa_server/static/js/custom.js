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
