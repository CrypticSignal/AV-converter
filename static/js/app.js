const input = document.getElementById("file_input");
const file_input_label = document.getElementById("file_input_label");
const outputNameBox = document.getElementById("output_name");
const progress = document.getElementById("progress");
const progress_wrapper = document.getElementById("progress_wrapper");
const progress_status = document.getElementById("progress_status");
const upload_btn = document.getElementById("upload_btn");
const loading_btn = document.getElementById("loading_btn");
const cancel_btn = document.getElementById("cancel_btn");
const alert_wrapper = document.getElementById("alert_wrapper");

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

// Show the file selected and enter a default output name.
function updateBoxes() {

    file_input_label.innerText = input.files[0].name; // Show name of selected file.

    inputFilename = input.files[0].name; // Filename of the selected file.

    removePercentageSign = inputFilename.replace(/%/g, ''); // Remove percentage sign(s) as this causes an issue due to secure_filename?

    inputFilenameFormatted = removePercentageSign.replace(/_/g, ' '); // Replace the underscores with spaces, to make the filename look more aesthetically pleasing.

    defaultOutputName = inputFilenameFormatted.substring(0, inputFilenameFormatted.lastIndexOf('.')); // Get the filename without the extension by only getting the part before the last "."

    outputNameBox.value = defaultOutputName; // Put the formatted filename into the textbox.
}


// Run this function when the user clicks on the "Convert" button.
function upload_and_convert() {

    if (outputNameBox.value.includes('"') || outputNameBox.value.includes('/') || outputNameBox.value.includes('?') || outputNameBox.value.includes('*') || outputNameBox.value.includes('>') || outputNameBox.value.includes('<') || outputNameBox.value.includes('|') || outputNameBox.value.includes(':') || outputNameBox.value.includes(';') || outputNameBox.value.includes('&&')) {
        show_alert('Output name cannot contain any of the following characters: "/?*><|:', "danger");
        return;
    }

    // Show an error if no filename selected or if filename input is empty.
    if (!input.value && document.getElementById("output_name").value == '') {
        show_alert("Perhaps in the future a website will be able to read your mind and automatically complete the required fields, but technology hasn't gotten that far yet.", "info")
        return;
    }

    else if (!input.value) {
        show_alert("No file selected.", "danger")
        return;
    }

    else if (document.getElementById("output_name").value == '') {
        show_alert("You must enter your desired filename.", "danger")
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

    // Name of uploaded file
    const filename = chosen_file.name;

    const filenameParts = filename.split('.');
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
    upload_btn.classList.add("d-none");

    // Show the loading button
    loading_btn.classList.remove("d-none");

    // Show the cancel button
    cancel_btn.classList.remove("d-none");

    // Show the progress bar
    progress_wrapper.classList.remove("d-none");

    // Append the file to the FormData instance
    data.append("chosen_file", chosen_file);

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
    request.open("POST", "/");
    data.append("requestType", "uploaded");
    request.send(data);

    cancel_btn.addEventListener("click", function () {
        request.abort();
    })

    // Request load handler (transfer complete)
    request.addEventListener("load", function (e) {

        if (request.status == 200) {
            //show_alert(`${request.response.message}`, "info"); <-- No longer needed as I'm showing a loading button instead.
            document.getElementById('spinner').style.display = 'block'; // Show the converting button.
            convert_file(chosen_file.name);
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
    request.addEventListener("error", function (e) {
        reset();
        show_alert(`${request.response.message}`, "danger");
    });

    // Request abort handler
    request.addEventListener("abort", function (e) {

        reset();

        show_alert(`Upload cancelled`, "primary");

    });
 
} // Closing bracket for upload function.

function convert_file(filename) {

    const chosenCodec = document.getElementById('codecs').value;
    const sliderValue = document.getElementById("slider").value;
    const outputName = document.getElementById("output_name").value;
    const mp3EncodingType = document.getElementById('mp3_encoding_type').value;
    const cbr_abr_Bitrate = document.getElementById('cbr_abr_bitrate').value; 
    const vbrSettingMP3 = document.getElementById('mp3_vbr_setting').value;
    const isYswitch = document.querySelector('input[name="is-y-switch"]:checked').value;
    const ac3Bitrate = document.getElementById('ac3-bitrate').value;
    const vorbisQuality = document.getElementById('vorbis_quality').value
    const vorbisEncoding = document.getElementById('vorbis_encoding').value;
    const flacCompression = document.getElementById('flac_compression').value;
    const fdkType = document.getElementById('fdk_encoding').value;
    const fdkCBR = document.getElementById('fdk-slider-aac').value;
    const fdkVBR = document.getElementById('fdk-vbr-value').value;
    const isFDKLowpass = document.querySelector('input[name="is-lowpass"]:checked').value;
    const FDKLowpass = document.getElementById('fdk-lowpass').value;
    const dtsBitrate = document.getElementById('dts-slider').value;
    const opusBitrate = document.getElementById('opus_cbr_slider').value;
    const opusEncodingType = document.getElementById('opus-encoding-type').value;
    const isDownmix = document.querySelector('input[name="is-downmix"]:checked').value;

    
    const conversionRequest = new XMLHttpRequest();
    conversionRequest.responseType = "json";

    // Create a new FormData instance
    const data = new FormData();

    data.append("requestType", "convert");
    data.append("file_name", filename);
    data.append("chosen_codec", chosenCodec);
    data.append("slider_value", sliderValue);
    data.append("output_name", outputName);
    data.append("mp3_encoding_type", mp3EncodingType);
    data.append("cbr_abr_bitrate", cbr_abr_Bitrate);
    data.append("mp3_vbr_setting", vbrSettingMP3);
    data.append("ac3_bitrate", ac3Bitrate);
    data.append("vorbis_quality", vorbisQuality);
    data.append("vorbis_encoding", vorbisEncoding);
    data.append("flac_compression", flacCompression);
    data.append("is_downmix", isDownmix);
    data.append("fdk_type", fdkType);
    data.append("fdk_cbr", fdkCBR);
    data.append("fdk_vbr", fdkVBR);
    data.append("is_fdk_lowpass", isFDKLowpass);
    data.append("fdk_lowpass", FDKLowpass);
    data.append("dts_bitrate", dtsBitrate);
    data.append("opus-cbr-bitrate", opusBitrate);
    data.append("opus-encoding-type", opusEncodingType);
    data.append("is_y_switch", isYswitch);

    // Open the request and send the required data to main.py so the conversion can happen.
    conversionRequest.open('POST', '/');
    conversionRequest.send(data);

    conversionRequest.addEventListener("load", function (e) { // "load" means when the conversionRequest is complete

        alert_wrapper.innerHTML = ""; // Clear any existing alerts.
        document.getElementById('spinner').style.display = 'none'; // Hide the converting msg.

        show_alert(`${conversionRequest.response.message} <a href="${conversionRequest.response.downloadFilePath}" download />Click here</a> if the download does not begin automatically.`, "success");

        const link = document.createElement("a"); // Create a virtual link.
        link.download = ''; //The download attribute specifies that the target will be downloaded when a user clicks on the hyperlink. As we have set an empty value, it means use the original filename.
        link.href = conversionRequest.response.downloadFilePath;
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
    upload_btn.classList.remove("d-none")
    // Hide the loading button
    loading_btn.classList.add("d-none");
    // Hide the progress bar
    progress_wrapper.classList.add("d-none");
    // Reset the progress bar state
    progress.setAttribute("style", `width: 0%`);
    // Reset the input placeholder
    file_input_label.innerText = "Select file";
    // Clear the output filename box.
    outputNameBox.value = ''
}