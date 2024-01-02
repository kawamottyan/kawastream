import Toprated from "../models/toprated.model.js";

export const getToprated = async (req, res) => {
  try {
    const toprateds = await Toprated.find({});
    res.send(toprateds);
  } catch (err) {
    console.log(err);
    res.status(500).send({ message: err.message });
  }
};