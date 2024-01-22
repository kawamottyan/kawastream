import Trending from "../models/trending.model.js";

export const getTrending = async (req, res) => {
  try {
    const trendings = await Trending.find({});
    res.send(trendings);
  } catch (err) {
    console.log(err);
    res.status(500).send({ message: err.message });
  }
};