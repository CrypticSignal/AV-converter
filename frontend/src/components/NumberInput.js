export default function NumberInput(props) {
  return (
    <div>
      <input type="number" onChange={props.onChange} value={props.value}></input>
      <span> {props.units}</span>
    </div>
  );
}
