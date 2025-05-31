<template>
  <!-- Swipe detection overlay that allows clicks to pass through -->
  <div
    class="swipe-navigation-overlay"
    @touchstart="handleTouchStart"
    @touchmove="handleTouchMove"
    @touchend="handleTouchEnd"
    @click="handleClick"
  ></div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'SwipeNavigationComponent',
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    // Touch tracking variables
    const touchStartX = ref(0);
    const touchStartY = ref(0);
    const touchStartTime = ref(0);
    const isSwipeGesture = ref(false);

    // Define the navigation pages in order (same as bottom navbar)
    const navPages = [
      { name: 'home' },
      { name: 'activities' },
      { name: 'gears' },
      { name: 'health' },
      { name: 'menu' }
    ];

    // Swipe detection thresholds
    const SWIPE_THRESHOLD = 50; // Minimum distance for swipe
    const SWIPE_TIME_THRESHOLD = 300; // Maximum time for swipe (ms)
    const VERTICAL_THRESHOLD = 100; // Maximum vertical movement for horizontal swipe

    // Helper function to find the current page index in the navigation array
    const getCurrentPageIndex = () => {
      const currentRoute = router.currentRoute.value.name;
      return navPages.findIndex(page => page.name === currentRoute);
    };

    // Handle touch start
    const handleTouchStart = (event) => {
      // Only handle single touch
      if (event.touches.length !== 1) return;

      const touch = event.touches[0];
      touchStartX.value = touch.clientX;
      touchStartY.value = touch.clientY;
      touchStartTime.value = Date.now();
      isSwipeGesture.value = false;
    };

    // Handle touch move
    const handleTouchMove = (event) => {
      // Only handle single touch
      if (event.touches.length !== 1) return;

      const touch = event.touches[0];
      const deltaX = Math.abs(touch.clientX - touchStartX.value);
      const deltaY = Math.abs(touch.clientY - touchStartY.value);

      // If horizontal movement is significant and vertical movement is minimal,
      // this might be a swipe gesture
      if (deltaX > 10 && deltaY < VERTICAL_THRESHOLD) {
        isSwipeGesture.value = true;
        // Prevent scrolling during horizontal swipe
        event.preventDefault();
      }
    };

    // Handle touch end
    const handleTouchEnd = (event) => {
      // Only handle if we detected a potential swipe
      if (!isSwipeGesture.value) return;

      const touch = event.changedTouches[0];
      const deltaX = touch.clientX - touchStartX.value;
      const deltaY = Math.abs(touch.clientY - touchStartY.value);
      const deltaTime = Date.now() - touchStartTime.value;

      // Check if this qualifies as a swipe
      if (Math.abs(deltaX) >= SWIPE_THRESHOLD &&
          deltaY < VERTICAL_THRESHOLD &&
          deltaTime < SWIPE_TIME_THRESHOLD) {

        // Prevent the touch event from becoming a click
        event.preventDefault();
        event.stopPropagation();

        // Determine swipe direction and navigate
        if (deltaX > 0) {
          handleSwipeRight();
        } else {
          handleSwipeLeft();
        }
      }

      // Reset swipe tracking
      isSwipeGesture.value = false;
    };

    // Handle click events - let them pass through
    const handleClick = (event) => {
      // If this was part of a swipe gesture, prevent the click
      if (isSwipeGesture.value) {
        event.preventDefault();
        event.stopPropagation();
      }
      // Otherwise, let the click pass through to underlying elements
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
      handleTouchStart,
      handleTouchMove,
      handleTouchEnd,
      handleClick
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
  pointer-events: none; /* Allow clicks to pass through by default */
  touch-action: pan-y; /* Allow vertical scrolling */
  display: none; /* Hidden on desktop */
}

/* Only show the swipe overlay on mobile devices */
@media (max-width: 991.98px) {
  .swipe-navigation-overlay {
    display: block;
    pointer-events: auto; /* Enable touch events on mobile only */
  }
}
</style>
