<template>
  <transition-group
    name="list"
    tag="div"
    class="animated-list"
    @before-enter="beforeEnter"
    @enter="enter"
    @leave="leave"
  >
    <slot />
  </transition-group>
</template>

<script setup lang="ts">
const beforeEnter = (el: Element) => {
  const element = el as HTMLElement
  element.style.opacity = '0'
  element.style.transform = 'translateY(30px)'
}

const enter = (el: Element, done: () => void) => {
  const element = el as HTMLElement
  const delay = parseInt(element.dataset.index || '0') * 50
  
  setTimeout(() => {
    element.style.transition = 'all 0.4s ease-out'
    element.style.opacity = '1'
    element.style.transform = 'translateY(0)'
    
    setTimeout(done, 400)
  }, delay)
}

const leave = (el: Element, done: () => void) => {
  const element = el as HTMLElement
  element.style.transition = 'all 0.3s ease-in'
  element.style.opacity = '0'
  element.style.transform = 'translateX(-30px)'
  
  setTimeout(done, 300)
}
</script>

<style scoped>
.animated-list {
  position: relative;
}

/* List transition styles */
.list-move {
  transition: transform 0.4s ease;
}

.list-enter-active,
.list-leave-active {
  transition: all 0.4s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* Ensure smooth repositioning */
.list-leave-active {
  position: absolute;
  width: 100%;
}
</style>