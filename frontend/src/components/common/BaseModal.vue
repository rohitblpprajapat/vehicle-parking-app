<template>
  <div class="modal fade show d-block" tabindex="-1" aria-modal="true" role="dialog" @click="$emit('close')">
    <div class="modal-dialog modal-dialog-centered" @click.stop>
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <slot name="title">{{ title }}</slot>
          </h5>
          <button type="button" class="btn-close" aria-label="Close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <slot></slot>
        </div>
        <div class="modal-footer" v-if="$slots.footer">
          <slot name="footer"></slot>
        </div>
      </div>
    </div>
  </div>
  <div class="modal-backdrop fade show"></div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'

defineProps({
  title: {
    type: String,
    default: 'Modal Title'
  }
})

defineEmits(['close'])

// Prevent body scrolling when modal is open
onMounted(() => {
  document.body.classList.add('modal-open')
})

onUnmounted(() => {
  document.body.classList.remove('modal-open')
})
</script>

<style scoped>
/* Bootstrap handles styling, we just added the backdrop logic */
</style>
