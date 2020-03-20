const canvas = document.getElementById('canvas');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
const ctx = canvas.getContext('2d');
ctx.font = "20px arial";
ctx.fillText(`Window Dimensions: ${canvas.width}x${canvas.height}`, 0, 20);
canvas.addEventListener("touchstart", isCircleHit)
canvas.addEventListener("click", isCircleHit)

// If the user has visited the page Before, don't show the opening alert.
const isVisited = localStorage.getItem('isVisited');
if (isVisited !== "yes") {
    alert("This game tests your reaction speed. Whenever you hit the circle, it spawns in a new location. How many times can you hit the circle in 10 seconds? Dismiss this alert to begin playing.");
    localStorage.setItem('isVisited', 'yes')
}

// The centre of the first circle should be in the middle of the canvas.
x = Math.round(canvas.width / 2);
y = Math.round(canvas.height / 2);

// Make the diameter of the circle a fifth of the height of the canvas.
const radius = Math.round(canvas.height / 10);

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

let timesHit = 0;
let timesMissed = 0;
let timer = 10;

function newCircle() {
    timesHit += 1;
    x = Math.floor(Math.random() * (canvas.width - radius - radius)) + radius;
    y = Math.floor(Math.random() * (canvas.height - radius - radius)) + radius;
    removeCircle(currentXLocation, currentYLocation);
    createCircle(x, y)
    currentXLocation = x;
    currentYLocation = y;
}

function showTimer() {
    timer -= 1; 
    ctx.clearRect(canvas.width/2, 0, 20, 20);
    ctx.fillText(timer, canvas.width/2, 20);

    if (timer == 0) {

        if (confirm(`
        You hit the circle ${timesHit} times.
        Average hits per second: ${timesHit/10}
        Misses: ${timesMissed}
        Accuracy: ${((timesHit / (timesHit + timesMissed)) * 100).toFixed(1)}%
        To play again, click on 'OK'`)) {
            location.reload();
        }
        else {
            window.location.href = "https://freeaudioconverter.net";
        }
    }
    else if (timer < 0) {
        ctx.clearRect(0, 0, canvas.width, 20)
    }
}

function isCircleHit (event) {

    if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
        var xPosition = event.touches[0].clientX;
        var yPosition = event.touches[0].clientY;
    } else {
        var xPosition = event.offsetX;
        var yPosition = event.offsetY;
    }

    // Distance of hit from the centre of the circle.
    const deltaX = xPosition - currentXLocation
    const deltaY = yPosition - currentYLocation

    // Use a^2 + b^2 = c^2 to check if the hit is within the circle.
    if (((deltaX * deltaX) + (deltaY * deltaY)) <= (radius * radius)) {

        newCircle();
        //navigator.vibrate(50); 

        if (timesHit == 1) {
            setInterval(showTimer, 1000); // Run the showTimer function every 1000ms.
            ctx.clearRect(0, 0, canvas.width, 20);
        }

        else if (timesHit == 101) {
            location.reload();
        } 
    }

    else { // Don't spawn a new square and increased timesMissed by 1.
        timesMissed += 1;
    }
}
