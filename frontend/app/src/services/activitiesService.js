import { fetchGetRequest, fetchPostFileRequest, fetchDeleteRequest, fetchPutRequest, fetchPostRequest } from '@/utils/serviceUtils';

export const activities = {
    getUserWeekActivities(user_id, week_number) {
        return fetchGetRequest(`activities/user/${user_id}/week/${week_number}`);
    },
    getUserThisWeekStats(user_id) {
        return fetchGetRequest(`activities/user/${user_id}/thisweek/distances`);
    },
    getUserThisMonthStats(user_id) {
        return fetchGetRequest(`activities/user/${user_id}/thismonth/distances`);
    },
    getUserThisMonthActivitiesNumber(user_id) {
        return fetchGetRequest(`activities/user/${user_id}/thismonth/number`);
    },
    getUserActivitiesByGearId(gear_id) {
        return fetchGetRequest(`activities/user/gear/${gear_id}`);
    },
    getUserNumberOfActivities(user_id) {
        return fetchGetRequest(`activities/user/${user_id}/number`);
    },
    getUserActivitiesWithPagination(user_id, pageNumber, numRecords) {
        return fetchGetRequest(`activities/user/${user_id}/page_number/${pageNumber}/num_records/${numRecords}`);
    },
    getUserFollowersActivitiesWithPagination(user_id, pageNumber, numRecords) {
        return fetchGetRequest(`activities/user/${user_id}/followed/page_number/${pageNumber}/num_records/${numRecords}`);
    },
    getActivityById(activityId) {
        return fetchGetRequest(`activities/${activityId}`);
    },
    getActivityByName(name) {
        return fetchGetRequest(`activities/name/contains/${name}`);
    },
    uploadActivityFile(formData) {
        return fetchPostFileRequest('activities/create/upload', formData);
    },
    bulkImportActivities() {
        return fetchPostRequest('activities/create/bulkimport');
    },
    editActivity(data) {
        return fetchPutRequest('activities/edit', data);
    },
    deleteActivity(activityId) {
        return fetchDeleteRequest(`activities/${activityId}/delete`);
    }
};