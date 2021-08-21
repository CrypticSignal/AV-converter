import ReactDOM from "react-dom";
import { Fragment } from "react";
import App from "./App";
import { Provider } from "react-redux";
import store from "./app/store";

ReactDOM.render(
  <Fragment>
    <Provider store={store}>
      <App />
    </Provider>
  </Fragment>,
  document.getElementById("root")
);
