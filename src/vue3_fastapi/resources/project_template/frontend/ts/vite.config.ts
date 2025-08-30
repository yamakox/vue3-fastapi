import { fileURLToPath, URL } from "node:url";
import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import vueDevTools from "vite-plugin-vue-devtools";

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    // NOTE: Vue RouterのcreateWebHistory(import.meta.env.BASE_URL)で用いられるベースパスは`base`で設定する。
    base: env.BASE_URL || "/",
    server: {
      host: true,
      hmr: {
        host: "localhost",
        // HMR crashes with ENOENT when deleting SVG asset with Vite + Tailwind v4
        // https://github.com/vitejs/vite/issues/19786
        overlay: false,
      },
      proxy: {
        "/api": {
          target: "http://localhost:8000", // NOTE: Dockerコンテナ内部のホスト名とポート番号を設定する
          changeOrigin: true,
          //rewrite: (path) => path.replace(/^\/api/, '/api'),
        },
      },
    },
    build: {
      outDir: fileURLToPath(
        new URL(env.BUILD_DIR || "./dist", import.meta.url)
      ),
      emptyOutDir: true, // ビルド時にフォルダーを空にする(以前のjsファイルなどが残るため)
      chunkSizeWarningLimit: 1024 * 1024 * 10, // 10MiB
    },
    resolve: {
      alias: {
        // エイリアス'@'はjsやvueのimportでのみ有効。htmlでは`/src/...`と書くこと。
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
    plugins: [vue(), vueDevTools()],
  };
});
