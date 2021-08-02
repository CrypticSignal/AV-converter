import { useSelector, useDispatch } from "react-redux";
import { useEffect } from "react";
import { setDefault, change } from "../redux/bitrateSliderSlice";

function BitrateSlider(props) {
  const { bitrate } = useSelector((state) => state.bitrate);
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(setDefault("192"));
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
        value={bitrate}
        step={props.step}
        onChange={(e) => dispatch(change(e.target.value))}
      />
      <span>{` ${bitrate} kbps`}</span>
    </div>
  );
}

export default BitrateSlider;
