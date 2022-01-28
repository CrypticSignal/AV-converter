import showAlert from "./showAlert";
const axios = require("axios");

// A function that creates a synchronous sleep.
function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

let shouldLog = true;

async function showDownloadProgress(progressFilePath) {
  while (shouldLog) {
    await sleep(500);
    const response = await fetch(`/api/progress/${progressFilePath}`);
    if (response.ok) {
      const ytdlpOutput = await response.text();
      if (ytdlpOutput !== "" && !ytdlpOutput.includes("pass -k to keep")) {
        const lines = ytdlpOutput.split("\n");
        const mostRecentOutput = lines[lines.length - 2];
        showAlert(mostRecentOutput, "info");
        console.log(mostRecentOutput);
      }
    }
  }
}

// This function runs when one of the download buttons is clicked.
async function buttonClicked(url, whichButton) {
  console.clear();
  const linkBox = document.getElementById("link");
  if (linkBox.value === "") {
    showAlert("Trying to download something without pasting the URL? You silly billy.", "warning");
    return;
  }

  showAlert("Initialising...", "warning");

  const progressFilename = `${Date.now()}.txt`;
  shouldLog = true;
  showDownloadProgress(progressFilename);

  const response = await axios({
    url: "/api/yt",
    method: "POST",
    data: {
      link: url,
      buttonClicked: whichButton,
      progressFilename: progressFilename,
    },
    responseType: "blob",
    onDownloadProgress: (progressEvent) => {
      const loaded = progressEvent.loaded;
      const total = progressEvent.total;
      const percentageProgress = ((loaded / total) * 100).toFixed(1);
      showAlert(`Sent ${percentageProgress}% of the file to your browser...`, "info");
    },
  });

  shouldLog = false;

  if (response.status === 200) {
    const filename = response.headers["content-disposition"]
      .replace('attachment; filename="', "")
      .replace('"', "");
    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    link.click();
    showAlert("File downloaded :)", "success");
    //Sometimes the alert below didn't show up, adding a delay seems to fix this.
    //await sleep(1000);
    return;
  } else {
    const error = await response.text();
    showAlert(error, "danger");
    console.log(error);
    return;
  }
}

export default buttonClicked;
