const input = document.getElementById("file_input");
const inputLabel = document.getElementById("file_input_label");
const trimButton = document.getElementById("trim-btn");

// This function runs when the user selects a file.
function updatePlaceholder() {
    inputLabel.innerText = input.files[0].name;
}

// Run this function when the user clicks on the "Trim file" button
function upload_and_send_trim_request() {
    
    if (!input.value) {
        show_alert("No file selected.", "danger")
        return;
    }

    alert_wrapper.innerHTML = "";

    const chosenFile = input.files[0];
    const filesize = chosenFile.size;
    const inputFilename = input.files[0].name;
    const filenameParts = inputFilename.split('.');
    const fileExt = filenameParts[filenameParts.length - 1];

    allowedFiletypes = ["mp3", "aac", "wav", "ogg", "opus", "m4a", "flac", "mka", "wma", "mkv", "mp4", "flv", "wmv","avi", "ac3", "3gp", "MTS", "webm", "ADPCM", "dts", "spx", "caf"]

    if (!allowedFiletypes.includes(fileExt)) {
        show_alert("Incompatible filetype selected.", "danger")
        return;
    }
   
    else if (filesize > 5000000000) {
        show_alert("The selected file is larger than 5GB; unable to convert.", "danger")
        return;    
    }

    // First POST request to send the chosen file to the server.
    const request = new XMLHttpRequest();
    request.open("POST", "/trimmer");

    const data = new FormData();
    data.append("request_type", "upload_complete");
    data.append("chosen_file", chosenFile);

    // Disable the input during upload
    input.disabled = true;

    // Hide the upload button
    trimButton.classList.add("d-none");

    // Show the loading button
    loading_btn.classList.remove("d-none");

    // Show the cancel button
    cancel_btn.classList.remove("d-none");

    // Show the progress bar
    progress_wrapper.classList.remove("d-none");

    let previousTime = Date.now() / 1000;
    let previousLoaded = 0;
    
    request.upload.addEventListener("progress", (event) => {

        // Get the uploaded amount and total filesize (MB)
        const loaded = event.loaded / 10**6;
        const total = event.total / 10**6;
    
        // MB loaded in this interval is loaded - previousLoaded and
        // (Date.now() - previousTime) gives us the time since the last time-interval.
        let speed = ((loaded - previousLoaded) / ((Date.now() / 1000) - previousTime)) * 8;
    
        const percentageComplete = (loaded / total) * 100;

        // Add percentage complete to progress div.
        $('#progress').html(`${Math.floor(percentageComplete)}%`);
        // Add a style attribute to the progress div, i.e. "style=width: x%"
        progress.setAttribute("style", `width: ${Math.floor(percentageComplete)}%`);
        // Show extra info.
        progress_status.innerText = `${loaded.toFixed(2)}MB of ${total.toFixed(2)}MB uploaded
        Upload Speed: ${speed.toFixed(2)}Mbps (${(speed / 8).toFixed(2)}MB/s)`;
    
        previousLoaded = loaded;
        previousTime = Date.now() / 1000;
    });

    cancel_btn.addEventListener("click", () => request.abort());

    // Send the request.
    request.send(data);

    // Upload complete
    request.addEventListener("load", () => {

        if (request.status == 200) {
            send_trim_request();
        }
        else if (request.status == 415) {
            show_alert('Incompatible filetype selected. Click <a href="https://freeaudioconverter.net/filetypes" target="_blank">here</a> to see the list of compatible filetypes.', "danger");
        }
        else {
            show_alert("Error uploading file.", "danger");
        }
        reset();
    });

    // Request error handler
    request.addEventListener("error", () => {
        reset();
        show_alert(`${request.response.message}`, "danger");
    });

    // Request abort handler
    request.addEventListener("abort", () => {
        reset();
        show_alert("Upload cancelled", "primary");
    });
 
} // Closing bracket for upload_and_trim function.

// Runs when upload is complete and 200 status received from server.
function send_trim_request() {

    inputFilename = input.files[0].name;

    let startTime = document.getElementById('start-time').value;
    let endTime = document.getElementById('end-time').value;
    
    if (startTime.length == 5) { 
        startTime += ':00';
    }
    if (endTime.length == 5){
        endTime += ':00'
    }

    // Second POST request to give the server the data it needs to trim the file.
    const request = new XMLHttpRequest();
    request.open("POST", "/trimmer");
    
    const data = new FormData();
    data.append("request_type", "trim");
    data.append("filename", inputFilename);
    data.append("start_time", startTime);
    data.append("end_time", endTime);

    request.send(data);

    request.addEventListener("load", () => {

        if (request.status !== 200) {
            console.log(request.responseText);
            show_alert(request.responseText, 'danger');
            return;
        }
        else {
            console.log(request.response.downloadFilePath);
            alert_wrapper.innerHTML = ""; // Clear any existing alerts.
            document.getElementById('spinner').style.display = 'none'; // Hide the converting msg.
            show_alert(`File trimmed. <a href="${request.responseText}" download />Click here</a> if the download does not begin automatically.`, "success");
            const link = document.createElement("a"); // Create a virtual link.
            //link.download = ''; //The download attribute specifies that the target will be downloaded when a user clicks on the hyperlink. As we have set an empty value, it means use the original filename.
            link.href = request.responseText;
            link.click();
        }
    });
}

// Function to show alerts
function show_alert(message, type) {
    alert_wrapper.innerHTML =
    `<div id="alert" class="alert alert-${type} alert-dismissible fade show" role="alert">
      <span>${message}</span>
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>`
}

// Function to reset the page
function reset() {
    // Clear the input
    input.value = null;
    // Hide the cancel button
    cancel_btn.classList.add("d-none");
    // Reset the input element
    input.disabled = false;
    // Show the upload button
    trimButton.classList.remove("d-none")
    // Hide the loading button
    loading_btn.classList.add("d-none");
    // Hide the progress bar
    progress_wrapper.classList.add("d-none");
    // Reset the progress bar state
    progress.setAttribute("style", `width: 0%`);
    // Reset the input placeholder
    inputLabel.innerText = "Select file";
}