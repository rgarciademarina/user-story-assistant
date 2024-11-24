<template>
    <div>
      <form @submit.prevent novalidate>
        <label for="story">Historia de Usuario:</label>
        <textarea 
          id="story" 
          v-model="localStory" 
          required
          :class="{ 'error': showError }"
        ></textarea>
        <span v-if="showError" class="error-message">La historia de usuario es requerida</span>
    
        <label for="feedback">Feedback (Opcional):</label>
        <textarea id="feedback" v-model="localFeedback"></textarea>
    
        <button type="button" :disabled="!isValid" @click="submitForm">Enviar</button>
      </form>
    </div>
</template>
  
<script>
const initialState = {
  localStory: '',
  localFeedback: '',
  showError: false
}

export default {
  name: 'UserStoryForm',
  data() {
    return { ...initialState }
  },
  computed: {
    isValid() {
      return this.localStory.trim().length > 0;
    }
  },
  methods: {
    submitForm() {
      if (!this.isValid) {
        this.showError = true;
        return;
      }
      
      const story = this.localStory.trim();
      const feedback = this.localFeedback.trim();
      
      console.log('UserStoryForm - submitForm - localStory:', story);
      console.log('UserStoryForm - submitForm - localFeedback:', feedback);
      
      this.$emit('submit', {
        story,
        feedback,
      });
      
      this.showError = false;
      this.localFeedback = '';
    },
    validateForm() {
      this.showError = !this.isValid;
    }
  },
  watch: {
    localStory(newValue) {
      if (this.showError && this.isValid) {
        this.showError = false;
      }
    }
  }
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
textarea.error {
  border-color: red;
}
.error-message {
  color: red;
  font-size: 0.8em;
  display: block;
  margin-top: 5px;
}
button {
  margin-top: 10px;
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
}
button:hover:not(:disabled) {
  background-color: #358a6b;
}
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>