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
            const textInFile = await response.text()
            lines = textInFile.split('\r')
            lastLine = lines[lines.length - 1];
            console.log(lastLine);
            if (lastLine.includes('Downloading webpage')) {
                show_alert('Initialising...', 'warning');
            }
            else if (lastLine.includes('[MP3].mp3')) {
                show_alert('Converting to MP3...', 'info')
            }
            else if (lastLine.includes('[ffmpeg] Merging')) {
                show_alert('Merging audio and video...', 'info');
            }
            else if (lastLine.includes('Deleting original file ') || lastLine.includes('[ffmpeg] D')) {
                show_alert('Finishing up...', 'info');
            }
            else if (lastLine.includes('[download] ')) {
                show_alert(lastLine.substring(11), 'info');
            }
            await sleep(500); // Using the sleep function created above.
        }
        catch(error) {
            shouldLog = false;
            show_alert(error);
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
    
    const firstFormData = new FormData();
    firstFormData.append('button_clicked', 'yes');

    // 1st POST request to get the path of the progress file.
    const requestProgressPath = await fetch('/yt', {
        method: 'POST',
        body: firstFormData
    });

    const progressFilePath = await requestProgressPath.text();

    if (!requestProgressPath.ok) {
        show_alert(requestProgressPath, 'danger');
        return;
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
        console.log(`secondRequest status: ${secondRequest.status}`)
        if (secondRequest.status == 200){
    
            shouldLog = false; // Set shouldLog to false to end the while loop in showDownloadProgress.

            const jsonResponse = await secondRequest.json();
            console.log(`jsonResponse: ${jsonResponse}`)
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
        
        else if (secondRequest.status == 500) {
            shouldLog = false;
            error = await secondRequest.text()
            show_alert(error, 'danger')
            console.log(error)
            return;
        }
        else {
            shouldLog = false;
            show_alert(`HTTP Status Code: ${secondRequest.status}`)
            return;
        }
    }
}

function reset() {
    document.getElementById('logfile').innerHTML = '';
}