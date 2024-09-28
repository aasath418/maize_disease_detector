document.addEventListener('DOMContentLoaded', function() {
    const reasonNav = document.getElementById('reason-nav');
    const organicNav = document.getElementById('organic-nav');
    const inorganicNav = document.getElementById('inorganic-nav');
    const reasonContainer = document.getElementById('reason-container');
    const organicContainer = document.getElementById('organic-container');
    const inorganicContainer = document.getElementById('inorganic-container');

    reasonNav.addEventListener('click', function() {
        showReason();
    });

    organicNav.addEventListener('click', function() {
        showOrganic();
    });

    inorganicNav.addEventListener('click', function() {
        showInorganic();
    });

    function showReason() {
        reasonContainer.classList.add('active', 'slide-in-right');
        organicContainer.classList.remove('active', 'slide-in-left');
        inorganicContainer.classList.remove('active', 'slide-in-left');
        reasonNav.classList.add('active');
        organicNav.classList.remove('active');
        inorganicNav.classList.remove('active');
    }

    function showOrganic() {
        organicContainer.classList.add('active', 'slide-in-right');
        inorganicContainer.classList.remove('active', 'slide-in-left');
        reasonContainer.classList.remove('active', 'slide-in-right');
        organicNav.classList.add('active');
        inorganicNav.classList.remove('active');
        reasonNav.classList.remove('active');
    }

    function showInorganic() {
        inorganicContainer.classList.add('active', 'slide-in-left');
        organicContainer.classList.remove('active', 'slide-in-right');
        reasonContainer.classList.remove('active', 'slide-in-right');
        inorganicNav.classList.add('active');
        organicNav.classList.remove('active');
        reasonNav.classList.remove('active');
    }

    // Swipe detection setup
    let touchstartX = 0;
    let touchendX = 0;

    document.addEventListener('touchstart', function(event) {
        touchstartX = event.changedTouches[0].screenX;
    });

    document.addEventListener('touchend', function(event) {
        touchendX = event.changedTouches[0].screenX;
        handleSwipe();
    });

    function handleSwipe() {
        if (touchendX < touchstartX - 50) { // Swipe left
            if (reasonContainer.classList.contains('active')) {
                showOrganic();
            } else if (organicContainer.classList.contains('active')) {
                showInorganic();
            }
        } else if (touchendX > touchstartX + 50) { // Swipe right
            if (inorganicContainer.classList.contains('active')) {
                showOrganic();
            } else if (organicContainer.classList.contains('active')) {
                showReason();
            }
        }
    }

    document.getElementById('generate-pdf').addEventListener('click', function() {
        fetch('/generate_pdf/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                disease: document.querySelector('h1').textContent.split(': ')[1],
                organic_solutions: Array.from(document.querySelectorAll('#organic-container .solution p')).map(p => p.textContent),
                inorganic_solutions: Array.from(document.querySelectorAll('#inorganic-container .solution p')).map(p => p.textContent),
                reason: document.querySelector('#reason-container p').textContent
            })
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'disease_solutions.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => console.error('Error:', error));
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});