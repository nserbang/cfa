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


const successCallback = (position) => {
    latitude = position.coords.latitude
    longitude = position.coords.longitude
    console.log(latitude, longitude)
    lat = latitude.toFixed(4)
    long = longitude.toFixed(4)
    addGeoLoactionInURL(lat, long)
};

const errorCallback = (error) => {
    console.log(error);
};

navigator.geolocation.getCurrentPosition(successCallback, errorCallback);

function addGeoLoactionInURL(lat, long) {
    let url = new URL(window.location.href);
    let lattitude = url.searchParams.get('lat')
    let longitude = url.searchParams.get('long')
    if (!lattitude && !longitude) {
        url.searchParams.set('lat', lat)
        url.searchParams.set('long', long)
        location.assign(url)
    }
}
