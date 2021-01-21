function IsKeepVideo(props) {
    return (
        <div id="keep_video_div" onChange={props.onIsKeepVideoChange}>
            <br/>
            <div className="form-check">
                <label className="form-check-label">
                <input type="radio" className="form-check-input" value="yes" checked={props.isKeepVideo === 'yes'} />
                Keep the video (if applicable)
                </label>
            </div>
            <div className="form-check">
                <label className="form-check-label">
                <input type="radio" className="form-check-input" value="no" checked={props.isKeepVideo === 'no'}/>
                I want an audio file
                </label>
            </div>
        </div>
    )
}

export default IsKeepVideo;