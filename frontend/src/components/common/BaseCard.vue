<template>
  <div class="card mb-3 h-100 shadow-sm">
    <div v-if="$slots.header || title" class="card-header bg-white">
      <slot name="header">
        <h5 v-if="title" class="card-title mb-0">{{ title }}</h5>
      </slot>
    </div>
    <div class="card-body">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" class="card-footer bg-white border-top-0">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
    title: {
        type: String,
        default: ''
    }
})
</script>
