function MKVMP4(props) {
  return (
    <div id="video">
      <select id="video_mode" onChange={props.onVideoSettingChange} value={props.videoSetting}>
        <option value="keep_codecs">[1] -c copy</option>
        <option value="keep_video_codec">[2] -c:v copy -c:a libfdk_aac</option>
        <option value="convert_video_keep_audio">[3] -c:v libx264 -c:a copy</option>
        <option disabled>Or choose an x264 preset:</option>
        <option value="ultrafast">[4] -preset ultrafast</option>
        <option value="superfast">[5] -preset superfast</option>
        <option value="veryfast">[6] -preset veryfast</option>
        <option value="faster">[7] -preset faster</option>
        <option value="fast">[9] -preset fast</option>
        <option value="medium">[9] -preset medium</option>
        <option value="slow">[10] -preset slow</option>
        <option value="slower">[11] -preset slower</option>
        <option value="veryslow">[12] -preset veryslow</option>
      </select>
      <br />

      <i
        style={{
          display: props.videoSetting.includes("codec") ? "none" : "block",
        }}
      >
        When using a preset (options 4 to 12), the video codec is converted to H.264 (AVC) and the
        audio codec is converted to AAC, using libfdk_aac with VBR mode 5. More details about the
        presets can be found
        <a href="https://trac.ffmpeg.org/wiki/Encode/H.264" target="_blank">
          {" "}
          here
        </a>
        .
      </i>
      <br />

      <div
        id="crf_div"
        style={{
          display: props.videoSetting.includes("keep") ? "none" : "block",
        }}
      >
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
          <a href="https://trac.ffmpeg.org/wiki/Encode/H.264#crf" target="_blank">
            here
          </a>
          .
        </i>
      </div>
    </div>
  );
}

export default MKVMP4;
