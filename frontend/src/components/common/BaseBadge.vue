<template>
  <span :class="['badge', `bg-${variant}`, { 'rounded-pill': pill }]">
    <slot></slot>
  </span>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark'].includes(value)
  },
  pill: {
    type: Boolean,
    default: true
  }
})
</script>
