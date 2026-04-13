<script setup lang="ts">
// The App layout is now just a container for the routed views.
// Navigation headers are moved directly to their respective views to completely separate them.
</script>

<template>
  <div class="app-root">
    <router-view></router-view>
  </div>
</template>

<style>
/* Global reset and app-root styles */
body, html {
  margin: 0;
  padding: 0;
  height: 100%;
}
.app-root {
  height: 100vh;
  width: 100vw;
}
</style>
