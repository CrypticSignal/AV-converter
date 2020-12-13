linkBox = document.getElementById('link');
linkBox.addEventListener('mousedown', paste);

// This function pastes the contents of the clipboard when clicking on the link box,
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
            console.log(lastLine);
            if (lastLine.includes('.audio_mp3')) {
                show_alert('Converting to MP3...', 'info')
            }
            else if (lastLine.includes('[ffmpeg] Merging')) {
                show_alert('Merging audio and video...', 'info');
            }
            else if (lastLine.includes('[ffmpeg] Merging')) {
                show_alert('Merging audio and video...', 'info');
            }
            else if (lastLine.includes('[download] ')) {
                show_alert(lastLine.substring(11), 'info');
            }
            else {
                show_alert(lastLine, 'info');
            }
            await sleep(500);
        }
    }
}

// This function runs when one of the download buttons is clicked.
async function buttonClicked(whichButton) { // whichButton is this.value in yt.html

    if (linkBox.value == '') {
        show_alert('Trying to download something without pasting the URL? You silly billy.', 'warning')
        return;
    }

    // If the "Other" button was clicked.
    if (whichButton == 'other') {
        hideInitialButtons();
        document.getElementById('table_div').style.display = 'block'
        document.getElementById('bring_back_other_buttons').style.display = 'block';
        const formData = new FormData();
        formData.append("link", linkBox.value);
        formData.append('button_clicked', 'other');

        const response = await fetch('/yt', {
            method: 'POST',
            body: formData
        });

        const jsonResponse = await response.json();
        const jsonParsed = JSON.parse(jsonResponse.streams)

        table = document.getElementById('table')
        table.innerHTML = '';
        const tbl = $("<table/>").attr("id", "mytable");
        const columnNames = `<th>Type</th><th>Resolution</th><th>Codec</th><th>Filetype</th><th>Size</th><th>Right click on Download, save link</th>`
        table.innerHTML = columnNames;

        for (let i = 0; i < jsonParsed.length; i++) {
            const openingTr = `<tr>`;
            const td1 = `<td>${jsonParsed[i]['type']}</td>`;
            const td2 = `<td>${jsonParsed[i]['resolution']}</td>`;
            const td3 = `<td>${jsonParsed[i]['codec']}</td>`;
            const td4 = `<td>${jsonParsed[i]['extension']}</td>`;
            let td5 = `<td>${jsonParsed[i]['filesize']}</td>`;
            if (jsonParsed[i]['filesize'] === null) {
                td5 = `<td>unknown</td>`
            }
            const td6 = `<td><a href="${jsonParsed[i]['video_url']}">Download</a></td>`;
            const closingTr = `</tr>`
            table.innerHTML += openingTr + td1 + td2 + td3 + td4 + td5 + td6 + closingTr;
        }
        hideInitialButtons();
        return;
    }

    // If one of the other buttons was clicked, we will send 2 POST requests.
    // The first request will receive the path of the youtube-dl progress file.
    // The second request will receive the download link.
    else {
        show_alert('Initialising...', 'warning');

        // 1st POST request
        const requestProgressPath = await fetch('/yt', {
            method: 'POST',
            body: 'send_progress_path'
        });

        if (!requestProgressPath.ok) {
            show_alert(requestProgressPath, 'danger');
            return;
        }
        else {
            const progressFilePath = await requestProgressPath.text();
            console.log(`https://free-av-tools.com/${progressFilePath}`)
            const formData = new FormData();
            formData.append("link", linkBox.value);
            formData.append("button_clicked", whichButton);

            if (whichButton == 'download_mp3') {
                const mp3EncodingType = document.getElementById('mp3_encoding_type').value;
                const mp3Bitrate = document.getElementById('mp3_bitrate').value;
                const vbrSettingMP3 = document.getElementById('mp3_vbr_setting').value;

                formData.append("mp3_encoding_type", mp3EncodingType);
                formData.append("mp3_bitrate", mp3Bitrate);
                formData.append("mp3_vbr_setting", vbrSettingMP3);
            }

            shouldLog = true;
            showDownloadProgress(progressFilePath);

            // 2nd POST request to get the download link.
            const secondRequest = await fetch("/yt", {
                method: 'POST',
                body: formData
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
                show_alert(`Your browser should have started downloading the file. \
                           Click <a href="${progressFilePath}" target="_blank">here</a> \
                           if you'd like to view the log file.`, 'success');
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
}

function hideInitialButtons() {
    document.getElementById('mp4').style.display = 'none';
    document.getElementById('video_best').style.display = 'none';
    document.getElementById('audio_mp3').style.display = 'none';
    document.getElementById('audio').style.display = 'none';
    document.getElementById('other').style.display = 'none';
    document.getElementById('alert_wrapper').style.display = 'none';
}

function showInitialButtons() {
    document.getElementById('mp4').style.display = 'block';
    document.getElementById('video_best').style.display = 'block';
    document.getElementById('audio_mp3').style.display = 'block';
    document.getElementById('audio').style.display = 'block';
    document.getElementById('other').style.display = 'block';
    document.getElementById('table_div').style.display = 'none';
    document.getElementById('bring_back_other_buttons').style.display = 'none';
    document.getElementById('mp3_div').style.display = 'none';
}

function showMP3Div() {
    hideInitialButtons();
    document.getElementById('mp3_div').style.display = 'block';
    document.getElementById('mp3_encoding_type').selectedIndex = 1;
    document.getElementById('mp3_slider_div').style.display = 'block';
    document.getElementById('mp3_vbr_setting_div').style.display = 'none';
    document.getElementById('bring_back_other_buttons').style.display = 'block';
}

function showHideMP3(value) {
    if (value == 'cbr') {
        document.getElementById('mp3_slider_div').style.display = 'block';
        document.getElementById('mp3_vbr_setting_div').style.display = 'none';
    }
    else {
        document.getElementById('mp3_vbr_setting_div').style.display = 'block';
        document.getElementById('mp3_slider_div').style.display = 'none';
    }
}

// MP3 CBR bitrate slider.
const mp3Slider = document.getElementById("mp3_bitrate");
const bitrateValue = document.getElementById("bitrate_value");
bitrateValue.innerHTML = mp3Slider.value + " kbps";
// Update the value when the slider handle is moved.
mp3Slider.oninput = function () {
    bitrateValue.innerHTML = this.value + " kbps";
}