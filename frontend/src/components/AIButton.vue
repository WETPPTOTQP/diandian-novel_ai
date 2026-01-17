<template>
  <button :disabled="loading" @click="run">
    {{ loading ? "生成中..." : "AI 续写" }}
  </button>
</template>

<script setup>
import { ref } from "vue";
import { aiApi } from "../api/index.js";

const props = defineProps({
  text: { type: String, default: "" }
});
const emit = defineEmits(["apply"]);

const loading = ref(false);

async function run() {
  loading.value = true;
  try {
    const res = await aiApi.generate({
      mode: "continue",
      stream: false,
      context: { previous_text: props.text, style: "normal" }
    });
    emit("apply", (props.text || "") + "\n" + (res?.data?.content || ""));
  } finally {
    loading.value = false;
  }
}
</script>

