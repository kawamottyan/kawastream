import responseHandler from "../handlers/response.handler.js";
import clickModel from "../models/click.model.js";

const addClick = async (req, res) => {
  try {
    const isClick = await clickModel.findOne({
      user: req.user.id,
      mediaId: req.body.mediaId
    });

    if (isClick) return responseHandler.ok(res, isClick);

    const click = new clickModel({
      ...req.body,
      user: req.user.id
    });

    await click.save();

    responseHandler.created(res, click);
  } catch {
    responseHandler.error(res);
  }
};

export default { addClick };