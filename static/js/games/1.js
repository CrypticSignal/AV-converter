const canvas = document.getElementById('canvas');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
const ctx = canvas.getContext('2d');
ctx.font = "20px arial";
ctx.fillText(`Window Dimensions: ${canvas.width}x${canvas.height}`, 0, 20);

if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
    canvas.addEventListener("touchstart", isCircleHit);
    canvas.addEventListener("touchmove", function(event) {
        event.preventDefault();
        event.stopPropagation();
    }, false);
} else {
    canvas.addEventListener("mousemove", changeColour);
    canvas.addEventListener("mousedown", isCircleHit);
}

// If the user has visited the page Before, don't show the opening alert.
const isVisited = localStorage.getItem('isVisited');
if (isVisited !== "yes") {
    alert("This game tests your reaction speed. Whenever you hit the circle, it spawns in a new location. How many times can you hit the circle in 15 seconds? Dismiss this alert to begin playing.");
    localStorage.setItem('isVisited', 'yes')
}

// The centre of the first circle should be in the middle of the canvas.
let x = Math.round(canvas.width / 2);
let y = Math.round(canvas.height / 2);

// Make the diameter of the circle a quarter of the longest side of the canvas.
const radius = (canvas.width < canvas.height) ? Math.round(canvas.height / 8) : Math.round(canvas.width / 8);

// Function to create a circle.
function createCircle(x, y) {
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.stroke();
    ctx.fillStyle = "#FFFFFF";
    ctx.fill();
}

// Show the first circle.
createCircle(x, y);

let currentXLocation = x;
let currentYLocation = y;

// Make circle green when mouse is hovered on the circle.
function changeColour (event) {

    xPosition = event.offsetX;
    yPosition = event.offsetY;
    // Distance of hit from the centre of the circle.
    deltaX = xPosition - currentXLocation
    deltaY = yPosition - currentYLocation

    // Use a^2 + b^2 = c^2 to check if the hit is within the circle.
    if (((deltaX * deltaX) + (deltaY * deltaY)) <= (radius * radius)) {
        ctx.beginPath();
        ctx.arc(currentXLocation, currentYLocation, radius, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.fillStyle = "#32CD32";
        ctx.fill();    
    }
    else {
        ctx.beginPath();
        ctx.arc(currentXLocation, currentYLocation, radius, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.fillStyle = "#FFFFFF";
        ctx.fill();
    }
}

function removeCircle(currentXLocation, currentYLocation){
    ctx.beginPath();
    ctx.clearRect(currentXLocation - radius - 1, currentYLocation - radius - 1, radius * 2 + 2, radius * 2 + 2);
    ctx.closePath();
}

let timesHit = 0;
let timesMissed = 0;
let timer = 15;

function newCircle() {
    timesHit += 1;
    x = Math.floor(Math.random() * (canvas.width - radius - radius)) + radius;
    y = Math.floor(Math.random() * (canvas.height - radius - radius)) + radius;
    removeCircle(currentXLocation, currentYLocation);
    createCircle(x, y)
    currentXLocation = x;
    currentYLocation = y;
}

async function showTimer() {
    timer -= 1; 
    ctx.clearRect(canvas.width/2, 0, 40, 20);
    ctx.fillText(timer, canvas.width/2, 20);

    if (timer == 0) {

        if (localStorage.getItem('highScore') == null) {
            localStorage.setItem('highScore', timesHit)
        }
       
        else if (timesHit > localStorage.getItem('highScore')){
            localStorage.setItem('highScore', timesHit)
        }

        const highScore = localStorage.getItem('highScore')
        const accuracy = `${Math.round((timesHit / (timesHit + timesMissed)) * 100)}%`
        
        const data = new FormData();
        data.append('score', timesHit);
        data.append('times_missed', timesMissed);
        data.append('canvas_width', canvas.width);
        data.append('canvas_height', canvas.height);
        
        const response = await fetch('/game', {
            method: 'POST',
            body: data
        });

        const responseText = await response.text();

        if (response.status === 200) { 

            if (confirm(`You hit the circle ${timesHit} times\nYour high score: ${highScore}\nTo play again, click on 'OK'`)) {
                location.reload();
            }
            else {
                window.location.href = "https://freeaudioconverter.net";
            }
        }
        else {
            console.log(`Couldn't receive response from server [${response.status}]`)
        }
    }
    else if (timer < 0) {
        ctx.clearRect(0, 0, canvas.width, 20)
    }
}

let xPosition;
let yPosition;
let deltaX;
let deltaY;

function isCircleHit (event) {

    if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
        touchIndex = event.touches.length - 1;
        xPosition = event.touches[`${touchIndex}`].clientX;
        yPosition = event.touches[`${touchIndex}`].clientY;
    }
    else {
        xPosition = event.clientX;
        yPosition = event.clientY;
    }
    
    // Distance of hit from the centre of the circle.
    const deltaX = xPosition - currentXLocation
    const deltaY = yPosition - currentYLocation

    // Use a^2 + b^2 = c^2 to check if the hit is within the circle.
    if (((deltaX * deltaX) + (deltaY * deltaY)) <= (radius * radius)) {
        newCircle();
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