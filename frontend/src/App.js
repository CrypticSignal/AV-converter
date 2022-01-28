import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { selectSliderValue } from "./redux/bitrateSliderSlice";
import { BrowserRouter as Router, Route, Switch, useLocation } from "react-router-dom";
// FFmpeg WASM
import { createFFmpeg, fetchFile } from "@ffmpeg/ffmpeg";
// Pages
import AboutPage from "./pages/AboutPage";
import Filetypes from "./pages/Filetypes";
import YoutubePage from "./pages/YouTubePage";
// General Components
import AlertDiv from "./components/AlertDiv";
import ConvertButton from "./components/ConvertButton";
import AacEncodingTypeSelector from "./components/AAC/EncodingTypeSelector";
import FileInput from "./components/FileInput";
import FormatSelector from "./components/FormatSelector";
import IsKeepVideo from "./components/IsKeepVideo";
import Navbar from "./components/Navbar";
// Output Format Related Components
import AacExtensionSelector from "./components/AAC/AacExtensionSelector";
import AC3 from "./components/AC3";
import DTS from "./components/DTS";
import FLAC from "./components/FLAC";
import H264 from "./components/H264";
import MP3EncodingTypeSelector from "./components/MP3/EncodingTypeSelector";
import NoOptions from "./components/NoOptions";
import Opus from "./components/Opus";
import VorbisEncodingType from "./components/Vorbis/EncodingType";
import WavBitDepth from "./components/WAV";
// React-Bootstrap
import Container from "react-bootstrap/Container";
import ProgressBar from "react-bootstrap/ProgressBar";
import Spinner from "react-bootstrap/Spinner";
// Functions
import { createFFmpegArgs } from "./functions/createFFmpegArgs";
import showAlert from "./functions/showAlert";
import buttonClicked from "./functions/youtubeDownloader";
// Images
import ffmpegLogo from "./images/ffmpeg-25.png";
import webAssemblyLogo from "./images/webassembly-25.png";
// React Google Analytics module
import ReactGA from "react-ga";

ReactGA.initialize("UA-216028081-1");

function App() {
  const location = useLocation();

  useEffect(() => {
    ReactGA.pageview(location.pathname);
  }, [location]);

  const [file, setFile] = useState(null);
  const [inputFilename, setInputFilename] = useState("");
  const [codec, setCodec] = useState("MP3");
  // MP3
  const [mp3EncodingType, setMp3EncodingType] = useState("cbr");
  const [mp3VbrSetting, setMp3VbrSetting] = useState("0");
  // AAC
  const [aacExtension, setAacExtension] = useState("m4a");
  const [aacEncodingType, setAacEncodingType] = useState("cbr");
  const [aacVbrMode, setAacVbrMode] = useState("5");
  // AC3
  const [ac3Bitrate, setAc3Bitrate] = useState("640");
  // DTS
  const [dtsBitrate, setDtsBitrate] = useState("768");
  // FLAC
  const [flacCompression, setFlacCompression] = useState("5");
  // Keep the video?
  const [isKeepVideo, setIsKeepVideo] = useState("no");
  // H.264/AVC
  const [crfValue, setCrfValue] = useState("18");
  const [transcodeVideosAudio, setTranscodeVideosAudio] = useState(true);
  const [transcodeVideo, setTranscodeVideo] = useState("yes");
  const [videoBitrate, setVideoBitrate] = useState("8");
  const [videoContainer, setVideoContainer] = useState("mp4");
  const [videoEncodingType, setVideoEncodingType] = useState("crf");
  const [x264Preset, setX264Preset] = useState("superfast");
  // Opus
  const [opusEncodingType, setOpusEncodingType] = useState("vbr");
  // Conversion progress.
  const [progress, setProgress] = useState(0);
  // Vorbis
  const [vorbisEncodingType, setVorbisEncodingType] = useState("abr");
  const [qValue, setQValue] = useState("6");
  // WAV
  const [wavBitDepth, setWavBitDepth] = useState("16");
  // Which button was clicked on the YT downloader page.
  const [whichButtonClicked, setWhichButtonClicked] = useState(null);

  // ...............................................................................................

  const getFFmpegWASMLogs = ({ message }) => {
    if (message !== "use ffmpeg.wasm v0.10.1") {
      showAlert(message, "info");
      console.log(message);
    }
  };

  const getProgress = ({ ratio }) => {
    setProgress((ratio * 100).toFixed(1));
  };

  const ffmpeg = createFFmpeg({
    logger: getFFmpegWASMLogs,
    progress: getProgress,
  });

  const convertFile = async (ffmpegArgs, outputFilename) => {
    await ffmpeg.load();

    ffmpeg.FS("writeFile", inputFilename, await fetchFile(file));

    document.getElementById("converting_spinner").style.display = "block";
    document.getElementById("conversion_progress").style.display = "block";
    const startTime = Date.now() / 1000;
    await ffmpeg.run(...ffmpegArgs);

    console.log(`Conversion took ${(Date.now() / 1000 - startTime).toFixed(1)} seconds.`);
    document.getElementById("converting_spinner").style.display = "none";
    document.getElementById("conversion_progress").style.display = "none";
    // Reset the value of progress.
    setProgress(0);

    const data = ffmpeg.FS("readFile", outputFilename);
    const objectURL = URL.createObjectURL(new Blob([data.buffer]));

    const anchorTag = document.createElement("a");
    anchorTag.href = objectURL;
    anchorTag.download = outputFilename;
    anchorTag.click();

    // Delete file from MEMFS
    ffmpeg.FS("unlink", outputFilename);

    showAlert(
      `Conversion complete. The converted file should be downloading :)<br>If it isn't, click <a href="${objectURL}" download="${outputFilename}">here</a> to start the download.`,
      "success"
    );
    document.getElementById("convert_btn").style.display = "block";
  };

  const onFileInput = (e) => {
    setFile(e.target.files[0]);
    const filename = e.target.files[0].name;
    setInputFilename(filename);
    const inputLabel = document.getElementById("file_input_label");
    const outputNameBox = document.getElementById("output_name");
    // Show the name of the selected file.
    inputLabel.innerText = filename;
    // Filename without the extension.
    const nameWithoutExt = filename.split(".").slice(0, -1).join(".");
    // Remove percentage sign(s) as this causes an issue when secure_filename is used in main.py
    const defaultOutputName = nameWithoutExt.replace(/%/g, "");
    // Set the value of the Output Name box to defaultOutputName.
    outputNameBox.value = defaultOutputName;
  };

  const onCodecChange = (e) => {
    setCodec(e.target.value);
  };

  // MP3
  const onMp3EncodingTypeChange = (e) => {
    setMp3EncodingType(e.target.value);
  };
  const onMp3VbrSettingChange = (e) => {
    setMp3VbrSetting(e.target.value);
  };

  // AAC
  const onAacExtensionChange = (e) => {
    setAacExtension(e.target.value);
  };
  const onAacEncodingTypeChange = (e) => {
    setAacEncodingType(e.target.value);
  };
  const onAacVbrModeChange = (e) => {
    setAacVbrMode(e.target.value);
  };

  // AC3
  const onAc3BitrateChange = (e) => {
    setAc3Bitrate(e.target.value);
  };

  // DTS
  const onDtsBitrateChange = (e) => {
    setDtsBitrate(e.target.value);
    console.log(e.target.value);
  };

  // FLAC
  const onFlacCompressionChange = (e) => {
    setFlacCompression(e.target.value);
  };

  // isKeepVideo
  const onIsKeepVideoChange = (e) => {
    setIsKeepVideo(e.target.value);
  };

  // H.264/AVC (MP4 or MKV container)
  const onTranscodeVideoChange = (e) => {
    setTranscodeVideo(e.target.value);
  };
  const onCrfChange = (e) => {
    setCrfValue(e.target.value);
  };
  const onTranscodeAudioCheckbox = () => {
    setTranscodeVideosAudio(!transcodeVideosAudio);
  };
  const onVideoContainerChange = (e) => {
    setVideoContainer(e.target.value);
  };
  const onVideoBitrateChange = (e) => {
    setVideoBitrate(e.target.value);
  };
  const onVideoEncodingTypeChange = (e) => {
    setVideoEncodingType(e.target.value);
  };
  const onX264PresetChange = (e) => {
    setX264Preset(e.target.value);
  };

  // Opus
  const onOpusTypeChange = (e) => {
    setOpusEncodingType(e.target.value);
  };

  // Vorbis
  const onVorbisEncodingTypeChange = (e) => {
    setVorbisEncodingType(e.target.value);
  };
  const onVorbisSliderMoved = (e) => {
    setQValue(e.target.value);
  };

  // WAV
  const onWavBitDepthChange = (e) => {
    setWavBitDepth(e.target.value);
  };

  const sliderValue = useSelector(selectSliderValue);

  const onConvertClicked = async () => {
    if (file === null) {
      showAlert("You must choose an input file.", "danger");
      return;
    }

    console.clear();

    const { ffmpegArgs, outputFilename } = createFFmpegArgs(
      aacEncodingType,
      aacExtension,
      aacVbrMode,
      ac3Bitrate,
      codec,
      crfValue,
      dtsBitrate,
      flacCompression,
      isKeepVideo,
      inputFilename,
      mp3EncodingType,
      mp3VbrSetting,
      window.navigator.hardwareConcurrency, // numLogicalProcessors
      opusEncodingType,
      document.getElementById("output_name").value,
      qValue,
      sliderValue,
      transcodeVideo,
      transcodeVideosAudio,
      videoBitrate,
      videoContainer,
      videoEncodingType,
      vorbisEncodingType,
      wavBitDepth,
      x264Preset
    );

    if (outputFilename === inputFilename) {
      showAlert("Output filename cannot be same as the input filename.", "danger");
      return;
    }

    document.getElementById("convert_btn").style.display = "none";

    ffmpegArgs.unshift(inputFilename);
    ffmpegArgs.unshift("-i");
    ffmpegArgs.push(outputFilename);

    convertFile(ffmpegArgs, outputFilename);
  };

  // YT downloader page
  const onYtButtonClicked = (e) => {
    setWhichButtonClicked(e.target.value);
    buttonClicked(document.getElementById("link").value, e.target.value);
  };

  const showFormatSettings = () => {
    switch (codec) {
      case "MP3":
        return (
          <div>
            <MP3EncodingTypeSelector
              mp3EncodingType={mp3EncodingType}
              initialSliderValue="192"
              onMp3EncodingTypeChange={onMp3EncodingTypeChange}
              onMp3VbrSettingChange={onMp3VbrSettingChange}
              vbrSetting={mp3VbrSetting}
            />
            <IsKeepVideo onIsKeepVideoChange={onIsKeepVideoChange} isKeepVideo={isKeepVideo} />
          </div>
        );
      case "AAC":
        return (
          <div>
            <AacEncodingTypeSelector
              onAacEncodingTypeChange={onAacEncodingTypeChange}
              encodingType={aacEncodingType}
              initialSliderValue="192"
              onVbrModeChange={onAacVbrModeChange}
              vbrMode={aacVbrMode}
            />
            <IsKeepVideo onIsKeepVideoChange={onIsKeepVideoChange} isKeepVideo={isKeepVideo} />
          </div>
        );
      case "AC3":
        return (
          <div>
            <AC3 onAc3BitrateChange={onAc3BitrateChange} ac3Bitrate={ac3Bitrate} />
            <IsKeepVideo onIsKeepVideoChange={onIsKeepVideoChange} isKeepVideo={isKeepVideo} />
          </div>
        );
      case "ALAC":
        return (
          <div>
            <NoOptions />
            <IsKeepVideo onIsKeepVideoChange={onIsKeepVideoChange} isKeepVideo={isKeepVideo} />
          </div>
        );
      case "CAF":
        return <NoOptions />;
      case "DTS":
        return (
          <div>
            <DTS onDtsBitrateChange={onDtsBitrateChange} dtsBitrate={dtsBitrate} />
            <IsKeepVideo onIsKeepVideoChange={onIsKeepVideoChange} isKeepVideo={isKeepVideo} />
          </div>
        );
      case "FLAC":
        return (
          <div>
            <FLAC
              onFlacCompressionChange={onFlacCompressionChange}
              flacCompression={flacCompression}
            />
            <IsKeepVideo onIsKeepVideoChange={onIsKeepVideoChange} isKeepVideo={isKeepVideo} />
          </div>
        );
      case "MKA":
        return (
          <i>
            Only the audio streams will be kept and left as-is (no transcoding will be done). The
            Matroska container will be used.
          </i>
        );
      case "H264":
        return (
          <H264
            onVideoContainerChange={onVideoContainerChange}
            onTranscodeVideoChange={onTranscodeVideoChange}
            onCrfChange={onCrfChange}
            crfValue={crfValue}
            transcodeVideosAudio={transcodeVideosAudio}
            onTranscodeAudioCheckbox={onTranscodeAudioCheckbox}
            transcodeVideo={transcodeVideo}
            videoContainer={videoContainer}
            videoBitrate={videoBitrate}
            onVideoBitrateChange={onVideoBitrateChange}
            videoEncodingType={videoEncodingType}
            onVideoEncodingTypeChange={onVideoEncodingTypeChange}
            // videoFilesize={videoFilesize}
            // onVideoFilesizeChange={onVideoFilesizeChange}
            x264Preset={x264Preset}
            onX264PresetChange={onX264PresetChange}
          />
        );
      case "Opus":
        return (
          <Opus
            onOpusTypeChange={onOpusTypeChange}
            opusType={opusEncodingType}
            initialSliderValue="192"
          />
        );
      case "Vorbis":
        return (
          <VorbisEncodingType
            onVorbisEncodingTypeChange={onVorbisEncodingTypeChange}
            vorbisEncodingType={vorbisEncodingType}
            onSliderMoved={onVorbisSliderMoved}
            qValue={qValue}
            initialSliderValue="192"
          />
        );
      case "WAV":
        return (
          <div>
            <WavBitDepth onWavBitDepthChange={onWavBitDepthChange} bitDepth={wavBitDepth} />
            <IsKeepVideo onIsKeepVideoChange={onIsKeepVideoChange} isKeepVideo={isKeepVideo} />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <Switch>
      <Route exact path="/">
        <Navbar />

        <h1>Audio / Video Converter</h1>

        <div id="powered_by">
          <i id="ffmpeg">Powered by FFmpeg</i>
          <a href="https://ffmpeg.org/" target="_blank">
            <img src={ffmpegLogo} id="ffmpeg_logo" />
          </a>
          <i id="webassembly">and WebAssembly</i>
          <a href="https://webassembly.org/" target="_blank">
            <img src={webAssemblyLogo} />
          </a>
        </div>

        <Container>
          <FileInput updateBoxes={onFileInput} />
          <i style={{ fontSize: "80%" }}>Max Filesize: 2 GB</i>
          <hr />

          <FormatSelector onCodecChange={onCodecChange} codec={codec} />
          {codec === "AAC" ? (
            <AacExtensionSelector
              onAacExtensionChange={onAacExtensionChange}
              aacExtension={aacExtension}
            />
          ) : null}
          <hr />

          <h5>Encoder Settings</h5>
          {showFormatSettings()}
          <br />
          <hr />

          <h5>Output Filename</h5>
          <input
            type="text"
            autoComplete="off"
            className="form-control"
            maxLength="200"
            id="output_name"
            required
          />

          <div id="converting_spinner" style={{ display: "none" }}>
            <Spinner id="converting_btn" animation="border" /> Converting...
          </div>

          <div id="conversion_progress" style={{ display: "none" }}>
            <ProgressBar now={progress} label={`${progress}%`} />
          </div>

          <AlertDiv />

          <div id="convert_btn">
            <br />
            <ConvertButton onConvertClicked={onConvertClicked} />
          </div>
        </Container>
      </Route>

      <Route exact path="/about">
        <Navbar />
        <AboutPage />
      </Route>

      <Route exact path="/filetypes">
        <Navbar />
        <Filetypes />
      </Route>

      <Route exact path="/yt">
        <Navbar />
        <YoutubePage onYtButtonClicked={onYtButtonClicked} buttonClicked={whichButtonClicked} />
      </Route>
    </Switch>
  );
}

export default App;
