import BitrateSlider from '../BitrateSlider';
import QualitySlider from './QualitySlider';

function EncodingType(props) {
    function renderComponent() {
        switch (props.vorbisEncodingType) {
            case 'abr':
                return (
                    <BitrateSlider
                        onBitrateSliderMoved={props.onBitrateSliderMoved}
                        sliderValue={props.sliderValue}
                        min='32'
                        max='512'
                        step='32' />
                )
            case 'vbr':
                return (
                    <QualitySlider
                        onSliderMoved={props.onSliderMoved}
                        qValue={props.qValue} />
                )
            default:
                return null;
        }
    }
    return (
        <div id="Vorbis">
            <div id="vorbis_encoding_div">
                <label>VBR setting:</label>
                <select onChange={props.onVorbisEncodingTypeChange} value={props.vorbisEncodingType}>
                <option disabled>Select encoding type</option>
                <option value="abr">ABR (Average Bitrate)</option>
                <option value="vbr">VBR (target a quality level)</option>
                </select><br/>
            </div>
            {renderComponent()}
        </div>
    )
}

export default EncodingType;