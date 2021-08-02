import bitrateSliderReducer from "../redux/bitrateSliderSlice";
import uploadProgressReducer from "../redux/uploadProgressSlice";
import { configureStore } from "@reduxjs/toolkit";

const store = configureStore({
  reducer: {
    bitrate: bitrateSliderReducer,
    progress: uploadProgressReducer,
  },
});

export default store;
