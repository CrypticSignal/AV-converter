import showAlert from "./ShowAlert";

// A function that creates a synchronous sleep.
function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

let shouldLog = false;
// This needs to be a "var" variable so that it can be set to "true" in the showDownloadProgress function.
var is_downloading_audio = false;

async function showDownloadProgress(progressFilePath) {
  while (shouldLog) {
    await sleep(250);
    const response = await fetch(progressFilePath);
    if (response.ok) {
      const textInFile = await response.text();
      const lines = textInFile.split("\n");
      const lastLine = lines[lines.length - 2];
      if (is_downloading_audio) {
        if (lastLine.includes("[download]")) {
          showAlert(lastLine.replace("[download]", "[audio]"), "info");
        } else if (lastLine.includes("[ffmpeg] Merging")) {
          showAlert("Merging the audio and video...", "info");
        }
      } else {
        if (
          textInFile.includes(".m4a") &&
          !textInFile.includes("pass -k to keep")
        ) {
          is_downloading_audio = true;
        } else if (lastLine.includes("[download]")) {
          showAlert(lastLine.substring(11), "info");
        } else if (lastLine.includes(".mp3")) {
          showAlert("Converting to MP3...", "info");
        } else if (lastLine.includes("[ffmpeg] Merging")) {
          showAlert("Merging the audio and video...", "info");
        } else if (lastLine.includes("Deleting original file ")) {
          showAlert("Your file is almost ready...", "info");
        }
      }
    }
  }
}

// This function runs when one of the download buttons is clicked.
async function buttonClicked(url, whichButton) {
  const linkBox = document.getElementById("link");
  if (linkBox.value == "") {
    showAlert(
      "Trying to download something without pasting the URL? You silly billy.",
      "warning"
    );
    return;
  }

  showAlert("Initialising...", "warning");

  const firstFormData = new FormData();
  firstFormData.append("button_clicked", "yes");

  // 1st POST request to get the path of the progress file.
  const requestProgressPath = await fetch("/api/yt", {
    method: "POST",
    body: firstFormData,
  });

  if (!requestProgressPath.ok) {
    const error = await requestProgressPath.text();
    showAlert(error, "danger");
    console.log(error);
    return;
  } else {
    let progressFilePath = await requestProgressPath.text();
    progressFilePath = `api/${progressFilePath}`;
    console.log(`https://free-av-tools.com/${progressFilePath}`);
    const secondFormData = new FormData();
    secondFormData.append("link", url);
    secondFormData.append("button_clicked", whichButton);

    shouldLog = true;
    showDownloadProgress(progressFilePath);

    // 2nd POST request to get the download link.
    const secondRequest = await fetch("/api/yt", {
      method: "POST",
      body: secondFormData,
    });

    shouldLog = false;
    is_downloading_audio = false;

    if (secondRequest.status == 200) {
      const response = await secondRequest.text();
      const anchorTag = document.createElement("a");
      anchorTag.href = response;
      anchorTag.download = "";
      anchorTag.click();
      // Sometimes the alert below didn't show up, adding a delay seems to fix this.
      await sleep(1000);
      showAlert(
        "Your browser should have started downloading the file.",
        "success"
      );
    } else {
      const error = await secondRequest.text();
      showAlert(error, "danger");
      return;
    }
  }
}

export default buttonClicked;
