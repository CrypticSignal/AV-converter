import showAlert from "./ShowAlert";
import reset from "./Reset";
import showUploadProgress from "./ShowUploadProgress";
import getProgressFilename from "./GetProgressFilename";

function showError(progressFilenameRequest) {
  showAlert(`${progressFilenameRequest.responseText}`, "danger");
  console.log(`progressFilenameRequest error: ${progressFilenameRequest.responseText}`);
  reset();
}

function abortUpload(progressFilenameRequest) {
  progressFilenameRequest.abort();
  reset();
}

function start(state) {
  const input = document.getElementById("file_input");
  const outputNameBox = document.getElementById("output_name");

  if (!input.value) {
    showAlert("No file selected.", "danger");
    return;
  }

  if (!outputNameBox.value) {
    showAlert("You must enter your desired output filename.", "danger");
    return;
  }

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
  if (filesize > 3 * 10 ** 9) {
    showAlert("Max file size: 3 GB", "danger");
    reset();
    return;
  }

  document.getElementById("convert_btn").style.display = "none";
  document.getElementById("alert_wrapper").style.display = "none";
  document.getElementById("uploading_div").style.display = "block";

  input.disabled = true;
  outputNameBox.disabled = true;

  const cancelButton = document.getElementById("cancel_btn");
  cancelButton.style.display = "block";
  cancelButton.addEventListener("click", () => abortUpload(progressFilenameRequest));

  document.getElementById("upload_progress").style.display = "block";

  // The convesion progress will be written to a txt file. This request will receive the name of the txt file.
  const progressFilenameRequest = new XMLHttpRequest();

  // While the file is uploading.
  progressFilenameRequest.upload.addEventListener("progress", showUploadProgress);
  // When the file has finished uploading.
  progressFilenameRequest.addEventListener("load", () =>
    getProgressFilename(progressFilenameRequest, inputFilename, state)
  );
  // If there is an error.
  progressFilenameRequest.addEventListener("error", () => showError(progressFilenameRequest));

  const data = new FormData();
  data.append("uploadedFile", inputFile);
  data.append("filesize", filesizeMB);

  progressFilenameRequest.open("POST", "/api");
  progressFilenameRequest.send(data);
}

export default start;
