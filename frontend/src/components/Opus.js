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
        If the audio is mono, selecting a bitrate above 256 kbps will result in an unsuccessful
        conversion as Opus only supports up to 256 kbps per channel.
      </i>
    </div>
  );
}

export default Opus;
