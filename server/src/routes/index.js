import express from "express";
import userRoute from "./user.route.js";
import mediaRoute from "./media.route.js";
import personRoute from "./person.route.js";
import reviewRoute from "./review.route.js";
import { getNowplaying } from "../controllers/nowplaying.controller.js";
import { getPopular } from "../controllers/popular.controller.js";
import { getToprated } from "../controllers/toprated.controller.js";

const router = express.Router();

router.use("/user", userRoute);
router.use("/person", personRoute);
router.use("/reviews", reviewRoute);
router.use("/:mediaType", mediaRoute);
router.get('/nowplaying', getNowplaying);
router.get('/popular', getPopular);
router.get('/toprated', getToprated);

export default router;
