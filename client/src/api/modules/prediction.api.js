import privateClient from "../client/private.client";

const predictionEndpoints = {
  list: "user/prediction",
};

const predictionApi = {
  getList: async () => {
    try {
      const response = await privateClient.get(predictionEndpoints.list);
      return { response };
    } catch (err) { return { err }; }
  },
};

export default predictionApi;
