<template>
  <div class="container mt-4">
    <h1>Swipe Navigation Test</h1>
    <p class="text-muted">This page tests that swipe navigation works without breaking click functionality.</p>
    
    <div class="row">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5>Click Test</h5>
          </div>
          <div class="card-body">
            <p>These links should work normally when clicked/tapped:</p>
            <ul class="list-group">
              <li class="list-group-item">
                <router-link :to="{ name: 'home' }" class="btn btn-primary me-2">
                  Go to Home
                </router-link>
                <span>Should navigate to home page</span>
              </li>
              <li class="list-group-item">
                <router-link :to="{ name: 'activities' }" class="btn btn-success me-2">
                  Go to Activities
                </router-link>
                <span>Should navigate to activities page</span>
              </li>
              <li class="list-group-item">
                <button @click="handleButtonClick" class="btn btn-warning me-2">
                  Test Button
                </button>
                <span>Clicked: {{ buttonClickCount }} times</span>
              </li>
              <li class="list-group-item">
                <a href="#" @click.prevent="handleLinkClick" class="btn btn-info me-2">
                  Test Link
                </a>
                <span>Clicked: {{ linkClickCount }} times</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5>Swipe Test</h5>
          </div>
          <div class="card-body">
            <p>On mobile devices, try swiping left/right on this page:</p>
            <ul class="list-group">
              <li class="list-group-item">
                <strong>Swipe Left:</strong> Should go to next page in navigation
              </li>
              <li class="list-group-item">
                <strong>Swipe Right:</strong> Should go to previous page in navigation
              </li>
              <li class="list-group-item">
                <strong>Vertical Scroll:</strong> Should work normally
              </li>
              <li class="list-group-item">
                <strong>Tap/Click:</strong> Should not interfere with swipe detection
              </li>
            </ul>
            
            <div class="mt-3">
              <h6>Current Page: {{ currentRoute }}</h6>
              <p class="text-muted">
                Navigation order: Home → Activities → Gears → Health → Menu
              </p>

              <!-- iOS PWA Detection -->
              <div class="alert alert-info mt-2">
                <strong>Environment:</strong><br>
                PWA: {{ isPWA ? 'Yes' : 'No' }}<br>
                iOS: {{ isIOS ? 'Yes' : 'No' }}<br>
                Mobile: {{ isMobile ? 'Yes' : 'No' }}<br>
                User Agent: {{ userAgent.substring(0, 50) }}...
              </div>

              <!-- Touch Status -->
              <div class="alert alert-secondary mt-2">
                <strong>Touch Status:</strong><br>
                Touch Active: {{ touchActive ? 'Yes' : 'No' }}<br>
                Swipe in Progress: {{ swipeInProgress ? 'Yes' : 'No' }}<br>
                Last Touch: {{ lastTouchInfo }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="row mt-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5>Event Log</h5>
          </div>
          <div class="card-body">
            <div class="event-log" style="height: 200px; overflow-y: auto; background: #f8f9fa; padding: 10px; border-radius: 4px;">
              <div v-for="(event, index) in eventLog" :key="index" class="mb-1">
                <small class="text-muted">{{ event.timestamp }}</small> - {{ event.message }}
              </div>
            </div>
            <button @click="clearLog" class="btn btn-sm btn-secondary mt-2">Clear Log</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

export default {
  name: 'SwipeTestView',
  setup() {
    const router = useRouter();
    const route = useRoute();
    
    const buttonClickCount = ref(0);
    const linkClickCount = ref(0);
    const eventLog = ref([]);
    const touchActive = ref(false);
    const swipeInProgress = ref(false);
    const lastTouchInfo = ref('None');

    const currentRoute = computed(() => route.name);

    // Environment detection
    const isPWA = computed(() => {
      return window.matchMedia('(display-mode: standalone)').matches ||
             window.navigator.standalone ||
             document.referrer.includes('android-app://');
    });

    const isIOS = computed(() => {
      return /iPad|iPhone|iPod/.test(navigator.userAgent) ||
             (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    });

    const isMobile = computed(() => {
      return window.innerWidth <= 991.98;
    });

    const userAgent = computed(() => {
      return navigator.userAgent;
    });
    
    const addToLog = (message) => {
      const timestamp = new Date().toLocaleTimeString();
      eventLog.value.unshift({ timestamp, message });
      // Keep only last 50 events
      if (eventLog.value.length > 50) {
        eventLog.value = eventLog.value.slice(0, 50);
      }
    };
    
    const handleButtonClick = () => {
      buttonClickCount.value++;
      addToLog(`Button clicked (count: ${buttonClickCount.value})`);
    };
    
    const handleLinkClick = () => {
      linkClickCount.value++;
      addToLog(`Link clicked (count: ${linkClickCount.value})`);
    };
    
    const clearLog = () => {
      eventLog.value = [];
      addToLog('Event log cleared');
    };
    
    // Touch event tracking
    const handleTestTouchStart = (event) => {
      touchActive.value = true;
      const touch = event.touches[0];
      lastTouchInfo.value = `Start: ${touch.clientX}, ${touch.clientY}`;
      addToLog(`Touch Start: ${touch.clientX}, ${touch.clientY}`);
    };

    const handleTestTouchMove = (event) => {
      if (touchActive.value) {
        const touch = event.touches[0];
        lastTouchInfo.value = `Move: ${touch.clientX}, ${touch.clientY}`;
      }
    };

    const handleTestTouchEnd = (event) => {
      touchActive.value = false;
      swipeInProgress.value = false;
      const touch = event.changedTouches[0];
      lastTouchInfo.value = `End: ${touch.clientX}, ${touch.clientY}`;
      addToLog(`Touch End: ${touch.clientX}, ${touch.clientY}`);
    };

    onMounted(() => {
      addToLog('SwipeTestView mounted - ready for testing');
      addToLog(`Environment: PWA=${isPWA.value}, iOS=${isIOS.value}, Mobile=${isMobile.value}`);

      // Add touch listeners for testing
      document.addEventListener('touchstart', handleTestTouchStart, { passive: true });
      document.addEventListener('touchmove', handleTestTouchMove, { passive: true });
      document.addEventListener('touchend', handleTestTouchEnd, { passive: true });
    });

    onUnmounted(() => {
      // Clean up test listeners
      document.removeEventListener('touchstart', handleTestTouchStart);
      document.removeEventListener('touchmove', handleTestTouchMove);
      document.removeEventListener('touchend', handleTestTouchEnd);
    });
    
    return {
      buttonClickCount,
      linkClickCount,
      eventLog,
      currentRoute,
      touchActive,
      swipeInProgress,
      lastTouchInfo,
      isPWA,
      isIOS,
      isMobile,
      userAgent,
      handleButtonClick,
      handleLinkClick,
      clearLog
    };
  }
};
</script>

<style scoped>
.event-log {
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}
</style>
