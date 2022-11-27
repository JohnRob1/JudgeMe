const cursor = document.querySelector(".cursor");
const cursorBlob = document.querySelector(".cursor-blob");

const blobSmoothSpeed = 0.2;

var mouseY = 150;
var mouseX = 150;

var smoothX = 150;
var smoothY = 150;
var midX = 150;
var midY = 150;

var scaleX = 1;
var scaleY = 1;

var hoverScale = 1;
var hovering = false;

setInterval(moveBlob, 1000 / 60);

function moveBlob() {
    var targetPosX = hovering ? midX : mouseX;
    var targetPosY = hovering ? midY : mouseY;
    smoothX = lerp(smoothX, targetPosX, blobSmoothSpeed);
    smoothY = lerp(smoothY, targetPosY, blobSmoothSpeed);

    cursorBlob.style.left = smoothX + "px";
    cursorBlob.style.top = smoothY + "px";

    var deltaX = targetPosX - smoothX;
    var deltaY = targetPosY - smoothY;

    var delta = Math.abs(deltaX) + Math.abs(deltaY);
    var scale = delta / 300;

    var pulse = Math.sin(new Date() / 500) * 0.2;

    var rotation = Math.atan(deltaY / deltaX);

    targetScaleX = (1 + scale) * hoverScale * 1 + pulse;
    targetScaleY = (1 - scale / 2) * hoverScale * 1 + pulse;

    scaleX = lerp(scaleX, targetScaleX, 0.2);
    scaleY = lerp(scaleY, targetScaleY, 0.2);

    cursorBlob.style.transform = `
        rotate(${rotation}rad)
        scale(${scaleX}, ${scaleY})
        `;
}

const moveCursor = (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;

    cursor.style.left = mouseX + "px";
    cursor.style.top = mouseY + "px";

    var element = document.elementFromPoint(e.clientX, e.clientY);

    if(element == null)
        return
    
    var rect = element.getBoundingClientRect();

    hovering = element.nodeName == "BUTTON";

    midX = (rect.right + rect.left) / 2;
    midY = (rect.top + rect.bottom) / 2;
    hoverScale = hovering ? 3 : 1;
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
