export default function FormatSelector(props) {
  return (
    <div>
      <h5>Desired Format</h5>
      <select id="codecs" onChange={props.onCodecChange} value={props.codec}>
        <option value="AAC">AAC (.m4a)</option>
        <option value="AC3">AC3 (Dolby Digital)</option>
        <option value="ALAC">ALAC (.m4a)</option>
        <option value="CAF">CAF (.caf)</option>
        <option value="DTS">DTS (.dts)</option>
        <option value="FLAC">FLAC (.flac)</option>
        <option value="MKA">MKA (.mka)</option>
        <option value="MKV">MKV (.mkv)</option>
        <option value="MP3">MP3 (.mp3)</option>
        <option value="MP4">MP4 (.mp4)</option>
        <option value="Opus">Opus (.opus)</option>
        <option value="Vorbis">Vorbis (.ogg)</option>
        <option value="WAV">WAV (.wav)</option>
      </select>
    </div>
  );
}
