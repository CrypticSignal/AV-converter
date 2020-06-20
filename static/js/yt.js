linkBox = document.getElementById('link');
linkBox.addEventListener('touchstart', paste);

async function paste() {
    const text = await navigator.clipboard.readText();
    document.getElementById("link").value = text;
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
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function showDownloadProgress() {

    shouldLog = true;

    while (shouldLog) {
        try {
            const response = await fetch(`static/progress/${progressFilename}.txt`);
            const textInFile = await response.text();
            lines = textInFile.split('\n');
            secondLastLine = lines[lines.length - 2];
            if (typeof secondLastLine === 'undefined') {
                secondLastLine = 'Initialising...';
            }
            else if (secondLastLine.includes('[ffmpeg] Destination:')) {
                secondLastLine = 'Finishing up...';
            }
            else if (secondLastLine.includes('Deleting original file ')) {
                secondLastLine = 'Almost done...';
            }
            else if (secondLastLine.includes('[ffmpeg] Adding thumbnail')) {
                secondLastLine = 'Setting video thumnail as convert art...';
            }

            show_alert(secondLastLine, "info");
            console.log(secondLastLine);
            await sleep(500); // Using the sleep function defined above.
        } catch(error) {
            console.log(error);
        }
    }
}
  
// This function runs when one of the download buttons is clicked.
async function buttonClicked(whichButton) { // whichButton is this.value in yt.html
    if (linkBox.value == '') {
        show_alert('Trying to download something without pasting the URL? You silly billy.', 'warning')
        return;
    }
    const url = linkBox.value;
    const regExp = /^(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?$/;
    if (url.match(regExp)) {
        try {
            const logButtonClicked = new FormData();
            logButtonClicked.append('button_clicked', 'yes')
            // Python will return the filename for the youtube-dl progress file.
            filenameResponse = await fetch('/yt', {
                method: 'POST',
                body: logButtonClicked
            });
        } catch(error) {
            console.log(error);
        }
        
        progressFilename = await filenameResponse.text();


        console.log(`progressFilename: ${progressFilename}`);

        const link = document.getElementById('link').value;
        const data = new FormData();
        data.append("link", link);
        data.append("button_clicked", whichButton);
        shouldLog = true;
        showDownloadProgress();
        // The "await" word means wait for a response to be received before executing the rest of the code (lines 48+)
        try {
            const responseWithDownloadLink = await fetch("/yt", {
                method: 'POST',
                body: data
            });
            // As we're using await fetch, if we reach this line, it means that we've received a response,
            // so the download has completed.
            shouldLog = false; // Set shouldLog to false to end the while loop in showDownloadProgress.
            downloadLink = await responseWithDownloadLink.text();
            show_alert(`Your browser should have started downloading the file. If it hasn't, click \
            <a href="${downloadLink}">here</a>.`, "success");
            const createLink = document.createElement("a"); // Create a virtual link.
            // when the link is visited. As we have set an empty value, it means use the original filename.
            createLink.href = downloadLink; // Setting the URL of createLink to downloadLink
            createLink.download = ''; // The download attribute specifies that the file will be downloaded
            createLink.click();
        } 
        catch(error) {
            console.log(error);
        }
    }
    else {
        show_alert(`Invalid URL provided.`, 'danger');
    }
}