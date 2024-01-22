import privateClient from "../client/private.client";

const trendingEndpoints = {
  list: "trending",
};

const trendingApi = {
  getList: async () => {
    try {
      const response = await privateClient.get(trendingEndpoints.list);
      return { response };
    } catch (err) { return { err }; }
  },
};

export default trendingApi;