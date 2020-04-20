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
let refreshRate;

function animate(timeSinceTimeOrigin) {
    t.unshift(timeSinceTimeOrigin);
    if (t.length > 50) {
        const t0 = t.pop();
        refreshRate = (1000 * 50) / (timeSinceTimeOrigin - t0);
        console.log(`20 samples taken in ${timeSinceTimeOrigin} ms.`);
        return;
    }
    window.requestAnimationFrame(animate);
};

// Start the above function.
window.requestAnimationFrame(animate);

function randInt(min, max) {
    return min + Math.floor(Math.random() * (max - min + 1));
}

const randomTime = randInt(1000, 5000)
console.log("Colour will change in " + randomTime + " millseconds.")

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
        const canvasUpdateRate = (1000 / refreshRate);
        const averageDelay = canvasUpdateRate / 2;
        const reactionTime = Math.round(reactionTimeRaw - averageDelay);

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

        const responseText = await response.text();

        if (response.status === 200) {

            if (confirm(`Reaction Time: ~${reactionTime} ms\nPersonal Best: ${highScore} ms\nWorld Record: ${responseText} ms\nCanvas Refresh Rate: ${Math.round(refreshRate)} Hz\nTo play again, click on 'OK'`)) {
                location.reload();
            }
            else {
                window.location.href = "https://freeaudioconverter.net";
            }
        }
        else {
            console.log("status is: " + response.status)
        }
    }
}