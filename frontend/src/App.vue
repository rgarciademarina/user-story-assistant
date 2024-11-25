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
  padding: 0;
  background-color: #1e1e1e;
  color: #fff;
  height: 100vh;
  overflow: hidden;
}

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
</style>
