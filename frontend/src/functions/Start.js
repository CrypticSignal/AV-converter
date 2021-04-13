import showAlert from "./ShowAlert";
import reset from "./Reset";
import showUploadProgress from "./ShowUploadProgress";
import getProgressFilename from "./GetProgressFilename";

function showError(progressFilenameRequest) {
  showAlert(`${progressFilenameRequest.responseText}`, "danger");
  console.log(
    `progressFilenameRequest error: ${progressFilenameRequest.responseText}`
  );
  reset();
}

function abortUpload(progressFilenameRequest) {
  progressFilenameRequest.abort();
  showAlert("Upload cancelled", "info");
  reset();
}

function start(state) {
  const input = document.getElementById("file_input");
  const outputNameBox = document.getElementById("output_name");
  // Show an alert if a file hasn't been selected or the URL input box is empty.
  if (!input.value && !outputNameBox.value) {
    showAlert(
      "It helps if you select the file that you want to convert.",
      "warning"
    );
    return;
  }
  // If a file has been selected.
  else if (input.value) {
    const inputFile = input.files[0];
    const inputFilename = inputFile.name;
    const filenameParts = inputFilename.split(".");
    const fileExt = filenameParts[filenameParts.length - 1];
    const filesizeMB = (inputFile.size / 1000000).toFixed(2).toString();
    const filesize = inputFile.size;

    const allowedFiletypes = [
      "mp3",
      "aac",
      "wav",
      "ogg",
      "opus",
      "m4a",
      "flac",
      "mka",
      "wma",
      "mkv",
      "mp4",
      "flv",
      "wmv",
      "avi",
      "ac3",
      "3gp",
      "MTS",
      "webm",
      "adpcm",
      "dts",
      "spx",
      "caf",
      "mov",
      "thd",
      "dtshd",
      "aif",
      "aiff",
      "vob",
    ];

    // Show an alert if an incompatible filetype has been selected.
    if (!allowedFiletypes.includes(fileExt)) {
      showAlert(
        'Incompatible filetype selected. Click <a href="/filetypes" \
            target="_blank">here</a> to see the list of compatible filetypes.',
        "danger"
      );
      reset();
      return;
    }
    // Show an alert if the filesize exceeds the maximum size allowed.
    else if (filesize > 3 * 10 ** 9) {
      showAlert("Max file size: 3 GB", "danger");
      reset();
      return;
    }
    // Show an alert if a disallowed character has been entered in the output name box.
    else if (
      outputNameBox.value.includes('"') ||
      outputNameBox.value.includes("/") ||
      outputNameBox.value.includes("\\") ||
      outputNameBox.value.includes("?") ||
      outputNameBox.value.includes("*") ||
      outputNameBox.value.includes(">") ||
      outputNameBox.value.includes("<") ||
      outputNameBox.value.includes("|") ||
      outputNameBox.value.includes(":") ||
      outputNameBox.value.includes(";") ||
      outputNameBox.value.includes("&&") ||
      outputNameBox.value.includes("command") ||
      outputNameBox.value.includes("$") ||
      outputNameBox.value.includes(".")
    ) {
      showAlert(
        'Characters not allowed: ., ", /, ?, *, >, <, |, :, $ or the word "command"',
        "danger"
      );
      return;
    }
    // Show an alert if output name box is empty.
    else if (document.getElementById("output_name").value == "") {
      showAlert("You must enter your desired filename.", "danger");
      return;
    }

    document.getElementById("alert_wrapper").style.display = "none";
    input.disabled = true;
    outputNameBox.disabled = true;
    const cancelButton = document.getElementById("convert_btn");
    cancelButton.classList.add("d-none");
    document.getElementById("uploading_btn").classList.remove("d-none");
    document.getElementById("cancel_btn").classList.remove("d-none");
    const progressWrapper = document.getElementById("progress_wrapper");
    progressWrapper.classList.remove("d-none");
    progressWrapper.style.display = "block";

    // The convesion progress will be written to a .txt file. This request will receive the name of the .txt file
    const progressFilenameRequest = new XMLHttpRequest();

    progressFilenameRequest.upload.addEventListener(
      "progress",
      showUploadProgress
    );
    progressFilenameRequest.addEventListener("load", () =>
      getProgressFilename(progressFilenameRequest, inputFilename, state)
    );
    progressFilenameRequest.addEventListener("error", () =>
      showError(progressFilenameRequest)
    );
    cancelButton.addEventListener("click", () =>
      abortUpload(progressFilenameRequest)
    );

    const data = new FormData();
    data.append("request_type", "uploaded");
    data.append("chosen_file", inputFile);
    data.append("filesize", filesizeMB);

    progressFilenameRequest.open("POST", "/api");
    progressFilenameRequest.send(data);
  } else {
    showAlert("No file selected.", "danger");
    return;
  }
}

export default start;
