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

async function showDownloadProgress(progressFilename) {
    while (shouldLog) {
        try {
            const response = await fetch(`yt-progress/${progressFilename}`);
            console.log('Response when fetching the .txt file:');
            console.log(response);
            const textInFile = await response.text();
            lines = textInFile.split('\n');
            secondLastLine = lines[lines.length - 2];
            console.log(secondLastLine);
            if (typeof secondLastLine === 'undefined') {
                show_alert('Initialising...', 'dark');
            }
            else if (secondLastLine.includes('Downloading webpage')) {
                show_alert('Video found...', 'success');
            }
            else if (secondLastLine.includes('[download] ')) {
                show_alert(secondLastLine.substring(11), 'dark');
            }
            else if (secondLastLine.includes('[ffmpeg] Destination:')) {
                show_alert('Finishing up...', 'dark');
            }
            else if (secondLastLine.includes('[ffmpeg] Merging ')) {
                show_alert('Merging audio and video...', 'dark');
            }
            else if (secondLastLine.includes('Deleting original file ')) {
                show_alert('Almost done...', 'dark');
            }
            else if (secondLastLine.includes('[ffmpeg] Adding thumbnail')) {
                show_alert( `Your browser should have started downloading the file. If it hasn't, click \
                <a href="${downloadLink}">here</a>.`, 'success');
            }
            await sleep(1000); // Using the sleep function created above.
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
            document.getElementById('donate').style.display = 'none';
            document.getElementById('bitrate_info').style.display = 'block';
        }

        const firstFormData = new FormData();
        firstFormData.append('button_clicked', 'yes');
        
        // 1st POST request to get the name of the progress file.
        const progressFileResponse = await fetch('/yt', {
            method: 'POST',
            body: firstFormData
        });
        
        const progressFilename = await progressFileResponse.text();
        console.log(`progressFilename: ${progressFilename}`)

        if (!progressFileResponse.ok) {
            show_alert(progressFileResponse, 'danger');
            console.log(progressFileResponse);
        }
        else {
            // The FormData for the 2nd POST request.
            const secondFormData = new FormData();
            secondFormData.append("link", linkBox.value);
            secondFormData.append("button_clicked", whichButton);

            shouldLog = true;
            showDownloadProgress(progressFilename);
            
            // 2nd POST request to get the download link.
            const response = await fetch("/yt", {
                method: 'POST',
                body: secondFormData
            });

            if (response.ok) {
    
                shouldLog = false; // Set shouldLog to false to end the while loop in showDownloadProgress.

                const jsonResponse = await response.json();

                const downloadLink = jsonResponse.download_path
                const logFile = jsonResponse.log_file
                
                const virtualDownloadLink = document.createElement("a"); // Create a virtual link.
                virtualDownloadLink.href = downloadLink; // Setting the URL of createLink to downloadLink
                virtualDownloadLink.click();

                show_alert(`Your browser should have started downloading the file. If it hasn't, click \
                <a href="${downloadLink}">here</a>.`, "success");

                document.getElementById('logfile').innerHTML = `Would you like to view the log file? If so, click \
                <a href="${logFile}" target="_blank">here</a>.`
            } 
            else {
                show_alert(response, 'danger');
                console.log(response);
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