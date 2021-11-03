export default function AacExtensionSelector(props) {
  return (
    <div id="aac_extension_div" onChange={props.onAacExtensionChange}>
      <label>
        <input type="radio" value="m4a" checked={props.aacExtension === "m4a"} /> .m4a
      </label>

      <label>
        <input type="radio" value="aac" checked={props.aacExtension === "aac"} /> .aac
      </label>
    </div>
  );
}
