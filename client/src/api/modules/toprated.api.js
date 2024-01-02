import privateClient from "../client/private.client";

const topratedEndpoints = {
  list: "toprated",
};

const topratedApi = {
  getList: async () => {
    try {
      const response = await privateClient.get(topratedEndpoints.list);
      return { response };
    } catch (err) { return { err }; }
  },
};

export default topratedApi;