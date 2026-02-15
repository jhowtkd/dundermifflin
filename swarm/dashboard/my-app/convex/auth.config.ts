export default {
  providers: [
    {
      domain: process.env.CONVEX_AUTH_DOMAIN || "",
      applicationID: process.env.CONVEX_AUTH_CLIENT_ID || "",
    },
  ],
};
