import store from "../configureStore";
import { useEffect } from "react";
import { useSelector } from "react-redux";

function BitrateSlider(props) {
  useEffect(() => {
    store.dispatch({
      type: "DEFAULT",
      value: props.sliderValue,
    });
  }, []);

  return (
    <div>
      <br />
      <input
        type="range"
        id="bitrate_slider"
        className="slider"
        min={props.min}
        max={props.max}
        value={useSelector((state) => state.sliderBitrate)}
        step={props.step}
        onChange={(e) => {
          store.dispatch({
            type: "CHANGE",
            value: e.target.value,
          });
        }}
      />
      <span>{` ${useSelector((state) => state.sliderBitrate)} kbps`}</span>
    </div>
  );
}

export default BitrateSlider;
