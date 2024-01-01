import privateClient from "../client/private.client";

const explainEndpoints = {
  list: "user/explain",
};

const explainApi = {
  getList: async () => {
    try {
      const response = await privateClient.get(explainEndpoints.list);
      return { response };
    } catch (err) { return { err }; }
  },
};

export default explainApi;