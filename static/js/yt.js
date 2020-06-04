const alertWrapper = document.getElementById("alert_wrapper");

function show_alert(message, type) {
    alertWrapper.style.display = 'block';
    alertWrapper.innerHTML =
    `<div class="alert alert-${type}" role="alert">
      ${message}
    </div>`
}

// A function that creates a synchronous sleep.
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

let shouldLog = true;

async function showDownloadProgress() {
    while (shouldLog) {
        const response = await fetch('static/output.txt');
        const textInFile = await response.text();
        lines = textInFile.split('\n');
        secondLastLine = lines[lines.length - 2];
        if (typeof secondLastLine === 'undefined') {
            secondLastLine = 'Starting download...';
        }
        else if (secondLastLine.includes('[ffmpeg] Destination:')) {
            secondLastLine = 'Just a few seconds...';
        }
        show_alert(secondLastLine, "info");
        await sleep(1000); // Using the sleep function defined above.
    }
}
  
// This function runs when one of the download buttons is clicked.
async function buttonClicked(whichButton) {
    const link = document.getElementById('link').value;
    const data = new FormData();
    data.append("link", link);
    data.append("button_clicked", whichButton);
    shouldLog = true;
    showDownloadProgress();
    // The "await" word means wait for a response to be received before executing the rest of the code (lines 48+)
    const responseWithDownloadLink = await fetch("/yt", {
        method: 'POST',
        body: data,
    })
    // As we're using await fetch, if we reach this line, it means that we've received a response from the server,
    // so the download has completed.
    show_alert("All done!", "success");
    shouldLog = false; // Set shouldLog to false to end the while loop in showDownloadProgress.
    const downloadLink = await responseWithDownloadLink.text()
    const createLink = document.createElement("a"); // Create a virtual link.
    createLink.download = ''; // The download attribute specifies that the file will be downloaded
    // when the link is visited. As we have set an empty value, it means use the original filename.
    createLink.href = downloadLink; // Setting the URL of createLink to downloadLink
    createLink.click();
}