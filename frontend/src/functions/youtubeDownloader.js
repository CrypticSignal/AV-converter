import showAlert from "./showAlert";

// A function that creates a synchronous sleep.
function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

let shouldLog = false;

async function showDownloadProgress(progressFilePath) {
  while (shouldLog) {
    await sleep(500);
    const response = await fetch(progressFilePath);
    if (response.ok) {
      const ytdlpOutput = await response.text();
      if (ytdlpOutput !== "") {
        showAlert(ytdlpOutput, "info");
        console.log(ytdlpOutput);
      }
    }
  }
}

// This function runs when one of the download buttons is clicked.
async function buttonClicked(url, whichButton) {
  const linkBox = document.getElementById("link");
  if (linkBox.value === "") {
    showAlert("Trying to download something without pasting the URL? You silly billy.", "warning");
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

    if (secondRequest.status === 200) {
      const response = await secondRequest.text();
      console.log(response);
      const anchorTag = document.createElement("a");
      anchorTag.setAttribute("download", "");
      anchorTag.href = response;
      anchorTag.click();
      // Sometimes the alert below didn't show up, adding a delay seems to fix this.
      await sleep(1000);
      showAlert("Your browser should have started downloading the file.", "success");
    } else {
      const error = await secondRequest.text();
      showAlert(error, "danger");
      return;
    }
  }
}

export default buttonClicked;
