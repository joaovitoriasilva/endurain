<template>
    <div class="row row-gap-3">
        <h1>Settings</h1>

        <!-- Include the SettingsSideBarComponent -->
        <SettingsSideBarComponent :activeSection="activeSection" @update-active-section="updateActiveSection" />

        <!-- Include the SettingsUserZone -->
        <SettingsUsersZone v-if="activeSection === 'users' && authStore.user.access_type == 2" />

        <!-- Include the SettingsUserProfileZone -->
        <SettingsUserProfileZone v-if="activeSection === 'myProfile'" />

        <!-- Include the SettingsSecurityZone -->
        <SettingsSecurityZone v-if="activeSection === 'security'" />

        <!-- Include the SettingsIntegrationsZone -->
        <SettingsIntegrationsZone v-if="activeSection === 'integrations'" />
    </div>
    <!-- back button -->
    <BackButtonComponent />
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
// Importing the store
import { useAuthStore } from '@/stores/authStore';
// Importing the utils
import { addToast } from '@/utils/toastUtils';
// Importing the services
import { strava } from '@/services/strava';
// Importing the components
import SettingsSideBarComponent from '../components/Settings/SettingsSideBarComponent.vue';
import SettingsUsersZone from '../components/Settings/SettingsUsersZone.vue';
import SettingsUserProfileZone from '../components/Settings/SettingsUserProfileZone.vue';
import SettingsSecurityZone from '../components/Settings/SettingsSecurityZone.vue';
import SettingsIntegrationsZone from '../components/Settings/SettingsIntegrationsZone.vue';
import BackButtonComponent from '@/components/GeneralComponents/BackButtonComponent.vue';

export default {
    components: {
        SettingsSideBarComponent,
        SettingsUsersZone,
        SettingsUserProfileZone,
        SettingsSecurityZone,
        SettingsIntegrationsZone,
        BackButtonComponent,
    },
    setup () {
        const authStore = useAuthStore();
        const route = useRoute();
        const { t } = useI18n();
        const activeSection = ref('users');

        function updateActiveSection(section) {
            activeSection.value = section;
        }

        onMounted(async () => {
            if (authStore.user.access_type === 1) {
                activeSection.value = 'myProfile';
            }

            if (route.query.stravaLinked === '1') {
                activeSection.value = 'integrations';
                // Set the success message and show the success alert.
                addToast(t('settingsIntegrationsZone.successMessageStravaAccountLinked'), 'success', true);

                try {
                    await strava.unsetUniqueUserStateStravaLink();
                } catch (error) {
                    // If there is an error, set the error message and show the error alert.
                    addToast(t('settingsIntegrationsZone.errorMessageUnableToUnSetStravaState'), 'danger', true);
                }
            }
        });

        return {
            authStore,
            activeSection,
            updateActiveSection,
            t,
        };
    },
};
</script>