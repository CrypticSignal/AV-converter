function FLAC(props) {
  return (
    <div id="flac">
      <p>Set your desired compression level via the slider:</p>
      <input
        className="slider"
        type="range"
        onChange={props.onFlacCompressionChange}
        min={0}
        max={12}
        step={1}
        defaultValue={5}
        value={props.flacCompression}
      />
      <span id="flac_value" />
      {` ${props.flacCompression}`}
      <br />
      <i>A higher value means a slighter smaller file size, but a longer conversion time.</i>
    </div>
  );
}

export default FLAC;
