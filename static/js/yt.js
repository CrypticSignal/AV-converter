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
        const response = await fetch(progressFilePath);
        if (response.ok) {
            const textInFile = await response.text()
            lines = textInFile.split('\r')
            lastLine = lines[lines.length - 1];
            if (lastLine.includes('[MP3].mp3')) {
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
    }
}

// This function runs when one of the download buttons is clicked.
async function buttonClicked(whichButton) { // whichButton is this.value in yt.html
    reset();
    // If the "Choose" button was clicked.
    if (whichButton == 'other') {
        const data = new FormData();
        data.append("link", linkBox.value);
        data.append('button_clicked', 'other');
        // 1st POST request to get the path of the progress file.
        const response = await fetch('/yt', {
            method: 'POST',
            body: data
        });
        const jsonResponse = await response.json();
        const jsonParsed = JSON.parse(jsonResponse.streams)
        table = document.getElementById('table')
        table.innerHTML = '';
        const tbl = $("<table/>").attr("id", "mytable");
        const columnNames = `<th>Type</th><th>Resolution</th><th>Codec</th><th>Filetype</th><th>Size</th><th>Right click, save link</th></tr>`
        table.innerHTML = columnNames;
        for (let i = 0; i < jsonParsed.length; i++) {
            const openingTr = `<tr>`;
            const td1 = `<td>${jsonParsed[i]['type']}</td>`;
            const td2 = `<td>${jsonParsed[i]['resolution']}</td>`;
            const td3 = `<td>${jsonParsed[i]['codec']}</td>`;
            const td4 = `<td>${jsonParsed[i]['extension']}</td>`;
            let td5 = `<td>${jsonParsed[i]['file_size']}</td>`;
            if (jsonParsed[i]['file_size'] === null) {
                td5 = `<td>unknown</td>`
            }
            const td6 = `<td><a href="${jsonParsed[i]['video_url']}">Download</a></td>`;
            const closingTr = `</tr>`
            table.innerHTML += openingTr + td1 + td2 + td3 + td4 + td5 + td6 + closingTr;
        }  
        return;
    }

    if (linkBox.value == '') {
        show_alert('Trying to download something without pasting the URL? You silly billy.', 'warning')
        return;
    }
    show_alert('Initialising...', 'warning');
    const firstFormData = new FormData();
    firstFormData.append('button_clicked', 'yes');
    // 1st POST request to get the path of the progress file.
    const requestProgressPath = await fetch('/yt', {
        method: 'POST',
        body: firstFormData
    });
    if (!requestProgressPath.ok) {
        show_alert(requestProgressPath, 'danger');
        return;
    }
    else {
        const progressFilePath = await requestProgressPath.text();
        console.log(`https://free-av-tools.com/${progressFilePath}`)
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

        shouldLog = false; // Set shouldLog to false to end the while loop in showDownloadProgress.
        
        if (secondRequest.status == 200) {
            const jsonResponse = await secondRequest.json();
            console.log(jsonResponse)
            const downloadLink = jsonResponse.download_path;
            const logFile = jsonResponse.log_file;
           
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
            error = await secondRequest.text()
            show_alert(error, 'danger')
            console.log(error)
            return;
        }
        else {
            shouldLog = false;
            show_alert(`${secondRequest.status} status code`)
            console.log(secondRequest)
            return;
        }
    }
}

function reset() {
    document.getElementById('logfile').innerHTML = '';
}