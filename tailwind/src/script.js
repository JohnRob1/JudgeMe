const selectBtn = document.querySelector(".select-btn"),
        items = document.querySelectorAll(".item");
        console.log(selectBtn, items)
selectBtn.addEventListener("click", () => {
    selectBtn.classList.toggle("open");
});