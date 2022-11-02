const cursor = document.querySelector(".cursor");
const cursorBlob = document.querySelector(".cursor-blob");

var mouseY = 150;
var mouseX = 150;

var smoothX = 150;
var smoothY = 150;

var scaleX = 1;
var scaleY = 1;

var hoverScale = 1;

setInterval(moveBlob, 1000 / 60);

function moveBlob() {
    var xPrev = smoothX;
    var yPrev = smoothY;
    smoothX = lerp(smoothX, mouseX, 0.1);
    smoothY = lerp(smoothY, mouseY, 0.1);

    var deltaX = smoothX - mouseX;
    var deltaY = smoothY - mouseY;

    var delta = Math.abs(deltaX) + Math.abs(deltaY);
    var scale = delta / 800;

    var rotation = Math.atan(deltaY / deltaX);

    console.log(rotation);

    scaleX = (1 + scale) * hoverScale * 2;
    scaleY = (1 - scale / 2) * hoverScale * 2;

    cursorBlob.style.transform = `
        rotate(${rotation}rad)
        scale(${scaleX}, ${scaleY})
        `;

    scaleX = lerp(scaleX, Math.abs(deltaX) / 500 + 1, 0.1);
    scaleY = lerp(scaleY, Math.abs(deltaY / 500) + 1, 0.1);

    scaleX = Math.min(scaleX, 3);
    scaleY = Math.min(scaleY, 3);

    // console.log(delta);

    cursorBlob.style.left = smoothX + "px";
    cursorBlob.style.top = smoothY + "px";

    return;

    cursorBlob.style.transform = `
    scale(${scaleX * hoverScale}, ${scaleY * hoverScale})`;
}

const moveCursor = (e) => {
    mouseX = e.pageX;
    mouseY = e.pageY;

    cursor.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0)`;
};

function lerp(start, end, amt) {
    return (1 - amt) * start + amt * end;
}

window.addEventListener("mousemove", moveCursor);

// window.addEventListener("mouseover", (event) => {
//     hoverScale = 5;
// });
// window.addEventListener("mouseleave", (event) => {
//     hoverScale = 1;
// });
