<template>
  <button class="fancy-circle-btn" @click.stop="emit('click', $event)" :disabled="disabled">
    <span class="circle-base"></span>
    <span class="circle-top">
      <slot />
    </span>
  </button>
</template>

<script setup>
defineOptions({ inheritAttrs: false })
const emit = defineEmits(['click'])
const props = defineProps({
  disabled: Boolean
})
</script>

<style scoped>
.fancy-circle-btn {
  position: relative;
  width: 56px;
  height: 56px;
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
  outline: none;
  display: inline-block;
}
.fancy-circle-btn:disabled {
  opacity: 0.8;
  cursor: not-allowed;
}
.circle-base {
  position: absolute;
  left: 0; top: 0;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #AE8C6C;
  z-index: 1;
}
.circle-top {
  position: absolute;
  left: 5px; top: 2px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #CCCEFF;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: bold;
  color: #222;
  user-select: none;
}
</style> 