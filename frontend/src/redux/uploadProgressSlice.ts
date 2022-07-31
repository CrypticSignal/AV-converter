import { createSlice } from "@reduxjs/toolkit";

const uploadProgressSlice = createSlice({
  name: "progress",
  initialState: {
    progress: 0,
  },
  reducers: {
    update: (state, action) => {
      state.progress = action.payload;
    },
  },
});

export const { update } = uploadProgressSlice.actions;
export default uploadProgressSlice.reducer;
