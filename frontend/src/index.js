import ReactDOM from "react-dom";
import { Fragment } from "react";
import App from "./App";
import { Provider } from "react-redux";
import store from "./redux/store";
import { BrowserRouter as Router } from "react-router-dom";

ReactDOM.render(
  <Fragment>
    <Provider store={store}>
      <Router>
        <App />
      </Router>
    </Provider>
  </Fragment>,
  document.getElementById("root")
);
