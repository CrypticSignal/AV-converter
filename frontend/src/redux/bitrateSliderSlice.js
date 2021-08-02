import { createSlice } from "@reduxjs/toolkit";

const bitrateSliderSlice = createSlice({
  name: "sliderValue",
  initialState: {
    value: "192",
  },
  reducers: {
    setDefault: (state, action) => {
      state.value = action.payload;
    },
    change: (state, action) => {
      state.value = action.payload;
    },
  },
});

export const { setDefault, change } = bitrateSliderSlice.actions;
export default bitrateSliderSlice.reducer;
export const selectSliderValue = (state) => state.bitrate.value;
