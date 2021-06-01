const initialState = {
  sliderBitrate: "192",
};

const BitrateSliderReducer = (state = initialState, action) => {
  switch (action.type) {
    case "DEFAULT": {
      return {
        sliderBitrate: action.value,
      };
    }
    case "CHANGE": {
      return {
        sliderBitrate: action.value,
      };
    }
    default:
      return state;
  }
};

export default BitrateSliderReducer;
