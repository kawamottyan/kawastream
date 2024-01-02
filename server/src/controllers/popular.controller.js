import Popular from "../models/popular.model.js";

export const getPopular = async (req, res) => {
  try {
    const populars = await Popular.find({});
    res.send(populars);
  } catch (err) {
    console.log(err);
    res.status(500).send({ message: err.message });
  }
};