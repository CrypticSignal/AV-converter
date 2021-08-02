import ProgressBar from "react-bootstrap/ProgressBar";
import store from "../app/store";

function ProgressBar() {
  return (
    <div id="progress_wrapper" style={{ display: "none" }}>
      <br />
      <ProgressBar
        now={store.getState().progress.progress}
        label={`${store.getState().progress.progress}%`}
      />
      ;
      <label id="progress_status" />
    </div>
  );
}

export default ProgressBar;
