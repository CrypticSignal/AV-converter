import showAlert from "./showAlert";
const axios = require("axios");

// A function that creates a synchronous sleep.
const sleep = (milliseconds: number) => {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
};

let shouldLog = false;

const showDownloadProgress = async (progressFilename: string) => {
  while (shouldLog) {
    await sleep(500);
    const response = await axios(`/api/${progressFilename}`);
    if (response.status === 200) {
      const ytdlpOutput = response.data;
      if (ytdlpOutput.includes("[ExtractAudio]") && ytdlpOutput.includes(".mp3")) {
        showAlert("Converting to MP3...", "info");
      } else if (ytdlpOutput && !ytdlpOutput.includes("pass -k to keep")) {
        showAlert(ytdlpOutput, "info");
        console.log(ytdlpOutput);
      }
    }
  }
};

// This function runs when one of the download buttons is clicked.
export const sendDownloadRequest = async (url: string, whichButton: string) => {
  console.clear();
  const linkBox = document.getElementById("link") as HTMLInputElement;
  if (linkBox.value === "") {
    showAlert("Trying to download something without pasting the URL? You silly billy.", "warning");
    return;
  }

  showAlert("Initialising...", "warning");

  const progressFilename = `${Date.now()}.txt`;
  shouldLog = true;
  showDownloadProgress(progressFilename);

  try {
    const response = await axios({
      url: "/api/download",
      method: "POST",
      data: {
        link: url,
        buttonClicked: whichButton,
        progressFilename: progressFilename,
      },
      responseType: "blob",
      onDownloadProgress: (progressEvent: any) => {
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

      const anchorTag = document.createElement("a");
      const objectURL = window.URL.createObjectURL(response.data);
      anchorTag.href = objectURL;
      anchorTag.setAttribute("download", filename);
      anchorTag.click();
      window.URL.revokeObjectURL(objectURL);
      showAlert("File downloaded :)", "success");
    }
  } catch (err: any) {
    showAlert(err, "danger");
    console.log(err);
    return;
  }
};
