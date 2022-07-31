import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { RootState } from "./store";

interface SliderState {
  value: string;
}

const initialState = { value: "192" } as SliderState;

const bitrateSliderSlice = createSlice({
  name: "sliderValue",
  initialState,
  reducers: {
    setDefault: (state, action: PayloadAction<string>) => {
      state.value = action.payload;
    },
    change: (state, action: PayloadAction<string>) => {
      state.value = action.payload;
    },
  },
});

export default bitrateSliderSlice.reducer;
export const { setDefault, change } = bitrateSliderSlice.actions;
export const selectSliderValue = (state: RootState) => state.bitrate.value;
