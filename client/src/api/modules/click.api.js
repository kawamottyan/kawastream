import privateClient from "../client/private.client";

const clickEndpoints = {
  list: "user/click",
  add: "user/click",
  remove: ({ clickId }) => `user/click/${clickId}`
};

const clickApi = {
  getList: async () => {
    try {
      const response = await privateClient.get(clickEndpoints.list);

      return { response };
    } catch (err) { return { err }; }
  },
  add: async ({
    mediaId,
    containerName,
  }) => {
    try {
      const response = await privateClient.post(
        clickEndpoints.add,
        {
          mediaId,
          containerName,
        }
      );

      return { response };
    } catch (err) { return { err }; }
  },
  remove: async ({ clickId }) => {
    try {
      const response = await privateClient.delete(clickEndpoints.remove({ clickId }));

      return { response };
    } catch (err) { return { err }; }
  }
};

export default clickApi;