

// When on desktop, this function paste the contents of the clipboard when clicking on the link box,
// as this is quicker than right-click > Paste.
async function paste() {
    const clipboardText = await navigator.clipboard.readText();
    document.getElementById("link").value = clipboardText;
  }

const alertWrapper = document.getElementById("alert_wrapper");

function showAlert(message, type) {
    const alertWrapper = document.getElementById("alert_wrapper");
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

let shouldLog = false;

async function showDownloadProgress(progressFilePath) {
    while (shouldLog) {
        const response = await fetch(progressFilePath);
        if (response.ok) {
            const textInFile = await response.text()
            const lines = textInFile.split('\r')
            const lastLine = lines[lines.length - 1];
            if (lastLine.includes('[MP3].mp3')) {
                showAlert('Converting to MP3...', 'info')
            }
            else if (lastLine.includes('[ffmpeg] Merging')) {
                showAlert('Merging audio and video...', 'info');
            }
            else if (lastLine.includes('Deleting original file ') || lastLine.includes('[ffmpeg] D')) {
                showAlert('Finishing up...', 'info');
            }
            else if (lastLine.includes('[download] ')) {
                showAlert(lastLine.substring(11), 'info');
            }
            await sleep(500); // Using the sleep function created above.
        }
    }
}

// This function runs when one of the download buttons is clicked.
async function buttonClicked(url, whichButton) { // whichButton is this.value in yt.html
    const linkBox = document.getElementById('link');
    console.log(`whichButton: ${whichButton}`)
    linkBox.addEventListener('mousedown', paste);
    if (linkBox.value == '') {
        showAlert('Trying to download something without pasting the URL? You silly billy.', 'warning')
        return;
    }

    showAlert('Initialising...', 'warning');
    const firstFormData = new FormData();
    firstFormData.append('button_clicked', 'yes');
    // 1st POST request to get the path of the progress file.
    const requestProgressPath = await fetch('/api/yt', {
        method: 'POST',
        body: firstFormData
    });

    if (!requestProgressPath.ok) {
        showAlert(requestProgressPath, 'danger');
        return;
    }
    else {
        let progressFilePath = await requestProgressPath.text();
        progressFilePath = `api/${progressFilePath}`
        console.log(`https://free-av-tools.com/${progressFilePath}`)
        const secondFormData = new FormData();
        secondFormData.append("link", url);
        secondFormData.append("button_clicked", whichButton);

        shouldLog = true;
        showDownloadProgress(progressFilePath);

        // 2nd POST request to get the download link.
        const secondRequest = await fetch("/api/yt", {
            method: 'POST',
            body: secondFormData
        });

        // Set shouldLog to false to end the while loop in showDownloadProgress.
        shouldLog = false; 
        
        if (secondRequest.status == 200) {
            const response = await secondRequest.text();
            console.log(response)
           
            const anchorTag = document.createElement("a");
            anchorTag.href = response; 
            anchorTag.download = ''
            anchorTag.click();
            
            // Sometimes the alert below didn't show up, adding a delay seems to fixes this.
            await sleep(500)
            showAlert(`Your browser should have started downloading the file. \
                       Click <a href="${progressFilePath}">here</a> if you'd like to view the log file.`, 'success');
        }
        
        else if (secondRequest.status == 500) {
            const error = await secondRequest.text()
            showAlert(error, 'danger')
            console.log(error)
            return;
        }
        else {
            shouldLog = false;
            showAlert(`${secondRequest.status} status code`)
            console.log(secondRequest)
            return;
        }
    }
}

export default buttonClicked;