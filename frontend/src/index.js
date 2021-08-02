import { Fragment } from "react";
import ReactDOM from "react-dom";
import App from "./app/App";
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
