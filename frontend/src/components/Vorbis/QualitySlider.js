function QualitySlider(props) {
  return (
    <div id="vorbis_quality_div">
      <p>Set your desired quality setting via the slider:</p>
      <input
        type="range"
        className="slider"
        min={0}
        max={10}
        step={1}
        onChange={props.onSliderMoved}
        value={props.qValue}
      />
      <span>{` -q${props.qValue}`}</span>
      <br />
      <i>
        Quality range is from "-q 0" (lowest) to "-q 10" (highest). For more details, click{" "}
        <a
          target="_blank"
          rel="noreferrer"
          href="https://wiki.hydrogenaud.io/index.php?title=Recommended_Ogg_Vorbis#Recommended_Encoder_Settings"
        >
          here
        </a>
        .
      </i>
    </div>
  );
}

export default QualitySlider;
