import mongoose, { Schema } from "mongoose";
import modelOptions from "./model.options.js";

export default mongoose.model(
  "Click",
  mongoose.Schema({
    user: {
      type: Schema.Types.ObjectId,
      ref: "User",
      required: true
    },
    mediaId: {
      type: String,
      required: true
    },
    containerName: {
      type: String,
      required: false
    },
  }, modelOptions)
);