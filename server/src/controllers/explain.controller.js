import responseHandler from "../handlers/response.handler.js";
import explainModel from "../models/explain.model.js";

const getExplainOfUser = async (req, res) => {
  try {
    const explain = await explainModel.find({ user: req.user.id }).sort("-createdAt");

    responseHandler.ok(res, explain);
  } catch {
    responseHandler.error(res);
  }
};

export default { getExplainOfUser };