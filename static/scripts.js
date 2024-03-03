// scripts.js

function activateSelectedButton() {
    let links = document.querySelectorAll('nav ul li a');
    let currentPath = window.location.pathname;
    for (let link of links) {
        if (currentPath === link.pathname || (link.pathname === '/home' && currentPath === '/')) {
            link.classList.add('active');
        }
    }
}

function removeDiv(id) {
    var element = document.getElementById(id);
    if (element) {
        element.parentNode.removeChild(element);
    }
}

function inputSize(input) {
    var textLength = input.value.length;
    var width = textLength * 8 > 300 ? textLength * 8 : 300;
    input.style.width = width + 'px';
}

function onFileSelected() {
    const fileInput = document.getElementById('file');
    const fileNameSpan = document.getElementById('file-name');
    if (fileInput.files.length > 0) {
        fileNameSpan.textContent = fileInput.files[0].name;
    } else {
        fileNameSpan.textContent = 'Not selected';
    }
}
