<template>
  <!-- Swipe detection overlay that allows clicks to pass through -->
  <div
    class="swipe-navigation-overlay"
    @touchstart.passive="handleTouchStart"
    @touchmove="handleTouchMove"
    @touchend.passive="handleTouchEnd"
    @click="handleClick"
  ></div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
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
    const isTouchActive = ref(false);

    // Define the navigation pages in order (same as bottom navbar)
    const navPages = [
      { name: 'home' },
      { name: 'activities' },
      { name: 'gears' },
      { name: 'health' },
      { name: 'menu' }
    ];

    // Swipe detection thresholds (adjusted for iOS PWA)
    const SWIPE_THRESHOLD = 40; // Reduced for better sensitivity on iOS
    const SWIPE_TIME_THRESHOLD = 400; // Increased for iOS PWA
    const VERTICAL_THRESHOLD = 80; // Reduced for better horizontal detection

    // Helper function to find the current page index in the navigation array
    const getCurrentPageIndex = () => {
      const currentRoute = router.currentRoute.value.name;
      return navPages.findIndex(page => page.name === currentRoute);
    };

    // Detect if we're in a PWA environment
    const isPWA = () => {
      return window.matchMedia('(display-mode: standalone)').matches ||
             window.navigator.standalone ||
             document.referrer.includes('android-app://');
    };

    // Handle touch start
    const handleTouchStart = (event) => {
      // Only handle single touch
      if (event.touches.length !== 1) return;

      // Only process if user is authenticated
      if (!authStore.isAuthenticated) return;

      const touch = event.touches[0];
      touchStartX.value = touch.clientX;
      touchStartY.value = touch.clientY;
      touchStartTime.value = Date.now();
      isSwipeGesture.value = false;
      isTouchActive.value = true;

      // Debug logging for PWA
      if (isPWA()) {
        console.log('PWA Touch Start:', { x: touch.clientX, y: touch.clientY });
      }
    };

    // Handle touch move
    const handleTouchMove = (event) => {
      // Only handle single touch and if touch is active
      if (event.touches.length !== 1 || !isTouchActive.value) return;

      // Only process if user is authenticated
      if (!authStore.isAuthenticated) return;

      const touch = event.touches[0];
      const deltaX = Math.abs(touch.clientX - touchStartX.value);
      const deltaY = Math.abs(touch.clientY - touchStartY.value);

      // If horizontal movement is significant and vertical movement is minimal,
      // this might be a swipe gesture
      if (deltaX > 15 && deltaY < VERTICAL_THRESHOLD) {
        isSwipeGesture.value = true;

        // For PWA, we need to be more aggressive about preventing default
        if (isPWA()) {
          event.preventDefault();
          event.stopPropagation();
        } else {
          // Prevent scrolling during horizontal swipe on regular mobile
          event.preventDefault();
        }

        // Debug logging for PWA
        if (isPWA()) {
          console.log('PWA Swipe Detected:', { deltaX, deltaY });
        }
      }
    };

    // Handle touch end
    const handleTouchEnd = (event) => {
      // Reset touch active state
      const wasSwipeGesture = isSwipeGesture.value;
      isTouchActive.value = false;

      // Only process if user is authenticated and we had a potential swipe
      if (!authStore.isAuthenticated || !wasSwipeGesture) {
        isSwipeGesture.value = false;
        return;
      }

      const touch = event.changedTouches[0];
      const deltaX = touch.clientX - touchStartX.value;
      const deltaY = Math.abs(touch.clientY - touchStartY.value);
      const deltaTime = Date.now() - touchStartTime.value;

      // Debug logging for PWA
      if (isPWA()) {
        console.log('PWA Touch End:', {
          deltaX,
          deltaY,
          deltaTime,
          threshold: SWIPE_THRESHOLD,
          verticalThreshold: VERTICAL_THRESHOLD
        });
      }

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

        // Debug logging for PWA
        if (isPWA()) {
          console.log('PWA Navigation triggered:', deltaX > 0 ? 'right' : 'left');
        }
      }

      // Reset swipe tracking
      isSwipeGesture.value = false;
    };

    // Handle click events - let them pass through
    const handleClick = (event) => {
      // If this was part of a swipe gesture, prevent the click
      if (isSwipeGesture.value || isTouchActive.value) {
        event.preventDefault();
        event.stopPropagation();
        return;
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

    // Add global touch event listeners for better PWA support
    onMounted(() => {
      // Only add listeners on mobile/PWA
      if (window.innerWidth <= 991.98 || isPWA()) {
        // Add passive listeners to document for better PWA compatibility
        document.addEventListener('touchstart', handleDocumentTouchStart, { passive: true });
        document.addEventListener('touchmove', handleDocumentTouchMove, { passive: false });
        document.addEventListener('touchend', handleDocumentTouchEnd, { passive: true });
      }
    });

    onUnmounted(() => {
      // Clean up listeners
      document.removeEventListener('touchstart', handleDocumentTouchStart);
      document.removeEventListener('touchmove', handleDocumentTouchMove);
      document.removeEventListener('touchend', handleDocumentTouchEnd);
    });

    // Document-level touch handlers for PWA compatibility
    const handleDocumentTouchStart = (event) => {
      // Only handle if we're in a main navigation page
      const currentIndex = getCurrentPageIndex();
      if (currentIndex === -1) return;

      handleTouchStart(event);
    };

    const handleDocumentTouchMove = (event) => {
      // Only handle if we're tracking a touch
      if (!isTouchActive.value) return;

      handleTouchMove(event);
    };

    const handleDocumentTouchEnd = (event) => {
      // Only handle if we're tracking a touch
      if (!isTouchActive.value) return;

      handleTouchEnd(event);
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
  pointer-events: none; /* Allow clicks to pass through - document listeners handle touch */
  touch-action: pan-y; /* Allow vertical scrolling but capture horizontal */
  display: none; /* Hidden on desktop */
  -webkit-touch-callout: none; /* Disable iOS callout */
  -webkit-user-select: none; /* Disable iOS text selection */
  user-select: none; /* Disable text selection */
}

/* Only show the swipe overlay on mobile devices */
@media (max-width: 991.98px) {
  .swipe-navigation-overlay {
    display: block;
  }
}

/* PWA specific styles - still use pointer-events: none since we use document listeners */
@media (display-mode: standalone) {
  .swipe-navigation-overlay {
    display: block;
    pointer-events: none; /* Document listeners handle touch events */
    touch-action: pan-y; /* Critical for iOS PWA */
    -webkit-overflow-scrolling: touch; /* Enable momentum scrolling */
  }
}

/* iOS specific styles */
@supports (-webkit-touch-callout: none) {
  .swipe-navigation-overlay {
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -webkit-tap-highlight-color: transparent;
  }
}
</style>
