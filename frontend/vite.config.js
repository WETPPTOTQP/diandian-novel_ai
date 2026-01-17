import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  optimizeDeps: {
    include: ['@tiptap/vue-3', '@tiptap/starter-kit', '@tiptap/extension-bubble-menu'],
  },
  server: {
    port: 5173
  }
});

