const WavBitDepth = (props) => {
  return (
    <div id="wav_bit_depth_div">
      <label htmlFor="wav_bit_depth">Output Bit Depth (audio):</label>
      <select id="wav_bit_depth" onChange={props.onWavBitDepthChange} value={props.bitDepth}>
        <option value="16">16</option>
        <option value="24">24</option>
        <option value="32">32</option>
      </select>
    </div>
  );
};

export default WavBitDepth;
