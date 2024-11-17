<template>
    <form @submit.prevent="submitForm">
      <label for="story">Historia de Usuario:</label>
      <textarea id="story" v-model="localStory" required></textarea>
  
      <label for="feedback">Feedback (Opcional):</label>
      <textarea id="feedback" v-model="localFeedback"></textarea>
  
      <button type="submit">Enviar</button>
    </form>
  </template>
  
  <script>
  export default {
    data() {
      return {
        localStory: '',
        localFeedback: '',
      };
    },
    methods: {
      submitForm() {
        console.log('UserStoryForm - submitForm - localStory:', this.localStory);
        console.log('UserStoryForm - submitForm - localFeedback:', this.localFeedback);
        this.$emit('submit', {
          story: this.localStory,
          feedback: this.localFeedback,
        });
        this.localFeedback = '';
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
    min-height: 100px;
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