import ProgressBar from "react-bootstrap/ProgressBar";

function ProgressBarComponent(props) {
  return <ProgressBar now={props.progress} label={`${props.progress}%`} />;
}

export default ProgressBarComponent;
