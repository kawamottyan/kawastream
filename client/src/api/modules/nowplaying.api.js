import privateClient from "../client/private.client";

const nowplayingEndpoints = {
  list: "nowplaying",
};

const nowplayingApi = {
  getList: async () => {
    try {
      const response = await privateClient.get(nowplayingEndpoints.list);
      return { response };
    } catch (err) { return { err }; }
  },
};

export default nowplayingApi;