import responseHandler from "../handlers/response.handler.js";
import predictionModel from "../models/prediction.model.js";

const getPredictionsOfUser = async (req, res) => {
  try {
    const prediction = await predictionModel.find({ user: req.user.id }).sort("-createdAt");

    responseHandler.ok(res, prediction);
  } catch {
    responseHandler.error(res);
  }
};

export default { getPredictionsOfUser };