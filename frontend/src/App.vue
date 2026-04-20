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
  overflow-x: hidden; /* Prevent horizontal scrollbars */
}
.app-root {
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
}
</style>
