let collapsibles = document.getElementsByClassName('collapsible');

for (let collapsible of collapsibles) {
    collapsible.addEventListener("click", function() {
        this.classList.toggle("active");
    });
}