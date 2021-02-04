import BitrateSlider from '../BitrateSlider';
import VbrDropdown from './VbrDropdown';

function Mp3EncodingTypeSelector(props) {
  function renderComponent() {
    // Show the BitrateSlider component if CBR or ABR is selected. Show the VbrDropdown component if VBR is selected.
    switch (props.mp3EncodingType) {
      case 'cbr':
        return <BitrateSlider 
                  onBitrateSliderMoved={props.onBitrateSliderMoved}
                  sliderValue={props.sliderValue}
                  min='64'
                  max='320'
                  step='64' />
      case 'abr':
        return <BitrateSlider 
                  onBitrateSliderMoved={props.onBitrateSliderMoved}
                  sliderValue={props.sliderValue}
                  min='64'
                  max='320'
                  step='64' />
      case 'vbr':
        return <VbrDropdown
                  onVbrSettingChange={props.onVbrSettingChange}
                  vbrSetting={props.vbrSetting} />
      default:
        return null;
    }
  };
  return (
    <div id="mp3_encoding_div">
      <label htmlFor="mp3_encoding_type">Encoding Type:</label>
      <select value={props.mp3EncodingType} id="mp3_encoding_type" onChange={props.onMp3EncodingTypeChange}>
        <option disabled value>
          Select encoding type
        </option>
        <option value="cbr">CBR (Constant Bitrate)</option>
        <option value="abr">ABR (Average Bitrate)</option>
        <option value="vbr">VBR (Variable Bitrate)</option>
      </select>
      {renderComponent()}
    </div>
  );
}

export default Mp3EncodingTypeSelector;