const pageLoadTime = Date.now();
const canvas = document.getElementById('canvas');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
const ctx = canvas.getContext('2d');

if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
    canvas.addEventListener("touchstart", mouseClicked);
} else {
    window.addEventListener("keydown", mouseClicked);
    canvas.addEventListener("mousedown", mouseClicked);
} 

// If the user has visited the page Before, don't show the opening alert.
const isVisited = localStorage.getItem('isVisitedGame2');
if (isVisited !== "yes") {
    alert("This game tests your reaction speed. Click on the screen (or hit any key) as soon as it turns green.")
        localStorage.setItem('isVisitedGame2', 'yes');
}

let t = [];
const sampleSize = 30;
let sumOfDifferences = 0;
let canvasUpdateRate;
let refreshRate;

// Calculate how often the browser updates the canvas.
function calculateCanvasUpdateRate(millisecondsSinceTimeOrigin) {
    t.push(millisecondsSinceTimeOrigin);
    // Put sampleSize + 1 samples into the array so we can check the difference 50 times.
    if (t.length == (sampleSize + 1)) {
        for (let i = 1; i < (sampleSize + 1); i++) {
            sumOfDifferences += (t[i] - t[i - 1]);
        }
        canvasUpdateRate = Math.round(sumOfDifferences / sampleSize);
        //refreshRate = (1000 / canvasUpdateRate).toFixed(1);;
        console.log(`Calculation took ${millisecondsSinceTimeOrigin} ms with a sampleSize of ${sampleSize}.`);
        return;
    }
    window.requestAnimationFrame(calculateCanvasUpdateRate);
};

// Run the above function.
window.requestAnimationFrame(calculateCanvasUpdateRate);

function randInt(min, max) {
    return min + Math.floor(Math.random() * (max - min + 1));
}

const randomTime = randInt(1000, 5000)

// Run the changeColour func after randomTime ms
setTimeout(changeColour, randomTime)

let clickTime = null;
let changeTime = null;

function changeColour() {
    ctx.fillStyle = "#32CD32";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    changeTime = Date.now()
}

async function mouseClicked() {

    clickTime = Date.now();
    const timeSincePageLoad = clickTime - pageLoadTime;

    if (timeSincePageLoad < randomTime) { // User clicked before the screen turned green.

        if (confirm("You clicked too early. Click on 'OK' if you'd like to try again.")) {
            location.reload();
        }
        else {
            window.location.href = "https://freeaudioconverter.net";
        }
    }

    else { // User clicked after the screen turned green

        clickTime = Date.now();

        const reactionTimeRaw = clickTime - changeTime;
        const averageDelay = canvasUpdateRate / 2;
        const reactionTime = Math.round(reactionTimeRaw - averageDelay);
        const lowerRange = Math.round(reactionTime - canvasUpdateRate);
        console.log(`${lowerRange}-${reactionTimeRaw}ms`)

        if (localStorage.getItem('game2score') == null || reactionTime < localStorage.getItem('game2score')) {
            localStorage.setItem('game2score', reactionTime);
        }

        const highScore = localStorage.getItem('game2score');

        const data = new FormData();
        data.append("reaction_time", reactionTime)

        const response = await fetch('/game2', {
            method: 'POST',
            body: data
        });

        //const responseText = await response.text();

        if (response.status === 200) {

            if (confirm(`Reaction Time: ~${reactionTime} ms\nPersonal Best: ~${highScore} ms\nTo play again, click on 'OK'`)) {
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
}