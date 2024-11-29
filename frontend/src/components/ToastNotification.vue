<template>
  <div v-if="show" :class="['toast-notification', type]">
    {{ message }}
  </div>
</template>

<script>
export default {
  name: 'ToastNotification',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    message: {
      type: String,
      required: true
    },
    type: {
      type: String,
      default: 'info',
      validator: function(value) {
        return ['success', 'error', 'info'].indexOf(value) !== -1
      }
    }
  }
}
</script>

<style scoped>
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 25px;
  border-radius: 4px;
  color: white;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

.success {
  background-color: #28a745;
}

.error {
  background-color: #dc3545;
}

.info {
  background-color: #17a2b8;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
