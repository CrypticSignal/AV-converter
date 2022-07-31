import React from "react";

interface AacExtensionSelectorProps {
  onAacExtensionChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  aacExtension: string;
}

const AacExtensionSelector: React.FC<AacExtensionSelectorProps> = ({
  onAacExtensionChange,
  aacExtension,
}) => {
  return (
    <div id="aac_extension_div" onChange={onAacExtensionChange}>
      <label>
        <input type="radio" value="m4a" checked={aacExtension === "m4a"} /> .m4a
      </label>

      <label>
        <input type="radio" value="aac" checked={aacExtension === "aac"} /> .aac
      </label>
    </div>
  );
};

export default AacExtensionSelector;
