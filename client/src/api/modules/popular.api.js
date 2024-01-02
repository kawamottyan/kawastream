import privateClient from "../client/private.client";

const popularEndpoints = {
  list: "popular",
};

const popularApi = {
  getList: async () => {
    try {
      const response = await privateClient.get(popularEndpoints.list);
      return { response };
    } catch (err) { return { err }; }
  },
};

export default popularApi;