import { sentryVitePlugin } from "@sentry/vite-plugin"
import { sentryVitePlugin } from "@sentry/vite-plugin"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tsconfigPaths from "vite-tsconfig-paths"

// https://vitejs.dev/config/
export default defineConfig({
  base: "/",
  plugins: [
    react(),
    tsconfigPaths(),
    sentryVitePlugin({
      org: "betagouv",
      project: "carburebetagouvfr",
      url: "https://sentry.incubateur.net",
      sourcemaps: {
        filesToDeleteAfterUpload: ["build/**/*.map"],
      },
    }),
  ],
  plugins: [
    react(),
    tsconfigPaths(),
    sentryVitePlugin({
      org: "betagouv",
      project: "carburebetagouvfr",
      url: "https://sentry.incubateur.net",
      sourcemaps: {
        filesToDeleteAfterUpload: ["build/**/*.map"],
      },
    }),
  ],
  server: {
    host: true,
    port: 3000,
    hmr: {
      path: "/ws",
    },
  },
  build: {
    outDir: "./build",
    emptyOutDir: true,


    rollupOptions: {
      output: {
        assetFileNames: "static/[name].[hash][extname]", // Place les assets dans un dossier "static"
        chunkFileNames: "static/[name].[hash].js", // Place les chunks JavaScript dans "static"
        entryFileNames: "static/[name].[hash].js", // Place les fichiers d'entrée dans "static"
      },
    },
    assetsInlineLimit: 0,

    sourcemap: "hidden",
  },
})
