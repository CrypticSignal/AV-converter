function ProgressBar() {
    return (
        <div id="progress_wrapper" style={{display: 'none'}}>
            <br/>
            <div className="progress mb-3"> {/*Bootstrap class*/}
                <div id="progress_bar" className="progress-bar" role="progressbar" aria-valuenow={0} aria-valuemin={0} aria-valuemax={100} />
            </div>
            <label id="progress_status" />
        </div>
    )
}

export default ProgressBar;