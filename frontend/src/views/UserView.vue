<template>
    <!-- Error alerts -->
    <ErrorToastComponent v-if="errorMessage" />

    <!-- Success banners -->
    <SuccessToastComponent v-if="successMessage" />

    <div class="row align-items-center">
        <!-- picture col -->
        <div class="col">
            <div v-if="isLoading">
                <LoadingComponent />
            </div>
            <div class="vstack d-flex justify-content-center" v-else>
                <div class="d-flex justify-content-center" v-if="userMe">
                    <UserAvatarComponent :userProp="userMe" :width=120 :height=120 />
                </div>
                <div class="text-center mt-3 mb-3" v-if="userMe">
                    <h3>
                        <span>{{ userMe.name }}</span>
                    </h3>
                    <span class="fw-lighter" v-if="userMe.city">
                        <font-awesome-icon :icon="['fas', 'location-dot']" />
                        {{ userMe.city }}
                    </span>
                </div>
            </div>
        </div>
        <div class="col">
            <div v-if="isLoading">
                <LoadingComponent />
            </div>
            <div class="vstack d-flex align-middle text-center" v-else>
                <span class="fw-lighter">
                    {{ $t("user.thisMonthActivitiesNumber") }}
                </span>
                <h1>
                    {{ userThisMonthNumberOfActivities }}
                </h1>
                <div class="row align-items-center">
                    <div class="col">
                        {{ userFollowingCountAccepted }}
                        <br>
                        <span class="fw-lighter">
                            {{ $t("user.userFollowing") }}
                        </span>
                    </div>
                    <div class="col">
                        {{ userFollowersCountAccepted }}
                        <br>
                        <span class="fw-lighter">
                            {{ $t("user.userFollowers") }}
                        </span>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-sm">
            <div v-if="isLoading">
                <LoadingComponent />
            </div>
            <UserDistanceStatsComponent v-else />
        </div>
    </div>

    <!-- navigation -->
    <div v-if="isLoading">
        <LoadingComponent />
    </div>
    <ul class="nav nav-pills mb-3 justify-content-center" id="pills-tab" role="tablist" v-else-if="userMe">
        <li class="nav-item" role="presentation">
            <button class="nav-link active link-body-emphasis" id="pills-activities-tab" data-bs-toggle="pill"
                data-bs-target="#pills-activities" type="button" role="tab" aria-controls="pills-activities"
                aria-selected="true">
                {{ $t("user.navigationActivities") }}
            </button>
        </li>
        <li class="nav-item" role="presentation">
            <button class="nav-link link-body-emphasis" id="pills-following-tab" data-bs-toggle="pill"
                data-bs-target="#pills-following" type="button" role="tab" aria-controls="pills-following"
                aria-selected="false">
                {{ $t("user.navigationFollowing") }}
            </button>
        </li>
        <li class="nav-item" role="presentation">
            <button class="nav-link link-body-emphasis" id="pills-followers-tab" data-bs-toggle="pill"
                data-bs-target="#pills-followers" type="button" role="tab" aria-controls="pills-followers"
                aria-selected="false">
                {{ $t("user.navigationFollowers") }}
            </button>
        </li>
        <li class="nav-item" role="presentation" v-if="userMe.id == loggedUserId">
            <router-link :to="{ name: 'settings', query: { profileSettings: 1 }}" class="btn nav-link link-body-emphasis">
                <font-awesome-icon :icon="['fas', 'fa-gear']" />
                {{ $t("user.navigationUserSettings") }}
            </router-link>
        </li>
        <li class="nav-item" role="presentation" v-if="userMe.id != loggedUserId && userFollowState == null">
            <!-- Follow user button -->
            <a class="btn btn-outline-success h-100 ms-2" href="#" role="button" data-bs-toggle="modal"
                data-bs-target="#followUserModal">
                <font-awesome-icon :icon="['fas', 'fa-user-plus']" />
                {{ $t("user.navigationFollow") }}
            </a>

            <!-- Modal follow user -->
            <div class="modal fade" id="followUserModal" tabindex="-1" aria-labelledby="followUserModal" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h1 class="modal-title fs-5" id="followUserModal">
                                {{ $t("user.modalFollowUserTitle") }}
                            </h1>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            {{ $t("user.modalFollowUserBody") }}<b>{{ userMe.name }}</b>?
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                {{ $t("generalItens.buttonClose") }}
                            </button>
                            <a type="button" class="btn btn-success" data-bs-dismiss="modal" @click="submitFollowUser">
                                {{ $t("user.modalFollowUserTitle") }}
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </li>
        <li class="nav-item" role="presentation" v-if="userMe.id != loggedUserId && userFollowState != null && !userFollowState.is_accepted">
            <!-- Cancel follow request button -->
            <a class="btn btn-outline-secondary h-100 ms-2" href="#" role="button" data-bs-toggle="modal"
                data-bs-target="#cancelFollowUserModal">
                <font-awesome-icon :icon="['fas', 'fa-user-plus']" />
                {{ $t("user.navigationRequestSent") }}
            </a>

            <!-- Modal cancel follow request -->
            <div class="modal fade" id="cancelFollowUserModal" tabindex="-1" aria-labelledby="cancelFollowUserModal" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h1 class="modal-title fs-5" id="cancelFollowUserModal">
                                {{ $t("user.modalCancelFollowRequestTitle") }}
                            </h1>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            {{ $t("user.modalCancelFollowRequestBody") }}<b>{{ userMe.name }}</b>?
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                {{ $t("generalItens.buttonClose") }}
                            </button>
                            <a type="button" class="btn btn-danger" data-bs-dismiss="modal" @click="submitCancelFollowUser">
                                {{ $t("user.modalCancelFollowRequestTitle") }}
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </li>
        <li class="nav-item" role="presentation" v-if="userMe.id != loggedUserId && userFollowState != null && userFollowState.is_accepted">
            <!-- Unfollow user button -->
            <a class="btn btn-outline-danger h-100 ms-2" href="#" role="button" data-bs-toggle="modal"
                data-bs-target="#unfollowUserModal">
                <font-awesome-icon :icon="['fas', 'fa-user-minus']" />
                {{ $t("user.navigationUnfollow") }}
            </a>

            <!-- Modal unfollow user -->
            <div class="modal fade" id="unfollowUserModal" tabindex="-1" aria-labelledby="unfollowUserModal" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h1 class="modal-title fs-5" id="unfollowUserModal">
                                {{ $t("user.modalUnfollowUserTitle") }}
                            </h1>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            {{ $t("user.modalUnfollowUserBody") }}<b>{{ userMe.name }}</b>?
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                {{ $t("generalItens.buttonClose") }}
                            </button>
                            <a type="button" class="btn btn-danger" data-bs-dismiss="modal" @click="submitUnfollowUser">
                                {{ $t("user.modalUnfollowUserTitle") }}
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </li>
    </ul>

    <div v-if="isLoading">
        <LoadingComponent />
    </div>
    <div class="tab-content" id="pills-tabContent" v-else>
        <!-- activities tab content -->
        <div class="tab-pane fade show active" id="pills-activities" role="tabpanel" aria-labelledby="pills-activities-tab" tabindex="0">
            <!-- pagination -->
            <nav>
                <ul class="pagination justify-content-center">
                    <li :class="['page-item', { active: week === 0 }]" >
                        <a href="#" class="page-link link-body-emphasis" @click="setWeek(0, $event)">
                            {{ $t("user.activitiesPaginationWeek0") }}
                        </a>
                    </li>
                    <li v-if="week > 2" class="page-item disabled">
                        <a class="page-link">...</a>
                    </li>
                    <li v-for="i in visibleWeeks" :key="i" :class="['page-item', { active: i === week }]" >
                        <a href="#" class="page-link link-body-emphasis" @click="setWeek(i, $event)">
                            {{ formatDateRange(i) }}
                        </a>
                    </li>
                    <li v-if="week < 49" class="page-item disabled">
                        <a class="page-link">...</a>
                    </li>
                    <li :class="['page-item', { active: week === 51 }]" >
                        <a href="#" class="page-link link-body-emphasis" @click="setWeek(51, $event)">
                            {{ $t("user.activitiesPaginationWeek51") }}
                        </a>
                    </li>
                </ul>
            </nav>

            <!-- Checking if userWeekActivities is loaded and has length -->
            <div v-if="userWeekActivities && userWeekActivities.length">
            <!-- Iterating over userWeekActivities to display them -->
                <div class="card mb-3" v-for="activity in userWeekActivities" :key="activity.id">
                    <div class="card-body">
                        <ActivitySummaryComponent :activity="activity" :source="'home'"/>
                    </div>
                    <ActivityMapComponent class="mx-3 mb-3" :activity="activity" :source="'home'"/>
                </div>
            </div>
            <!-- Displaying a message or component when there are no activities -->
            <NoItemsFoundComponent v-else />
        </div>

        <!-- following tab content -->
        <div class="tab-pane fade" id="pills-following" role="tabpanel" aria-labelledby="pills-following-tab" tabindex="0">
            <ul class="list-group list-group-flush align-items-center" v-if="userFollowersAll && userFollowersAll.length">
                <li class="list-group-item d-flex justify-content-between" v-for="follower in userFollowersAll" :key="follower.following_id">
                    <FollowersListComponent :follower="follower" :type="1" @followingDeleted="updateFollowingList"/>
                </li>
            </ul>
            <!-- Displaying a message or component when there are no following users -->
            <NoItemsFoundComponent v-else />
        </div>

        <!-- followers tab content -->
        <div class="tab-pane fade" id="pills-followers" role="tabpanel" aria-labelledby="pills-followers-tab" tabindex="0">
            <ul class="list-group list-group-flush align-items-center" v-if="userFollowingAll && userFollowingAll.length">
                <li class="list-group-item d-flex justify-content-between" v-for="follower in userFollowingAll" :key="follower.follower_id">
                    <FollowersListComponent :follower="follower" :type="2" @followerDeleted="updateFollowerList" @followerAccepted="updateFollowerListWithAccepted"/>
                </li>
            </ul>
            <!-- Displaying a message or component when there are no following users -->
            <NoItemsFoundComponent v-else />
        </div>
    </div>

    <!-- back button -->
    <BackButtonComponent />
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user';
import { activities } from '@/services/activities';
import { followers } from '@/services/followers';
// Importing the stores
import { useSuccessAlertStore } from '@/stores/Alerts/successAlert';
import { useErrorAlertStore } from '@/stores/Alerts/errorAlert';
// Importing the components
import UserDistanceStatsComponent from '@/components/Activities/UserDistanceStatsComponent.vue';
import LoadingComponent from '@/components/LoadingComponent.vue';
import NoItemsFoundComponent from '@/components/NoItemsFoundComponents.vue';
import ActivitySummaryComponent from '@/components/Activities/ActivitySummaryComponent.vue';
import ActivityMapComponent from '@/components/Activities/ActivityMapComponent.vue';
import ErrorToastComponent from '@/components/Toasts/ErrorToastComponent.vue';
import SuccessToastComponent from '@/components/Toasts/SuccessToastComponent.vue';
import FollowersListComponent from '@/components/Followers/FollowersListComponent.vue';
import BackButtonComponent from '@/components/BackButtonComponent.vue';
import UserAvatarComponent from '@/components/Users/UserAvatarComponent.vue';

export default {
    components: {
        UserDistanceStatsComponent,
        NoItemsFoundComponent,
        LoadingComponent,
        ActivitySummaryComponent,
        ActivityMapComponent,
        FollowersListComponent,
        ErrorToastComponent,
        SuccessToastComponent,
        BackButtonComponent,
        UserAvatarComponent,
    },
    setup () {
        const idFromParam = computed(() => route.params.id);
        const userStore = useUserStore();
        const successAlertStore = useSuccessAlertStore();
        const errorAlertStore = useErrorAlertStore();
        const route = useRoute();
        const loggedUserId = JSON.parse(localStorage.getItem('userMe')).id;
        const userMe = computed(() => userStore.userMe);
        const userThisMonthNumberOfActivities = computed(() => userStore.thisMonthNumberOfActivities);
        const userFollowersCountAccepted = computed(() => userStore.userFollowingCountAccepted);
        const userFollowingCountAccepted = computed(() => userStore.userFollowersCountAccepted);
        const userFollowersAll = computed(() => userStore.userFollowingAll);
        const userFollowingAll = computed(() => userStore.userFollowersAll);
        const isLoading = ref(true);
        const isActivitiesLoading = ref(true);
        const { t } = useI18n();
        const week = ref(0);
        const totalWeeks = 50;
        const weekRange = 1;
        const visibleWeeks = computed(() => {
            let start = Math.max(1, week.value - weekRange);
            let end = Math.min(totalWeeks, week.value + weekRange);
            return Array.from({ length: end - start + 1 }, (_, i) => i + start);
        });
        const userWeekActivities = ref([]);
        const successMessage = ref('');
        const errorMessage = ref('');
        const userFollowState = ref(null);

        const fetchData = async () => {
            isLoading.value = true;
            isActivitiesLoading.value = true;
            week.value = 0;
            try {
                await userStore.fetchUserMe(route.params.id);
                await userStore.fetchUserStats();
                await userStore.fetchUserThisMonthActivitiesNumber();
                await userStore.fetchUserFollowersCountAccepted();
                await userStore.fetchUserFollowingCountAccepted();
                await userStore.fetchUserFollowersAll();
                await userStore.fetchUserFollowingAll();
                userWeekActivities.value = await activities.getUserWeekActivities(userMe.value.id, week.value);
                if (userMe.value.id != loggedUserId) {
                    userFollowState.value = await followers.getUserFollowState(loggedUserId, userMe.value.id);
                }
            } catch (error) {
                errorMessage.value = t('generalItens.errorFetchingInfo') + " - " + error.toString();
                errorAlertStore.setAlertMessage(errorMessage.value);
            }
            isLoading.value = false;
            isActivitiesLoading.value = false;
        };

        onMounted(fetchData);

        watch(() => route.params.id, fetchData);

        function formatDateRange(weekNumber) {
            const today = new Date();
            const currentDay = today.getDay();
            const daysToMonday = currentDay === 0 ? -6 : 1 - currentDay;  // Adjusting for when Sunday is day 0

            const startOfWeek = new Date(today);
            startOfWeek.setDate(today.getDate() + daysToMonday - (weekNumber * 7));

            const endOfWeek = new Date(startOfWeek);
            endOfWeek.setDate(startOfWeek.getDate() + 6);  // Set to Sunday of the same week

            const format = (date) => `${date.getDate().toString().padStart(2, '0')}/${(date.getMonth() + 1).toString().padStart(2, '0')}`;

            return `${format(startOfWeek)}-${format(endOfWeek)}`;
        }

        async function setWeek(newWeek, event) {
            isActivitiesLoading.value = true;
            event.preventDefault();
            week.value = newWeek;

            try{
                userWeekActivities.value = await activities.getUserWeekActivities(userMe.value.id, week.value);
            } catch (error) {
                // Set the error message
                errorMessage.value = t('generalItens.errorFetchingInfo') + " - " + error.toString();
                errorAlertStore.setAlertMessage(errorMessage.value);
            } finally {
                isActivitiesLoading.value = false;
            }
        }

        function updateFollowingList(deletedFollowingId) {
            userStore.userFollowingAll = userStore.userFollowingAll.filter(follower => follower.following_id !== deletedFollowingId);
            userStore.userFollowersCountAccepted -= 1;
            // Set the success message
            successMessage.value = t('user.successFollowingDeleted');
            successAlertStore.setAlertMessage(successMessage.value);
            successAlertStore.setClosableState(true);
        }

        function updateFollowerList(deletedFollowerId){
            userStore.userFollowersAll = userStore.userFollowersAll.filter(follower => follower.follower_id !== deletedFollowerId);
            userStore.userFollowingCountAccepted -= 1;
            // Set the success message
            successMessage.value = t('user.successFollowerDeleted');
            successAlertStore.setAlertMessage(successMessage.value);
            successAlertStore.setClosableState(true);
        }

        function updateFollowerListWithAccepted(acceptedFollowerId){
            userStore.userFollowersAll = userStore.userFollowersAll.map(follower => {
                if (follower.follower_id === acceptedFollowerId) {
                    follower.is_accepted = true;
                }
                return follower;
            });
            userStore.userFollowingCountAccepted += 1;
            // Set the success message
            successMessage.value = t('user.successFollowerAccepted');
            successAlertStore.setAlertMessage(successMessage.value);
            successAlertStore.setClosableState(true);
        }

        async function submitFollowUser() {
            try{
                await followers.createUserFollowsSpecificUser(loggedUserId, userMe.value.id);

                userFollowState.value = 0;

                // Set the success message
                successMessage.value = t('user.successFollowRequestSent');
                successAlertStore.setAlertMessage(successMessage.value);
                successAlertStore.setClosableState(true);
            } catch (error) {
                // Set the error message
                errorMessage.value = t('user.errorUnableToSendFollow') + " - " + error.toString();
                errorAlertStore.setAlertMessage(errorMessage.value);
            }
        }

        async function submitCancelFollowUser() {
            try {
                await followers.deleteUserFollowsSpecificUser(loggedUserId, userMe.value.id);

                userFollowState.value = null;

                // Set the success message
                successMessage.value = t('user.successFollowRequestCancelled');
                successAlertStore.setAlertMessage(successMessage.value);
                successAlertStore.setClosableState(true);
            } catch (error) {
                // Set the error message
                errorMessage.value = t('user.errorUnableToCancelFollowRequest') + " - " + error.toString();
                errorAlertStore.setAlertMessage(errorMessage.value);
            }
        }

        async function submitUnfollowUser() {
            try {
                await followers.deleteUserFollowsSpecificUser(loggedUserId, userMe.value.id);

                userFollowState.value = null;

                // Set the success message
                successMessage.value = t('user.successUserUnfollowed');
                successAlertStore.setAlertMessage(successMessage.value);
                successAlertStore.setClosableState(true);
            } catch (error) {
                // Set the error message
                errorMessage.value = t('user.errorUnableToUnfollow') + " - " + error.toString();
                errorAlertStore.setAlertMessage(errorMessage.value);
            }
        }

        return {
            idFromParam,
            isLoading,
            isActivitiesLoading,
            loggedUserId,
            userMe,
            userThisMonthNumberOfActivities,
            userFollowersCountAccepted,
            userFollowingCountAccepted,
            t,
            week,
            formatDateRange,
            setWeek,
            visibleWeeks,
            userWeekActivities,
            successMessage,
            errorMessage,
            userFollowState,
            userFollowersAll,
            userFollowingAll,
            updateFollowingList,
            updateFollowerList,
            updateFollowerListWithAccepted,
            submitFollowUser,
            submitCancelFollowUser,
            submitUnfollowUser,
        };
    },
};  
</script>