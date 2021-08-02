import { createSlice } from "@reduxjs/toolkit";

const bitrateSliderSlice = createSlice({
  name: "bitrate",
  initialState: {
    bitrate: "192",
  },
  reducers: {
    setDefault: (state, action) => {
      state.bitrate = action.payload;
    },
    change: (state, action) => {
      state.bitrate = action.payload;
    },
  },
});

export const { setDefault, change } = bitrateSliderSlice.actions;
export default bitrateSliderSlice.reducer;
