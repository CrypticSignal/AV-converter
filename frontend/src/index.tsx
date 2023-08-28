import ReactDOM from "react-dom";
import { Fragment } from "react";
import { Provider } from "react-redux";
import store from "./redux/store";
import { BrowserRouter } from "react-router-dom";
import { LocationProvider } from "@reach/router";
import App from "./App";

ReactDOM.render(
  <Fragment>
    <Provider store={store}>
      <BrowserRouter>
        <LocationProvider>
          <App />
        </LocationProvider>
      </BrowserRouter>
    </Provider>
  </Fragment>,
  document.getElementById("root")
);
