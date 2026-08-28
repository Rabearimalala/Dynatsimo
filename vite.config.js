const apiPort = Number(process.env.DYNATSIMO_API_PORT || 8000);

export default {
  server: {
    proxy: {
      "/api": {
        target: `http://127.0.0.1:${apiPort}`,
        changeOrigin: true,
      },
    },
  },
};
