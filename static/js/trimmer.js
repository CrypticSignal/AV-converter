const input = document.getElementById("file_input");
const file_input_label = document.getElementById("file_input_label");
const trim_btn = document.getElementById("trim-btn");

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


function updatePlaceholder() {
    file_input_label.innerText = input.files[0].name;
}

// Run this function when the user clicks on the "Convert" button

function trim() {
    
    if (!input.value) {
        show_alert("No file selected.", "danger")
        return;
    }

    // Create a new FormData instance
    const data = new FormData();

    // Create a XMLHTTPRequest instance
    const request = new XMLHttpRequest();

    // Set the response type
    request.responseType = "json";

    // Clear any existing alerts
    alert_wrapper.innerHTML = "";

    // Get a reference to the file
    const chosen_file = input.files[0];
    
    inputFilename = input.files[0].name;
    const filenameParts = inputFilename.split('.');
    const fileExt = filenameParts[filenameParts.length - 1];

    allowedFiletypes = ["mp3", "aac", "wav", "ogg", "opus", "m4a", "flac", "mka", "wma", "mkv", "mp4", "flv", "wmv","avi", "ac3", "3gp", "MTS", "webm", "ADPCM", "dts", "spx", "caf"]

    if (!allowedFiletypes.includes(fileExt)) {
        show_alert("Incompatible filetype selected.", "danger")
        return;
    }

    // Get a reference to the filesize & set a cookie
    const filesize = chosen_file.size;
    // document.cookie = `filesize=${filesize}`;

    if (filesize > 5000000000) {
        show_alert("The selected file is larger than 5GB; unable to convert.", "danger")
        return;    
    }

    // Disable the input during upload
    input.disabled = true;

    // Hide the upload button
    trim_btn.classList.add("d-none");

    // Show the loading button
    loading_btn.classList.remove("d-none");

    // Show the cancel button
    cancel_btn.classList.remove("d-none");

    // Show the progress bar
    progress_wrapper.classList.remove("d-none");

    // Append the file to the FormData instance
   

    let previousTime = Date.now() / 1000;
    let previousLoaded = 0;
    
    request.upload.addEventListener("progress", function (event) {
        // Get the loaded amount and total filesize (MB)
        const loaded = event.loaded / 10**6;
        const total = event.total / 10**6;
    
        // MB loaded in this interval --> loaded - previousLoaded;
        
        // (Date.now() - previousTime) will give us the time since the last time-interval.
        let speed = ((loaded - previousLoaded) / ((Date.now() / 1000) - previousTime)) * 8;
    
        const percentageComplete = (loaded / total) * 100;

        // Add percentage complete to progress div.
        $('#progress').html(`${Math.floor(percentageComplete)}%`);
        // Add a style attribute to the progress div, i.e. "style=width: x%"
        progress.setAttribute("style", `width: ${Math.floor(percentageComplete)}%`);
        // Show extra info.
        progress_status.innerText = `${loaded.toFixed(2)}MB of ${total.toFixed(2)}MB uploaded
        Upload Speed: ${speed.toFixed(2)}Mbps (${(speed / 8).toFixed(2)}MB/s)`;
    
        // Set the previous value for "loaded" to the current one just before we exit.
        previousLoaded = loaded;
        // Do the same for previousTime.
        previousTime = Date.now() / 1000;
    });

    // Open and send the request
    request.open("POST", "/video-trimmer");
    data.append("request_type", "upload_complete");
    data.append("chosen_file", chosen_file);
    request.send(data);

    cancel_btn.addEventListener("click", function () {
        request.abort();
    })

    // Request load handler (transfer complete)
    request.addEventListener("load", function (e) {

        if (request.status == 200) {
            //show_alert(`${request.response.message}`, "info"); <-- No longer needed as I'm showing a loading button instead.
            document.getElementById('spinner').style.display = 'block'; // Show the converting button.
            trim_file();
        }
         else if (request.status == 415) {
            show_alert('Incompatible filetype selected. Click <a href="http://onlineaudioconverter.net/filetypes" target="_blank">here</a> to see the list of compatible filetypes.', "danger");
        }
        else {
            show_alert("Error uploading file.", "danger");
        }
        reset();
    });

    // Request error handler
    request.addEventListener("error", function (e) {
        reset();
        show_alert(`${request.response.message}`, "danger");
    });

    // Request abort handler
    request.addEventListener("abort", function (e) {

        reset();

        show_alert(`Upload cancelled`, "primary");

    });
 
} // Closing bracket for trim function.

function trim_file() {

    inputFilename = input.files[0].name;
    let startTime = document.getElementById('start-time').value;
    let endTime = document.getElementById('end-time').value;
    if (startTime.length == 5) { 
        startTime += ':00';
    }
    if (endTime.length == 5){
        endTime += ':00'
    }

     // Create a new FormData instance
    const data = new FormData();

     // Create a XMLHTTPRequest instance
    const request = new XMLHttpRequest();
    request.responseType = "json";

    data.append("request_type", "trim");
    data.append("filename", inputFilename);
    data.append("start_time", startTime);
    data.append("end_time", endTime);
    request.open("POST", "/video-trimmer");
    request.send(data);

    request.addEventListener("load", function (e) { // "load" means when the conversionRequest is complete

        alert_wrapper.innerHTML = ""; // Clear any existing alerts.
        document.getElementById('spinner').style.display = 'none'; // Hide the converting msg.

        console.log(request.response)
        console.log("response msg: " + request.response.message)
        console.log("download path: " + request.response.downloadFilePath)

        show_alert(`${request.response.message} <a href="${request.response.downloadFilePath}" download />Click here</a> if the download does not begin automatically.`, "success");

        const link = document.createElement("a"); // Create a virtual link.
        link.download = ''; //The download attribute specifies that the target will be downloaded when a user clicks on the hyperlink. As we have set an empty value, it means use the original filename. This is not needed because as_attachment=True in main.py already specifies that the file will be downloaded.
        link.href = request.response.downloadFilePath;
        link.click();
    });
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
    trim_btn.classList.remove("d-none")
    // Hide the loading button
    loading_btn.classList.add("d-none");
    // Hide the progress bar
    progress_wrapper.classList.add("d-none");
    // Reset the progress bar state
    progress.setAttribute("style", `width: 0%`);
    // Reset the input placeholder
    file_input_label.innerText = "Select file";

}