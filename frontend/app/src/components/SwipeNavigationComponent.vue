<template>
  <!-- Transparent overlay that captures swipe events, positioned over the entire page -->
  <div 
    class="swipe-navigation-overlay" 
    v-touch:swipe.left="handleSwipeLeft"
    v-touch:swipe.right="handleSwipeRight"
  ></div>
</template>

<script>
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'SwipeNavigationComponent',
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    // Define the navigation pages in order (same as bottom navbar)
    const navPages = [
      { name: 'home' },
      { name: 'activities' },
      { name: 'gears' },
      { name: 'health' },
      { name: 'menu' }
    ];

    // Helper function to find the current page index in the navigation array
    const getCurrentPageIndex = () => {
      const currentRoute = router.currentRoute.value.name;
      return navPages.findIndex(page => page.name === currentRoute);
    };

    // Handle swipe left (navigate to next page)
    const handleSwipeLeft = () => {
      // Only navigate if user is authenticated
      if (!authStore.isAuthenticated) return;
      
      const currentIndex = getCurrentPageIndex();
      
      // If current page is in our navigation array and not the last page
      if (currentIndex !== -1 && currentIndex < navPages.length - 1) {
        router.push({ name: navPages[currentIndex + 1].name });
      }
    };

    // Handle swipe right (navigate to previous page)
    const handleSwipeRight = () => {
      // Only navigate if user is authenticated
      if (!authStore.isAuthenticated) return;
      
      const currentIndex = getCurrentPageIndex();
      
      // If current page is in our navigation array and not the first page
      if (currentIndex > 0) {
        router.push({ name: navPages[currentIndex - 1].name });
      }
    };

    return {
      handleSwipeLeft,
      handleSwipeRight
    };
  }
};
</script>

<style scoped>
.swipe-navigation-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000; /* High enough to capture events but below modal dialogs */
  pointer-events: auto; /* Captures swipe events */
  touch-action: pan-y; /* Allow vertical scrolling */
  display: none; /* Hidden on desktop */
}

/* Only show the swipe overlay on mobile devices */
@media (max-width: 991.98px) {
  .swipe-navigation-overlay {
    display: block;
  }
}
</style>
