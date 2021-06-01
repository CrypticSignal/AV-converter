import { createStore } from "redux";
import BitrateSliderReducer from "./reducers/BitrateSliderReducer";

const store = createStore(
  BitrateSliderReducer,
  window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__()
);

export default store;
