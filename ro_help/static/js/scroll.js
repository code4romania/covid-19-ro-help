document.addEventListener("DOMContentLoaded", function () {
    const scrollPos = localStorage.getItem('scrollPos');
    if (scrollPos) {
        window.scrollTo(0, parseFloat(scrollPos));
    }
});

window.onbeforeunload = function () {
    localStorage.setItem('scrollPos', window.scrollY.toString());
};