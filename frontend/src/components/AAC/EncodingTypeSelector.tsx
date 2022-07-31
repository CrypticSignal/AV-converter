import React from "react";
import BitrateSlider from "../BitrateSlider";
import VbrDropdown from "./VbrDropdown";

interface AacEncodingTypeSelectorProps {
  onAacEncodingTypeChange: (event: React.ChangeEvent<HTMLSelectElement>) => void;
  encodingType: string;
  initialSliderValue: string;
  onVbrModeChange: (event: React.ChangeEvent<HTMLSelectElement>) => void;
  vbrMode: string;
}

const AacEncodingTypeSelector: React.FC<AacEncodingTypeSelectorProps> = ({
  onAacEncodingTypeChange,
  encodingType,
  initialSliderValue,
  onVbrModeChange,
  vbrMode,
}) => {
  const renderComponent = () => {
    switch (encodingType) {
      case "cbr":
        return <BitrateSlider initialValue={initialSliderValue} min="32" max="512" step="32" />;
      case "vbr":
        return <VbrDropdown onVbrModeChange={onVbrModeChange} vbrMode={vbrMode} />;
      default:
        return null;
    }
  };

  return (
    <div id="FDK">
      <label htmlFor="fdk_encoding">CBR or VBR:</label>
      <select id="fdk_encoding" onChange={onAacEncodingTypeChange} value={encodingType}>
        <option disabled>Select Encoding Type</option>
        <option value="cbr">CBR (Constant Bitrate)</option>
        <option value="vbr">VBR (Variable Bitrate)</option>
      </select>
      {renderComponent()}
    </div>
  );
};

export default AacEncodingTypeSelector;
