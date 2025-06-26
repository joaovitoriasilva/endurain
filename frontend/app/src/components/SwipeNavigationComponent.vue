<template>
  <!-- iOS PWA compatible swipe detection -->
  <div
    v-if="shouldShowOverlay"
    class="swipe-navigation-overlay"
    ref="swipeOverlay"
  ></div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'SwipeNavigationComponent',
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const swipeOverlay = ref(null);

    // Touch tracking variables
    const touchStartX = ref(0);
    const touchStartY = ref(0);
    const touchStartTime = ref(0);
    const isSwipeGesture = ref(false);
    const isTouchActive = ref(false);
    const swipeInProgress = ref(false);

    // Define the navigation pages in order (same as bottom navbar)
    const navPages = [
      { name: 'home' },
      { name: 'activities' },
      { name: 'gears' },
      { name: 'health' },
      { name: 'menu' }
    ];

    // iOS PWA optimized thresholds
    const SWIPE_THRESHOLD = 30; // Lower threshold for iOS
    const SWIPE_TIME_THRESHOLD = 500; // More time for iOS PWA
    const VERTICAL_THRESHOLD = 100; // Allow more vertical movement
    const MIN_HORIZONTAL_MOVEMENT = 20; // Minimum to start detecting swipe

    // Computed property to determine if overlay should be shown
    const shouldShowOverlay = computed(() => {
      return window.innerWidth <= 991.98 && authStore.isAuthenticated;
    });

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

    // Check if we're on iOS
    const isIOS = () => {
      return /iPad|iPhone|iPod/.test(navigator.userAgent) ||
             (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    };

    // Enhanced touch start handler for iOS PWA
    const handleTouchStart = (event) => {
      // Only handle single touch
      if (event.touches.length !== 1) return;

      // Only process if user is authenticated and on a navigation page
      if (!authStore.isAuthenticated) return;

      const currentIndex = getCurrentPageIndex();
      if (currentIndex === -1) return;

      const touch = event.touches[0];
      touchStartX.value = touch.clientX;
      touchStartY.value = touch.clientY;
      touchStartTime.value = Date.now();
      isSwipeGesture.value = false;
      isTouchActive.value = true;
      swipeInProgress.value = false;

      // Debug logging
      console.log('Touch Start:', {
        x: touch.clientX,
        y: touch.clientY,
        isPWA: isPWA(),
        isIOS: isIOS(),
        page: router.currentRoute.value.name
      });
    };

    // Enhanced touch move handler for iOS PWA
    const handleTouchMove = (event) => {
      // Only handle single touch and if touch is active
      if (event.touches.length !== 1 || !isTouchActive.value) return;

      const touch = event.touches[0];
      const deltaX = touch.clientX - touchStartX.value;
      const deltaY = touch.clientY - touchStartY.value;
      const absDeltaX = Math.abs(deltaX);
      const absDeltaY = Math.abs(deltaY);

      // Start detecting horizontal swipe if movement is significant
      if (absDeltaX > MIN_HORIZONTAL_MOVEMENT && !swipeInProgress.value) {
        // Check if this is more horizontal than vertical
        if (absDeltaX > absDeltaY) {
          swipeInProgress.value = true;
          isSwipeGesture.value = true;

          // Prevent default to stop scrolling during swipe
          event.preventDefault();

          console.log('Swipe Started:', { deltaX, deltaY, absDeltaX, absDeltaY });
        }
      }

      // If we're in a swipe, continue preventing default
      if (swipeInProgress.value) {
        event.preventDefault();
        console.log('Swipe In Progress:', { deltaX, deltaY });
      }
    };

    // Enhanced touch end handler for iOS PWA
    const handleTouchEnd = (event) => {
      const wasSwipeInProgress = swipeInProgress.value;
      const wasSwipeGesture = isSwipeGesture.value;

      // Reset all touch states
      isTouchActive.value = false;
      swipeInProgress.value = false;

      // Only process if we had a swipe in progress
      if (!wasSwipeInProgress || !wasSwipeGesture) {
        isSwipeGesture.value = false;
        return;
      }

      const touch = event.changedTouches[0];
      const deltaX = touch.clientX - touchStartX.value;
      const deltaY = touch.clientY - touchStartY.value;
      const absDeltaX = Math.abs(deltaX);
      const absDeltaY = Math.abs(deltaY);
      const deltaTime = Date.now() - touchStartTime.value;

      console.log('Touch End Analysis:', {
        deltaX,
        deltaY,
        absDeltaX,
        absDeltaY,
        deltaTime,
        threshold: SWIPE_THRESHOLD,
        verticalThreshold: VERTICAL_THRESHOLD,
        timeThreshold: SWIPE_TIME_THRESHOLD
      });

      // Check if this qualifies as a completed swipe
      if (absDeltaX >= SWIPE_THRESHOLD &&
          absDeltaY < VERTICAL_THRESHOLD &&
          deltaTime < SWIPE_TIME_THRESHOLD) {

        // Prevent the touch event from becoming a click
        event.preventDefault();
        event.stopPropagation();

        // Determine swipe direction and navigate
        const direction = deltaX > 0 ? 'right' : 'left';
        console.log('Navigation triggered:', direction);

        if (deltaX > 0) {
          handleSwipeRight();
        } else {
          handleSwipeLeft();
        }
      } else {
        console.log('Swipe not qualified:', {
          distanceOk: absDeltaX >= SWIPE_THRESHOLD,
          verticalOk: absDeltaY < VERTICAL_THRESHOLD,
          timeOk: deltaTime < SWIPE_TIME_THRESHOLD
        });
      }

      // Reset swipe tracking
      isSwipeGesture.value = false;
    };

    // Handle swipe left (navigate to next page)
    const handleSwipeLeft = () => {
      console.log('Swipe Left - navigating to next page');
      const currentIndex = getCurrentPageIndex();

      // If current page is in our navigation array and not the last page
      if (currentIndex !== -1 && currentIndex < navPages.length - 1) {
        const nextPage = navPages[currentIndex + 1].name;
        console.log(`Navigating from ${router.currentRoute.value.name} to ${nextPage}`);
        router.push({ name: nextPage });
      } else {
        console.log('Cannot navigate left - at last page or invalid page');
      }
    };

    // Handle swipe right (navigate to previous page)
    const handleSwipeRight = () => {
      console.log('Swipe Right - navigating to previous page');
      const currentIndex = getCurrentPageIndex();

      // If current page is in our navigation array and not the first page
      if (currentIndex > 0) {
        const prevPage = navPages[currentIndex - 1].name;
        console.log(`Navigating from ${router.currentRoute.value.name} to ${prevPage}`);
        router.push({ name: prevPage });
      } else {
        console.log('Cannot navigate right - at first page or invalid page');
      }
    };

    // Setup touch event listeners for iOS PWA compatibility
    onMounted(() => {
      console.log('SwipeNavigationComponent mounted', {
        isPWA: isPWA(),
        isIOS: isIOS(),
        windowWidth: window.innerWidth,
        userAgent: navigator.userAgent
      });

      // Add touch listeners to the main container or body for iOS PWA
      const targetElement = document.body;

      if (targetElement) {
        // Use non-passive listeners for better control
        targetElement.addEventListener('touchstart', handleTouchStart, { passive: false });
        targetElement.addEventListener('touchmove', handleTouchMove, { passive: false });
        targetElement.addEventListener('touchend', handleTouchEnd, { passive: false });

        console.log('Touch event listeners added to body');
      }
    });

    onUnmounted(() => {
      console.log('SwipeNavigationComponent unmounted - cleaning up listeners');

      // Clean up listeners
      const targetElement = document.body;
      if (targetElement) {
        targetElement.removeEventListener('touchstart', handleTouchStart);
        targetElement.removeEventListener('touchmove', handleTouchMove);
        targetElement.removeEventListener('touchend', handleTouchEnd);
      }
    });

    return {
      shouldShowOverlay,
      swipeOverlay
    };
  }
};
</script>

<style scoped>
.swipe-navigation-overlay {
  /* Minimal overlay for visual debugging only */
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -1; /* Behind everything - not used for event capture */
  pointer-events: none; /* Never interfere with clicks */
  display: none; /* Hidden by default */
  background: transparent;
}

/* Show overlay on mobile for debugging (optional) */
@media (max-width: 991.98px) {
  .swipe-navigation-overlay {
    display: block;
  }
}

/* Global iOS PWA touch optimizations */
@media (display-mode: standalone) {
  :global(body) {
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -webkit-tap-highlight-color: transparent;
    touch-action: pan-y; /* Allow vertical scrolling, capture horizontal */
  }
}

/* iOS specific optimizations */
@supports (-webkit-touch-callout: none) {
  :global(body) {
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -webkit-tap-highlight-color: transparent;
  }
}
</style>
