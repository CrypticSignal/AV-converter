function MP3() {
    return (
        <div id="mp3_div">
            {'{'}/*Bitrate modes for MP3*/{'}'}
            <div id="mp3_encoding_div">
                <label htmlfor="mp3_encoding_type">Bitrate Type:</label>
                <select id="mp3_encoding_type" onChange="showHideMP3(this.value);">
                <option disabled value>Select encoding type</option>
                <option selected value="cbr">CBR (Constant Bitrate)</option>
                <option value="vbr">VBR (Variable Bitrate)</option>
                </select>
            </div>
            {'{'}/*Bitrate slider for MP3 CBR*/{'}'}
            <div id="mp3_slider_div">
                <p>Set your desired bitrate via the slider:</p>
                <input type="range" min="{64}" max="{320}" step="{64}" defaultvalue="{192}" id="mp3_bitrate" className="slider" />
                <span id="bitrate_value"><br /><br />
                </span></div>
            {'{'}/* VBR settings for MP3 */{'}'}
            <div id="mp3_vbr_setting_div">
                <label htmlFor="mp3_vbr_setting">Setting:</label>
                <select id="mp3_vbr_setting">
                <option disabled value>Select VBR setting</option>
                <option selected value="{0}">-V 0 (~240kbps)</option>
                <option value="{1}">-V 1 (~220kbps)</option>
                <option value="{2}">-V 2 (~190kbps)</option>
                <option value="{3}">-V 3 (~170kbps)</option>
                <option value="{4}">-V 4 (~160kbps)</option>
                <option value="{5}">-V 5 (~130kbps)</option>
                <option value="{6}">-V 6 (~120kbps)</option>
                </select><br />
                <i>For more details about the settings, click
                <a target="_blank" href="http://wiki.hydrogenaud.io/index.php?title=LAME#Recommended_settings_details">here</a>.
                </i>
            </div>
        </div>
    )
}