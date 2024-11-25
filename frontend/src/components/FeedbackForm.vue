<template>
    <div>
      <label for="feedback">Proporciona Feedback (Opcional):</label>
      <textarea id="feedback" v-model="feedback"></textarea>
      <button @click="submitFeedback">Enviar Feedback</button>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        feedback: '',
      };
    },
    methods: {
      submitFeedback() {
        this.$emit('submit', this.feedback);
        this.feedback = '';
      },
    },
  };
  </script>
  
  <style scoped>
  /* Estilos personalizados */
  label {
    display: block;
    margin-top: 10px;
  }
  textarea {
    width: 100%;
    min-height: 80px;
  }
  button {
    margin-top: 10px;
    padding: 10px 20px;
    background-color: #42b983;
    color: white;
    border: none;
    cursor: pointer;
  }
  button:hover {
    background-color: #358a6b;
  }
  </style>