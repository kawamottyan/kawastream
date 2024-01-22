import mongoose from "mongoose";

const trendingSchema = new mongoose.Schema({
  _id: false, 
  adult: Boolean,
  backdrop_path: String,
  genre_ids: [{ $numberInt: String }],
  id: { $numberInt: String },
  original_language: String,
  original_title: String,
  overview: String,
  popularity: { $numberDouble: String },
  poster_path: String,
  release_date: String,
  title: String,
  video: Boolean,
  vote_average: { $numberDouble: String },
  vote_count: { $numberInt: String }
}, { collection: 'test.trendings' });

const Trending = mongoose.model('Trending', trendingSchema, 'trendings');

export default Trending;