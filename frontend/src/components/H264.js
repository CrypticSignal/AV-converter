import NumberInput from "./NumberInput";

function H264(props) {
  return (
    <div id="video">
      <label htmlFor="video_container">Output Container: </label>
      <select
        id="video_container"
        onChange={props.onVideoContainerChange}
        value={props.videoContainer}
      >
        <option value="mp4">MP4 (.mp4)</option>
        <option value="mkv">MKV (.mkv)</option>
      </select>
      <div id="should_transcode">
        <div className="form-check">
          <label className="form-check-label">
            <input
              type="radio"
              onChange={props.onTranscodeVideoChange}
              className="form-check-input"
              value="yes"
              checked={props.transcodeVideo === "yes"}
            />
            Change the video codec to H.264/AVC
          </label>
        </div>
        <div className="form-check">
          <label className="form-check-label">
            <input
              type="radio"
              onChange={props.onTranscodeVideoChange}
              className="form-check-input"
              value="no"
              checked={props.transcodeVideo === "no"}
            />
            Don't transcode the video but change the format to {props.videoContainer.toUpperCase()}
          </label>
        </div>
      </div>
      <input
        type="checkbox"
        onChange={props.onTranscodeAudioCheckbox}
        checked={props.transcodeVideosAudio ? "checked" : ""}
      />{" "}
      <label>Transcode the audio to AAC</label>
      <br />
      <i style={{ display: props.transcodeVideosAudio ? "block" : "none" }}>
        FDK AAC at{" "}
        <a
          rel="noreferrer"
          href="https://wiki.hydrogenaud.io/index.php?title=Fraunhofer_FDK_AAC#Bitrate_Modes"
          target="_blank"
        >
          VBR mode 5
        </a>{" "}
        will be used.
      </i>
      <div
        id="video_encoding_type"
        style={{ display: props.transcodeVideo === "yes" ? "block" : "none" }}
      >
        <br />
        <label htmlFor="video_encoding_type">Encoding Type:</label>
        <select onChange={props.onVideoEncodingTypeChange} value={props.videoEncodingType}>
          <option value="crf">CRF (constant quality)</option>
          {/* <option value="filesize">Target a filesize</option> */}
          <option value="bitrate">Target a bitrate (Mbps)</option>
        </select>
      </div>
      <div
        id="x264_preset_div"
        style={{ display: props.transcodeVideo === "yes" ? "block" : "none" }}
      >
        <label htmlFor="x264_preset">x264 preset:</label>
        <select onChange={props.onX264PresetChange} value={props.x264Preset}>
          <option value="veryslow">veryslow</option>
          <option value="slower">slower</option>
          <option value="slow">slow</option>
          <option value="medium">medium</option>
          <option value="fast">fast</option>
          <option value="faster">faster</option>
          <option value="veryfast">veryfast</option>
          <option value="superfast">superfast</option>
          <option value="ultrafast">ultrafast</option>
        </select>
      </div>
      <div
        id="target_bitrate_div"
        style={{ display: props.videoEncodingType === "bitrate" ? "block" : "none" }}
      >
        <NumberInput
          onChange={props.onVideoBitrateChange}
          value={props.videoBitrate}
          units="Mbps"
        />
      </div>
      {/* <div
        id="target_filesize_div"
        style={{ display: props.videoEncodingType === "filesize" ? "block" : "none" }}
      >
        <NumberInput
          onChange={props.onVideoFilesizeChange}
          value={props.videoFilesize}
          units="MB"
        />
      </div> */}
      <div id="crf_div" style={{ display: props.videoEncodingType === "crf" ? "block" : "none" }}>
        <strong>Constant Rate Factor (CRF)</strong>
        <br />
        <input
          type="range"
          className="slider"
          onChange={props.onCrfChange}
          min={0}
          max={51}
          step={1}
          value={props.crfValue}
        />
        <span id="crf_value" />
        {` ${props.crfValue}`}
        <br />
        <i>
          A lower CRF means higher video quality, at the expense of a larger file size. A CRF of 17
          or 18 is considered to be visually lossless or nearly so. More details{" "}
          <a href="https://trac.ffmpeg.org/wiki/Encode/H.264#crf" target="_blank" rel="noreferrer">
            here
          </a>
          .
        </i>
      </div>
    </div>
  );
}

export default H264;
