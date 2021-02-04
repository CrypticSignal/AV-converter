import { useState } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';

import AboutPage from './components/pages/AboutPage';
import Filetypes from './components/pages/Filetypes';
import YoutubePage from './components/pages/yt/YouTubePage';
import buttonClicked from './components/pages/yt/yt'

import AlertDiv from './components/AlertDiv';
import TopBar from './components/TopBar'; 
import FileInput from './components/FileInput';
import AacEncodingTypeSelector from './components/encoders/AAC/EncodingTypeSelector';
import AC3 from './components/encoders/AC3';
import DTS from './components/encoders/DTS';
import FLAC from './components/encoders/FLAC';
import IsKeepVideo from './components/IsKeepVideo';
import MKVMP4 from './components/MKVMP4';
import Mp3EncodingTypeSelector from './components/encoders/MP3/EncodingTypeSelector';
import NoOptions from './components/NoOptions';
import Opus from './components/encoders/Opus';
import VorbisEncodingType from './components/encoders/VorbisEncodingType';
import WavBitDepth from './components/encoders/WAV';
import SubmitButton from './components/SubmitButton';

import start from './functions/Start';

function App() {
  const [codec, setCodec] = useState('MP3');
  const [file, setFile] = useState(null);
  const [sliderValue, setSliderValue] = useState('192');
  // MP3
  const [mp3EncodingType, setMp3EncodingType] = useState('cbr');
  const [mp3VbrSetting, setMp3VbrSetting] = useState('0');
  // AAC
  const [aacEncodingType, setAacEncodingType] = useState('cbr');
  const [aacVbrMode, setAacVbrMode] = useState('5');
  // AC3
  const [ac3Bitrate, setAc3Bitrate] = useState('640');
  // DTS
  const [dtsBitrate, setDtsBitrate] = useState('768');
  // FLAC
  const [flacCompression, setFlacCompression] =useState('5');
  // Keep the video?
  const [isKeepVideo, setIsKeepVideo] = useState('no');
  // MKV and MP4
  const [videoSetting, setVideoSetting] = useState('veryfast');
  const [crfValue, setCrfValue] = useState('18');
  // Opus
  const [opusEncodingType, setOpusEncodingType] = useState('vbr');
  // Vorbis
  const [vorbisEncodingType, setVorbisEncodingType] = useState('abr');
  const [qValue, setQValue] = useState('6');
  // WAV
  const [wavBitDepth, setWavBitDepth] = useState('16');
  // Which button was clicked on the YT downloader page.
  const [whichButtonClicked, setWhichButtonClicked] = useState(null);

  const onFileInput = (e) => {
    setFile(e.target.files[0])
    const filename = e.target.files[0].name;
    const inputLabel = document.getElementById("file_input_label");
    const outputNameBox = document.getElementById("output_name");
    // Show the name of the selected file.
    inputLabel.innerText = filename
    // Filename without the extension.
    const nameWithoutExt = filename.split('.').slice(0, -1).join('.')
    // Remove percentage sign(s) as this causes an issue when secure_filename is used in main.py
    const defaultOutputName = nameWithoutExt.replace(/%/g, '');
    // Set the value of the Output Name box to defaultOutputName.
    outputNameBox.value = defaultOutputName;
  }

  const onCodecChange = (e) => {
    setCodec(e.target.value);
    //renderComponent();
  };

  const onBitrateSliderMoved = (e) => {
    setSliderValue(e.target.value)
  }

  // MP3
  const onMp3EncodingTypeChange = (e) => {
    setMp3EncodingType(e.target.value);
  };

  const onMp3VbrSettingChange = (e) => {
    setMp3VbrSetting(e.target.value)
  }

  // AAC
  const onAacEncodingTypeChange = (e) => {
    setAacEncodingType(e.target.value);
  }
  const onAacVbrModeChange = (e) => {
    setAacVbrMode(e.target.value);
  }

  // AC3
  const onAc3BitrateChange = (e) => {
    setAc3Bitrate(e.target.value)
  }

  // DTS
  const onDtsBitrateChange = (e) => {
    setDtsBitrate(e.target.value)
    console.log(e.target.value)
  }

  // FLAC
  const onFlacCompressionChange = (e) => {
    setFlacCompression(e.target.value)
  }

  // isKeepVideo
  const onIsKeepVideoChange = (e) => {
    setIsKeepVideo(e.target.value)
  }

  // MKV and MP4
  const onVideoSettingChange = (e) => {
    setVideoSetting(e.target.value)
  }
  const onCrfChange = (e) => {
    setCrfValue(e.target.value)
  }

  // Opus
  const onOpusTypeChange = (e) => {
    setOpusEncodingType(e.target.value)
  }

  // Vorbis
  const onVorbisEncodingTypeChange = (e) => {
    setVorbisEncodingType(e.target.value)
  }
  const onVorbisSliderMoved = (e) => {
    setQValue(e.target.value)
  }

  // WAV
  const onWavBitDepthChange = (e) => {
    setWavBitDepth(e.target.value)
  }

  const onSubmitClicked = () => {
    const states = {
      file: file,
      codec: codec,
      sliderValue: sliderValue,
      mp3EncodingType: mp3EncodingType,
      mp3VbrSetting: mp3VbrSetting,
      aacEncodingType: aacEncodingType,
      aacVbrMode: aacVbrMode,
      ac3Bitrate: ac3Bitrate,
      dtsBitrate: dtsBitrate,
      flacCompression: flacCompression,
      isKeepVideo: isKeepVideo,
      videoSetting: videoSetting,
      crfValue: crfValue, 
      opusEncodingType: opusEncodingType,
      vorbisEncodingType: vorbisEncodingType,
      qValue: qValue,
      wavBitDepth: wavBitDepth
    }
    start(states)
  }

  // YT downloader page
  const onYtButtonClicked = (e) => {
    setWhichButtonClicked(e.target.value)
    buttonClicked(document.getElementById('link').value, e.target.value)
  }

  const renderComponent = () => {
    switch (codec) {
      case 'MP3':
        return (
          <div>
            <Mp3EncodingTypeSelector
              mp3EncodingType={mp3EncodingType}
              sliderValue={sliderValue}
              onMp3EncodingTypeChange={onMp3EncodingTypeChange}
              onBitrateSliderMoved={onBitrateSliderMoved}
              onMp3VbrSettingChange={onMp3VbrSettingChange}
              vbrSetting={mp3VbrSetting} />
            <IsKeepVideo
              onIsKeepVideoChange={onIsKeepVideoChange}
              isKeepVideo={isKeepVideo} />
          </div>
            
        );
      case 'AAC':
          return (
            <AacEncodingTypeSelector
              onAacEncodingTypeChange={onAacEncodingTypeChange}
              encodingType={aacEncodingType}
              onBitrateSliderMoved={onBitrateSliderMoved}
              sliderValue={sliderValue}
              onVbrModeChange={onAacVbrModeChange} 
              vbrMode={aacVbrMode} />
          )
      case 'AC3':
        return (
          <AC3
            onAc3BitrateChange={onAc3BitrateChange}
            ac3Bitrate={ac3Bitrate} />
        )
      case 'ALAC':
        return (
          <NoOptions/>
        )
      case 'CAF':
        return (
          <NoOptions/>
        )
      case 'DTS':
        return (
          <DTS 
            onDtsBitrateChange={onDtsBitrateChange}
            dtsBitrate={dtsBitrate} />
        )
      case 'FLAC':
        return (
          <FLAC
            onFlacCompressionChange={onFlacCompressionChange}
            flacCompression={flacCompression} />
        )
      case 'MKA':
        return (
          <NoOptions/>
        )
      case 'MKV':
        return (
          <MKVMP4
            onVideoSettingChange={onVideoSettingChange}
            videoSetting={videoSetting}
            onCrfChange={onCrfChange}
            crfValue = {crfValue} />
        )
      case 'MP4':
        return (
          <MKVMP4
            onVideoSettingChange={onVideoSettingChange}
            videoSetting={videoSetting}
            onCrfChange={onCrfChange}
            crfValue = {crfValue} />
        )

      case 'Opus':
        return (
          <Opus
            onOpusTypeChange={onOpusTypeChange}
            opusType={opusEncodingType}
            onBitrateSliderMoved={onBitrateSliderMoved}
            sliderValue={sliderValue} />
        )

      case 'Vorbis':
        return (
          <VorbisEncodingType
            onVorbisEncodingTypeChange={onVorbisEncodingTypeChange}
            vorbisEncodingType={vorbisEncodingType}
            onSliderMoved={onVorbisSliderMoved}
            qValue={qValue}
            onBitrateSliderMoved={onBitrateSliderMoved}
            sliderValue={sliderValue} />

        )
      case 'WAV':
        return (
          <WavBitDepth
            onWavBitDepthChange={onWavBitDepthChange}
            bitDepth={wavBitDepth}/>
        )
      default:
        return null;
    }
  };

  return (
    <Router>
      <Switch>
        <Route exact path='/'>
          <div>
            <TopBar/>
            <h1>Audio / Video Converter</h1>
            <div className="container">
              <FileInput
              updateBoxes={onFileInput} 
              />
              <hr></hr><h5>Desired Format</h5>
              <select
                id="codecs"
                onChange={onCodecChange}
                value={codec}>
                <option value="AAC">AAC (.m4a)</option>
                <option value="AC3">AC3 (Dolby Digital)</option>
                <option value="ALAC">ALAC</option>
                <option value="CAF">CAF (.caf)</option>
                <option value="DTS">DTS</option>
                <option value="FLAC">FLAC</option>
                <option value="MKA">MKA (extract audio without encoding it)</option>
                <option value="MKV">MKV (.mkv)</option>
                <option value="MP3">MP3</option>
                <option value="MP4">MP4 (.mp4)</option>
                <option value="Opus">Opus (.opus)</option>
                <option value="Vorbis">Vorbis (.ogg)</option>
                <option value="WAV">WAV</option>
              </select><br></br><br></br>
              <hr/><h5>Encoder Settings</h5>
              {renderComponent()}
              <br/>
              <hr/><h5>Output Filename</h5>
              <input type="text" autoComplete="off" className="form-control" maxLength="200" id="output_name" required/><br/>
              <AlertDiv/>
              <SubmitButton 
                onSubmitClicked={onSubmitClicked} />
              <button className="btn btn-primary d-none" id="uploading_btn" type="button" disabled>
                <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true" />
                Uploading file for conversion...
              </button>
              <>
              {/*"Cancel upload" button (Bootstrap class)*/}
              <button type="button" id="cancel_btn" className="btn btn-secondary d-none">Cancel upload</button>
              </>
              <>
              {/*"Converting..." button (Bootstrap class)*/}
              <div className="text-center" id="converting_btn" style={{display: 'none'}}>
                <button className="btn btn-info" disabled>
                  <span className="spinner-border spinner-border-sm" />
                  Converting...</button>
              </div>
              {/*Upload progress bar*/}
              <div id="progress_wrapper" style={{display: 'none'}}>
                <br />
                <div className="progress mb-3"> {/*Bootstrap class*/}
                  <div id="progress_bar" className="progress-bar" role="progressbar" aria-valuenow={0} aria-valuemin={0} aria-valuemax={100} />
                </div>
                <p id="progress_status" />
              </div>
              </>
              <>
              {/*ENCODER PROGRESS*/}
              <p id="progress" style={{display: 'none'}} ></p>
              </>
            </div>
          </div>
        </Route>

        <Route exact path='/about'>
          <TopBar/>
          <AboutPage/>
        </Route>

        <Route exact path='/filetypes'>
          <Filetypes/>
        </Route>

        <Route exact path='/yt'>
          <TopBar/>
          <YoutubePage
            onYtButtonClicked={onYtButtonClicked}
            buttonClicked={whichButtonClicked} />
        </Route>

      </Switch>
    </Router>
  );
}

export default App;