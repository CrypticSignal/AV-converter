import BitrateSlider from '../BitrateSlider';
import VbrDropdown from './VbrDropdown';

function AacEncodingTypeSelector(props) {

    function renderComponent() {
        switch (props.encodingType) {
          case 'cbr':
            return <BitrateSlider 
                        onBitrateSliderMoved={props.onBitrateSliderMoved}
                        sliderValue={props.sliderValue}
                        min='32'
                        max='512'
                        step='32' />
          case 'vbr':
            return <VbrDropdown
                        onVbrModeChange={props.onVbrModeChange}
                        vbrMode={props.vbrMode} />
          default:
            return null;
        }
    };

    return (
        <div id="FDK">
            <label htmlFor="fdk_encoding">CBR or VBR:</label>
            <select id="fdk_encoding" onChange={props.onAacEncodingTypeChange} value={props.encodingType}>
                <option disabled value>Select Encoding Type</option>
                <option value="cbr">CBR (Constant Bitrate)</option>
                <option value="vbr">VBR (Variable Bitrate)</option>
            </select>
            {renderComponent()}
        </div>
    )
}

export default AacEncodingTypeSelector;