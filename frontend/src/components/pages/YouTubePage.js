async function pasteClipboard() {
    const clipboardText = await navigator.clipboard.readText();
    document.getElementById("link").value = clipboardText;
}

function YoutubePage(props) {
    return (
        <div>
            <h1>YT downloader</h1>
            <div className="container">
                <p><strong>Video (best quality)</strong> - usually gives you an MKV (.mkv) or WebM (.webm) file with Opus audio.</p>
                <p><strong>Audio (best quality)</strong> - usually gives you an Opus file (.opus).</p>
                <p>If using an <strong>iOS device</strong>, select <strong>Video (MP4)</strong> or <strong>Audio (MP3)</strong> as iOS does not support all media formats natively.</p>
                <h5><b>Link:</b></h5>
                <input type="text" autoComplete="off" className="form-control" onClick={pasteClipboard} id="link" required />
                <hr /> 
                <div id="alert_wrapper" style={{display: 'none'}} />
                <div className="btn-group mr-2 mb-2" role="group">
                    <button className="btn btn-dark" onClick={props.onYtButtonClicked} value="mp4">Video (MP4)</button>
                </div>
                <div className="btn-group mb-2" role="group">
                    <button className="btn btn-dark" onClick={props.onYtButtonClicked} value="video_best">Video (best quality)</button>
                </div><br/>
                <div className="btn-group mr-2" role="group">
                    <button className="btn btn-dark" onClick={props.onYtButtonClicked} value="audio_mp3">Audio (MP3)</button>
                </div>
                <button className="btn btn-dark" onClick={props.onYtButtonClicked} value="audio_best">Audio (best quality)</button>
            </div>
        </div>
    )
}

export default YoutubePage;