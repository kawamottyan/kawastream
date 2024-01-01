import Nowplaying from "../models/nowplaying.model.js";

export const getNowplaying = async (req, res) => {
  try {
    const nowplayings = await Nowplaying.find({});
    res.send(nowplayings);
  } catch (err) {
    console.log(err);
    res.status(500).send({ message: err.message });
  }
};