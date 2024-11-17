<template>
  <div id="app">
    <RefinementFlow />
  </div>
</template>

<script>
import RefinementFlow from './components/RefinementFlow.vue';

export default {
  name: 'App',
  components: {
    RefinementFlow,
  },
};
</script>

<style>
/* Global styles */
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  margin: 0;
  padding: 20px;
  background-color: #f9f9f9;
}
#app {
  max-width: 800px;
  margin: 0 auto;
}
</style>
