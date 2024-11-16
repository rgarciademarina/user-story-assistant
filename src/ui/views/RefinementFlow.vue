<template>
  <div>
    <h1>Refinamiento de Historia de Usuario</h1>

    <!-- Paso 1: Mejora de Definición -->
    <div v-if="currentStep === 'Mejora de Definición'">
      <UserStoryForm @submit="handleStep1" />
      <div v-if="refinedStory">
        <h2>Historia Refinada</h2>
        <p>{{ refinedStory }}</p>
        <button @click="confirmStep1">Estoy de acuerdo</button>
      </div>
    </div>

    <!-- Paso 2: Identificación de Casos Esquinas -->
    <div v-if="currentStep === 'Identificación de Casos Esquinas'">
      <h2>Casos Esquinas Identificados</h2>
      <ul>
        <li v-for="(case, index) in cornerCases" :key="index">{{ case }}</li>
      </ul>
      <button @click="confirmStep2">Estoy de acuerdo</button>
    </div>

    <!-- Paso 3: Estrategia de Testing -->
    <div v-if="currentStep === 'Estrategia de Testing'">
      <h2>Estrategias de Testing Recomendadas</h2>
      <ul>
        <li v-for="(strategy, index) in testingStrategies" :key="index">{{ strategy }}</li>
      </ul>
      <button @click="confirmStep3">Estoy de acuerdo</button>
    </div>

    <!-- Finalización -->
    <div v-if="isCompleted">
      <h2>Proceso de Refinamiento Completado</h2>
      <p>La historia de usuario ha sido refinada exitosamente.</p>
    </div>
  </div>
</template>

<script>
import UserStoryForm from '../components/UserStoryForm.vue';
import axios from 'axios';

export default {
  components: {
    UserStoryForm,
  },
  data() {
    return {
      currentStep: 'Mejora de Definición',
      refinedStory: '',
      cornerCases: [],
      testingStrategies: [],
      isCompleted: false,
    };
  },
  methods: {
    async handleStep1(userStory) {
      try {
        const response = await axios.post('http://localhost:8000/api/refine_story', { story: userStory });
        this.refinedStory = response.data.refined_story;
      } catch (error) {
        console.error('Error al refinar la historia de usuario:', error);
      }
    },
    confirmStep1() {
      this.currentStep = 'Identificación de Casos Esquinas';
      this.fetchCornerCases();
    },
    async fetchCornerCases() {
      try {
        const response = await axios.post('http://localhost:8000/api/identify_corner_cases', { story: this.refinedStory });
        this.cornerCases = response.data.corner_cases;
      } catch (error) {
        console.error('Error al identificar casos esquinas:', error);
      }
    },
    confirmStep2() {
      this.currentStep = 'Estrategia de Testing';
      this.fetchTestingStrategies();
    },
    async fetchTestingStrategies() {
      try {
        const response = await axios.post('http://localhost:8000/api/propose_testing_strategy', {
          story: this.refinedStory,
          corner_cases: this.cornerCases,
        });
        this.testingStrategies = response.data.testing_strategies;
      } catch (error) {
        console.error('Error al proponer estrategias de testing:', error);
      }
    },
    confirmStep3() {
      this.isCompleted = true;
    },
  },
};
</script>

<style scoped>
h1, h2 {
  color: #333;
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
