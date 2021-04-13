function VbrDropdown(props) {
  return (
    <div>
      <label htmlFor="mp3_vbr_setting">Setting:</label>
      <select
        id="mp3_vbr_setting"
        onChange={props.onVbrSettingChange}
        value={props.vbrSetting}
      >
        <option disabled value>
          Select VBR setting
        </option>
        <option value="0">-V 0 (~240kbps)</option>
        <option value="1">-V 1 (~220kbps)</option>
        <option value="2">-V 2 (~190kbps)</option>
        <option value="3">-V 3 (~170kbps)</option>
        <option value="4">-V 4 (~160kbps)</option>
        <option value="5">-V 5 (~130kbps)</option>
        <option value="6">-V 6 (~120kbps)</option>
      </select>
      <br />
      <i>
        For more details about the settings, click{" "}
        <a
          target="_blank"
          href="http://wiki.hydrogenaud.io/index.php?title=LAME#Recommended_settings_details"
        >
          here
        </a>
        .
      </i>
    </div>
  );
}

export default VbrDropdown;
