import BitrateSlider from "./BitrateSlider";

function Opus(props) {
  return (
    <div id="Opus">
      <label htmlFor="opus_encoding_type">Encoding Type</label>
      <select onChange={props.onOpusTypeChange} value={props.opusType}>
        <option disabled value>
          Select Encoding Type
        </option>
        <option value="vbr">VBR (with a target bitrate)</option>
        <option value="cbr">CBR (Constant Bitrate)</option>
      </select>
      <BitrateSlider
        onBitrateSliderMoved={props.onBitrateSliderMoved}
        sliderValue={props.sliderValue}
        min="16"
        max="512"
        step="16"
      />
      <i>
        If your file contains a mono audio stream, the bitrate will be capped at 256 kbps as Opus
        does not support more than 256 kbps per channel.
      </i>
    </div>
  );
}

export default Opus;
