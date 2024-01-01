import mongoose, { Schema } from "mongoose";
import modelOptions from "./model.options.js";

const predictionSchema = new Schema({
  rank: Number,
  mediaId: String,
  rating: Number,
  mediaPoster: String,
  mediaTitle: String,
  backdrop_path: String,
  vote_average: Number,
  release_date: String,
  genre_names: [String]
});

export default mongoose.model(
  "Prediction",
  new Schema({
    user: {
      type: Schema.Types.ObjectId,
      ref: "User",
      required: true
    },
    mediaType: {
      type: String,
      enum: ["tv", "movie"],
      required: true
    },
    predictions: [predictionSchema]
  }, modelOptions)
);