function ConvertButton(props) {
  return (
    <button id="convert_btn" className="btn btn-primary" onClick={props.onSubmitClicked}>
      Convert
    </button>
  );
}

export default ConvertButton;