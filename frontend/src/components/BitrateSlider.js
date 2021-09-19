import { useSelector, useDispatch } from "react-redux";
import { useEffect } from "react";
import { setDefault, change, selectSliderValue } from "../redux/bitrateSliderSlice";

function BitrateSlider(props) {
  const dispatch = useDispatch();
  useEffect(() => {
    dispatch(setDefault(props.initialValue));
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
        value={useSelector(selectSliderValue)}
        step={props.step}
        onChange={(e) => dispatch(change(e.target.value))}
      />
      <span>{` ${useSelector(selectSliderValue)} kbps`}</span>
    </div>
  );
}

export default BitrateSlider;
