const canvas = document.querySelector('canvas');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
const ctx = canvas.getContext('2d');
const audio = document.getElementById("myAudio");
canvas.addEventListener("click", getClickLocation)
ctx.font = "20px arial";

//alert("This game tests your reaction speed. Whenever you click on the circle, it spawns in a new location. How many times can you click on the circle in 10 seconds? Dismiss this alert to begin playing.")
// Self-explanatory.

ctx.fillText(`Window Dimensions: ${canvas.width}x${canvas.height}`, 0, 20);

let x = Math.round(canvas.width / 2);
let y = Math.round(canvas.height / 2);
const radius = Math.round(canvas.height / 12);

// Function to create a circle.
function createCircle(x, y) {
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.stroke();
    ctx.fillStyle = "#000000";
    ctx.fill();
}

// Show the first circle.
createCircle(x, y);

currentXLocation = x;
currentYLocation = y;

function removeCircle(currentXLocation, currentYLocation){
    ctx.beginPath();
    ctx.clearRect(currentXLocation - radius - 1, currentYLocation - radius - 1, radius * 2 + 2, radius * 2 + 2);
    ctx.closePath();
}

let timesClicked = 0;
let timesMissed = 0;
let timer = 10;

function newCircle() {
    timesClicked += 1;
    x = Math.floor(Math.random() * (canvas.width - radius - radius)) + radius;
    y = Math.floor(Math.random() * (canvas.height - radius - radius)) + radius;
    removeCircle(currentXLocation, currentYLocation);
    createCircle(x, y)
    currentXLocation = x;
    currentYLocation = y;
}

function getClickLocation (event) {
    // Detect where the user clicks/touches
    let xPosition = event.offsetX;
    let yPosition = event.offsetY;
    // Check if the click location is within the circle:

    // Distance of click from centre of circle.
    const deltaX = xPosition - currentXLocation
    const deltaY = yPosition - currentYLocation

    // a^2 + b^2 = c^2
    if ((deltaX * deltaX) + (deltaY * deltaY) <= (radius * radius)) {

        newCircle();

        if (timesClicked == 1) {
            setInterval(showTimer, 1000); // Run the showTimer function every 1000ms.
            showTimer();
            ctx.clearRect(0, 0, canvas.width, 24);
        }

        else if (timesClicked == 101) {
            removeCircle(currentXLocation, currentYLocation);
            location.reload();
        } 
    }

    else { // Don't spawn a new square and increased timesMissed by 1.
        timesMissed += 1;
    }
}

function showTimer() {
    timer -= 1; 
    ctx.clearRect(canvas.width/2, 0, 20, 20);
    ctx.fillText(timer, canvas.width/2, 20);

    if (timer == 0) {
        alert(`
        You got the circle ${timesClicked} times.
        Average hits per second: ${timesClicked/10}
        Misses: ${timesMissed}
        Accuracy: ${((timesClicked / (timesClicked + timesMissed)) * 100).toFixed(1)}%
        To play again, dismiss this alert and click on the circle.`)
    }

    else if (timer < 0) {
        ctx.clearRect(0, 0, canvas.width, 20)
        timesClicked = 100;
    }
}