import bitrateSliderReducer from "./bitrateSliderSlice";
import uploadProgressReducer from "./uploadProgressSlice";
import { configureStore } from "@reduxjs/toolkit";

const store = configureStore({
  reducer: {
    bitrate: bitrateSliderReducer,
    progress: uploadProgressReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
