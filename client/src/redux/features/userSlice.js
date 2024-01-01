import { createSlice } from "@reduxjs/toolkit";

export const userSlice = createSlice({
  name: "User",
  initialState: {
    user: null,
    listFavorites: [],
    listPredictions: [],
    listClicks: [],
    listExplains: [],
  },
  reducers: {
    setUser: (state, action) => {
      if (action.payload === null) {
        localStorage.removeItem("actkn");
      } else {
        if (action.payload.token) localStorage.setItem("actkn", action.payload.token);
      }
      state.user = action.payload;
    },
    setListFavorites: (state, action) => {
      state.listFavorites = action.payload;
    },
    removeFavorite: (state, action) => {
      const { mediaId } = action.payload;
      state.listFavorites = [...state.listFavorites].filter(e => e.mediaId.toString() !== mediaId.toString());
    },
    addFavorite: (state, action) => {
      state.listFavorites = [action.payload, ...state.listFavorites];
    },

    setListPredictions: (state, action) => {
      state.listPredictions = action.payload;
    },

    addClick: (state, action) => {
      state.listClicks = [action.payload, ...state.listClicks];
    },

    setListExplain: (state, action) => {
      state.listExplains = action.payload;
    },

  }
});

export const {
  setUser,
  setListFavorites,
  addFavorite,
  removeFavorite,
  setListPredictions,
  addClick,
  setListExplain,
} = userSlice.actions;

export default userSlice.reducer;