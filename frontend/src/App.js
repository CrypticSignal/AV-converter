import { useState } from "react";
import { useSelector } from "react-redux";
import { selectSliderValue } from "./redux/bitrateSliderSlice";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
// FFmpeg WASM
import { createFFmpeg, fetchFile } from "@ffmpeg/ffmpeg";
// Pages
import AboutPage from "./pages/AboutPage";
import Filetypes from "./pages/Filetypes";
import YoutubePage from "./pages/YouTubePage";
// General Components
import AlertDiv from "./components/AlertDiv";
import ConvertButton from "./components/ConvertButton";
import EncodingTypeSelector from "./components/AAC/EncodingTypeSelector";
import FileInput from "./components/FileInput";
import FormatSelector from "./components/FormatSelector";
import IsKeepVideo from "./components/IsKeepVideo";
import Navbar from "./components/Navbar";
// Output Format Related Components
import AacExtensionSelector from "./components/AAC/AacExtensionSelector";
import AC3 from "./components/AC3";
import DTS from "./components/DTS";
import FLAC from "./components/FLAC";
import MKVMP4 from "./components/MKVMP4";
import MP3EncodingTypeSelector from "./components/MP3/EncodingTypeSelector";
import NoOptions from "./components/NoOptions";
import Opus from "./components/Opus";
import VorbisEncodingType from "./components/Vorbis/EncodingType";
import WavBitDepth from "./components/WAV";
// React-Bootstrap
import Button from "react-bootstrap/Button";
import Container from "react-bootstrap/Container";
import ProgressBar from "react-bootstrap/ProgressBar";
import Spinner from "react-bootstrap/Spinner";
// Functions
import showAlert from "./functions/showAlert";
import buttonClicked from "./functions/youtubeDownloader";

function App() {
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
  // MKV and MP4
  const [videoSetting, setVideoSetting] = useState("veryfast");
  const [crfValue, setCrfValue] = useState("18");
  // Opus
  const [opusEncodingType, setOpusEncodingType] = useState("vbr");
  // Conversion progress.
  const [progress, setProgress] = useState("Initialising...");
  // Vorbis
  const [vorbisEncodingType, setVorbisEncodingType] = useState("abr");
  const [qValue, setQValue] = useState("6");
  // WAV
  const [wavBitDepth, setWavBitDepth] = useState("16");
  // Which button was clicked on the YT downloader page.
  const [whichButtonClicked, setWhichButtonClicked] = useState(null);

  // ...............................................................................................

  const getFFmpegWASMLogs = ({ message }) => {
    if (message.includes("FS.readFile")) {
      showAlert("Conversion complete. The converted file should be downloading :)", "success");
      setProgress("Initialising...");
    } else if (message !== "use ffmpeg.wasm v0.9.8") {
      showAlert(`${progress}<br>${message}`, "info");
    }
  };

  const getProgress = ({ ratio }) => {
    setProgress(`Conversion is ${(ratio * 100).toFixed(1)}% complete...`);
  };

  const ffmpeg = createFFmpeg({
    logger: getFFmpegWASMLogs,
    progress: getProgress,
  });

  const convertFile = async (ffmpegArgs, outputFilename) => {
    await ffmpeg.load();
    ffmpeg.FS("writeFile", inputFilename, await fetchFile(file));
    await ffmpeg.run(...ffmpegArgs);
    const data = ffmpeg.FS("readFile", outputFilename);
    const anchorTag = document.createElement("a");
    console.log(URL.createObjectURL(new Blob([data.buffer])));
    anchorTag.href = URL.createObjectURL(new Blob([data.buffer]));
    anchorTag.download = outputFilename;
    anchorTag.click();
  };

  const onFileInput = (e) => {
    setFile(e.target.files[0]);
    setInputFilename(e.target.files[0].name);
    const filename = e.target.files[0].name;
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
    if (e.target.value === "MKV") {
      setVideoSetting("keep_codecs");
    } else if (e.target.value === "MP4") {
      setVideoSetting("veryfast");
    }
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

  // MKV and MP4
  const onVideoSettingChange = (e) => {
    setVideoSetting(e.target.value);
  };
  const onCrfChange = (e) => {
    setCrfValue(e.target.value);
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
    console.log("test");
    const state = {
      inputFilename: inputFilename,
      outputName: document.getElementById("output_name").value,
      file: file,
      codec: codec,
      sliderValue: sliderValue,
      mp3EncodingType: mp3EncodingType,
      mp3VbrSetting: mp3VbrSetting,
      aacEncodingType: aacEncodingType,
      aacExtension: aacExtension,
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
      wavBitDepth: wavBitDepth,
    };

    const formdata = new FormData();
    formdata.append("state", JSON.stringify(state));

    const conversionResponse = await fetch("/api/get-ffmpeg-args", {
      method: "POST",
      body: formdata,
    });

    const json = await conversionResponse.json();
    const ffmpegArgs = json["ffmpeg_args"].split(" ");
    const outputFilename = json["output_name"];

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
            <EncodingTypeSelector
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
      case "MKV":
        return (
          <MKVMP4
            onVideoSettingChange={onVideoSettingChange}
            videoSetting={videoSetting}
            onCrfChange={onCrfChange}
            crfValue={crfValue}
          />
        );
      case "MP4":
        return (
          <MKVMP4
            onVideoSettingChange={onVideoSettingChange}
            videoSetting={videoSetting}
            onCrfChange={onCrfChange}
            crfValue={crfValue}
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
    <Router>
      <Switch>
        <Route exact path="/">
          <Navbar />

          <h1>Audio / Video Converter</h1>

          <Container>
            <FileInput updateBoxes={onFileInput} />
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
            <br />

            <AlertDiv />

            <ConvertButton onConvertClicked={onConvertClicked} />

            <div id="uploading_div" style={{ display: "none" }}>
              <div id="upload_progress">
                <ProgressBar
                  now={useSelector((state) => state.progress.progress)}
                  label={`${useSelector((state) => state.progress.progress)}%`}
                />
                <p id="progress_values" />
              </div>
              <Button id="cancel_btn" variant="secondary">
                Cancel
              </Button>
            </div>

            <div id="converting_div" style={{ display: "none" }}>
              <p id="progress"></p>
              <Spinner id="converting_btn" animation="border" /> Converting...
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
    </Router>
  );
}

export default App;
