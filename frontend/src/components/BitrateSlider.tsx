import { useSelector, useDispatch } from "react-redux";
import React, { useEffect } from "react";
import { setDefault, change, selectSliderValue } from "../redux/bitrateSliderSlice";

interface BitrateSliderProps {
  initialValue: string;
  min: string;
  max: string;
  step: string;
}

const BitrateSlider: React.FC<BitrateSliderProps> = ({ initialValue, min, max, step }) => {
  const dispatch = useDispatch();
  useEffect(() => {
    dispatch(setDefault(initialValue));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div>
      <br />
      <input
        type="range"
        id="bitrate_slider"
        className="slider"
        min={min}
        max={max}
        value={useSelector(selectSliderValue)}
        step={step}
        onChange={(e) => dispatch(change(e.target.value))}
      />
      <span>{` ${useSelector(selectSliderValue)} kbps`}</span>
    </div>
  );
};

export default BitrateSlider;
