linkBox = document.getElementById('link');
linkBox.addEventListener('mousedown', paste);

// When on desktop, this function paste the contents of the clipboard when clicking on the link box,
// as this is quicker than right-click > Paste.
async function paste() {
    const clipboardText = await navigator.clipboard.readText();
    document.getElementById("link").value = clipboardText;
  }

const alertWrapper = document.getElementById("alert_wrapper");

function show_alert(message, type) {
    alertWrapper.style.display = 'block';
    alertWrapper.innerHTML =
    `<div class="alert alert-${type}" role="alert">
      ${message}
    </div>`
}

// A function that creates a synchronous sleep.
function sleep(milliseconds) {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}

async function showDownloadProgress(progressFilePath) {
    while (shouldLog) {
        try {
            const response = await fetch(progressFilePath);
            const textInFile = await response.text();
            lines = textInFile.split('\n');
            secondLastLine = lines[lines.length - 2];
            console.log('Reading from progress file:')
            console.log(secondLastLine);
            if (typeof secondLastLine === 'undefined') {
                show_alert('Initialising...', 'warning');
            }
            else if (secondLastLine.includes('Downloading webpage')) {
                show_alert('Video found...', 'success');
            }
            else if (secondLastLine.includes('[download] ')) {
                show_alert(secondLastLine.substring(11), 'info');
            }
            else if (secondLastLine.includes('[ffmpeg] Destination:')) {
                show_alert('Finishing up...', 'info');
            }
            else if (secondLastLine.includes('[ffmpeg] Merging ')) {
                show_alert('Merging audio and video...', 'info');
            }
            else if (secondLastLine.includes('Deleting original file ')) {
                show_alert('Finishing up...', 'info');
            }
            await sleep(500); // Using the sleep function created above.
        }
        catch(error) {
            show_alert(error, 'danger');
            console.log(error);
        }
    }
}

// This function runs when one of the download buttons is clicked.
async function buttonClicked(whichButton) { // whichButton is this.value in yt.html
    reset();
    if (linkBox.value == '') {
        show_alert('Trying to download something without pasting the URL? You silly billy.', 'warning')
        return;
    }

    const contentsOfLinkBox = linkBox.value;
    const regExp = /^(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?$/;

    if (contentsOfLinkBox.match(regExp)) {

        if (whichButton === 'Audio [best]') {
            document.getElementById('bitrate_info').style.display = 'block';
        }

        const firstFormData = new FormData();
        firstFormData.append('button_clicked', 'yes');

        // 1st POST request to get the path of the progress file.
        const requestProgressPath = await fetch('/yt', {
            method: 'POST',
            body: firstFormData
        });

        const progressFilePath = await requestProgressPath.text();
        console.log(`Progress File Path: ${progressFilePath}`)

        if (!requestProgressPath.ok) {
            show_alert(requestProgressPath, 'danger');
        }
        else {
            // The FormData for the 2nd POST request.
            const secondFormData = new FormData();
            secondFormData.append("link", linkBox.value);
            secondFormData.append("button_clicked", whichButton);

            shouldLog = true;
            showDownloadProgress(progressFilePath);

            // 2nd POST request to get the download link.
            const secondRequest = await fetch("/yt", {
                method: 'POST',
                body: secondFormData
            });

            if (secondRequest.ok) {

                shouldLog = false; // Set shouldLog to false to end the while loop in showDownloadProgress.

                const jsonResponse = await secondRequest.json();
                const downloadLink = jsonResponse.download_path
                const logFile = jsonResponse.log_file

                const virtualDownloadLink = document.createElement("a"); // Create a virtual link.
                virtualDownloadLink.href = downloadLink; // Setting the URL of createLink to downloadLink
                virtualDownloadLink.click();
                
                // Sometimes the alert below didn't show up but rather it would stay on the "Finishing up..." alert, 
                // adding a delay seems to fix this.
                await sleep(500)

                show_alert(`Your browser should have started downloading the file. If it hasn't, click \
                <a href="${downloadLink}">here</a>.`, "success");

                document.getElementById('logfile').innerHTML = `If you're a nerd, click \
                <a href="${logFile}" target="_blank">here</a> to view the youtube-dl log file.`
            }
            else {
                show_alert(secondRequest, 'danger');
                console.log(secondRequest);
            }
        }
    }
    else { // If the contents of the link box don't match the regex.
        show_alert(`Invalid URL provided.`, 'danger');
    }
}

function reset() {
    document.getElementById('logfile').innerHTML = '';
    document.getElementById('bitrate_info').style.display = 'none';
}