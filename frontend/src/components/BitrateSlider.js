function BitrateSlider(props) {
    return (
        <div><br/>
            <input type="range" className="slider" onChange={props.onBitrateSliderMoved} 
                min={props.min} max={props.max} step={props.step} value={props.sliderValue}/>
            <span>{` ${props.sliderValue} kbps`}</span>
        </div>
    )
}

export default BitrateSlider;