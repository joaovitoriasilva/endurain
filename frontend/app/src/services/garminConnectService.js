import {
	fetchGetRequest,
	fetchPostRequest,
	fetchDeleteRequest,
} from "@/utils/serviceUtils";

export const garminConnect = {
	linkGarminConnect(data) {
		return fetchPostRequest("garminconnect/link", data);
	},
	mfaGarminConnect(data) {
		return fetchPostRequest("garminconnect/mfa", data);
	},
	getGarminConnectActivitiesLastDays(days) {
		return fetchGetRequest(`garminconnect/activities/days/${days}`);
	},
	getGarminConnectGear() {
		return fetchGetRequest("garminconnect/gear");
	},
	unlinkGarminConnect() {
		return fetchDeleteRequest("garminconnect/unlink");
	},
};