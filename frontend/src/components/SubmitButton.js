function SubmitButton(props) {
    return (
        <button id="convert_btn" className="btn btn-primary" onClick={props.onSubmitClicked}>Submit</button>
    )
}

export default SubmitButton;