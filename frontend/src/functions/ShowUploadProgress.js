import { update } from "../redux/uploadProgressSlice";
import store from "../app/store";

let previousTime = Date.now() / 1000;
let previousLoaded = 0;
let previousPercentageComplete = 0;

function showUploadProgress(event) {
  const loaded = event.loaded / 10 ** 6;
  const total = event.total / 10 ** 6;
  const percentageComplete = Math.floor((loaded / total) * 100);
  //store.dispatch(update(percentageComplete));

  const progressBar = document.getElementById("progress_bar");
  // Add a style attribute to the progress div, i.e. style="width: x%"
  progressBar.setAttribute("style", `width: ${percentageComplete}%`);

  const progressStatus = document.getElementById("progress_status");
  progressStatus.innerHTML = `${Math.floor(percentageComplete)}%`;

  // MB loaded in this interval is (loaded - previousLoaded) and
  // ((Date.now() / 1000) - previousTime) will give us the time since the last time interval.
  const speed = (loaded - previousLoaded) / (Date.now() / 1000 - previousTime);

  const completionTimeSeconds = (total - loaded) / speed;
  const hours = (Math.floor(completionTimeSeconds / 3600) % 60).toString().padStart(2, "0");
  const minutes = (Math.floor(completionTimeSeconds / 60) % 60).toString().padStart(2, "0");
  const seconds = Math.ceil(completionTimeSeconds % 60)
    .toString()
    .padStart(2, "0");
  const completionTime = `${hours}:${minutes}:${seconds}`;

  progressStatus.innerText = `${loaded.toFixed(1)} MB of ${total.toFixed(1)} MB uploaded
    Upload Speed: ${(speed * 8).toFixed(1)} Mbps (${speed.toFixed(1)} MB/s)
    Upload will complete in ${completionTime} [HH:MM:SS]`;

  previousLoaded = loaded;
  previousTime = Date.now() / 1000;
  previousPercentageComplete = percentageComplete;
}

export default showUploadProgress;
