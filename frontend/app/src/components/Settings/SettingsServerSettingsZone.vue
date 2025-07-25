<template>
    <div class="col">
        <form class="bg-body-tertiary rounded p-3 shadow-sm">
            <h4>{{ $t("settingsServerSettingsZoneComponent.defaultsTitle") }}</h4>
            <!-- Units -->
            <label>{{ $t("settingsServerSettingsZoneComponent.unitsLabel") }}</label>
            <select class="form-select" name="serverSettingsUnits" v-model="units" required>
                <option value="1">{{ $t("settingsServerSettingsZoneComponent.unitsMetric") }}</option>
                <option value="2">{{ $t("settingsServerSettingsZoneComponent.unitsImperial") }}</option>
            </select>
            <!-- Currency -->
            <label class="mt-1">{{ $t("settingsServerSettingsZoneComponent.currencyLabel") }}</label>
            <select class="form-select" name="serverSettingsCurrency" v-model="currency" required>
                <option value="1">{{ $t("generalItems.currencyEuro") }}</option>
                <option value="2">{{ $t("generalItems.currencyDollar") }}</option>
                <option value="3">{{ $t("generalItems.currencyPound") }}</option>
            </select>
            <!-- Num records per list -->
            <label class="mt-1">{{ $t("settingsServerSettingsZoneComponent.numRecordsLabel") }}</label>
            <select class="form-select" name="serverSettingsNumRecordsPerPage" v-model="numRecordsPerPage" required>
                <option value=5>5</option>
                <option value=10>10</option>
                <option value=25>25</option>
                <option value=50>50</option>
                <option value=100>100</option>
            </select>
            <hr>
            <!-- Public shareable links -->
            <h4 class="mt-4">{{ $t("settingsServerSettingsZoneComponent.publicShareableLinksLabel") }}</h4>
            <label class="form-label" for="serverSettingsPublicShareableLinksEnabledSelect">{{
                $t("settingsServerSettingsZoneComponent.publicShareableLinksEnabledLabel") }}</label>
            <select class="form-select" name="serverSettingsPublicShareableLinksEnabledSelect"
                v-model="publicShareableLinks" required>
                <option value="false">{{ $t("settingsServerSettingsZoneComponent.publicShareableLinksFalse") }}</option>
                <option value="true">{{ $t("settingsServerSettingsZoneComponent.publicShareableLinksTrue") }}</option>
            </select>
            <div class="alert alert-warning mt-2" role="alert">
                <font-awesome-icon :icon="['fas', 'triangle-exclamation']" />
                <span class="ms-2">{{
                    $t("settingsServerSettingsZoneComponent.serverSettingsPublicShareableLinksEnabledWarningAlert")
                }}</span>
            </div>
            <!-- Public shareable user info -->
            <label class="form-label" for="serverSettingsPublicShareableLinksShowUserInfo">{{
                $t("settingsServerSettingsZoneComponent.publicShareableLinksShowUserInfoLabel") }}</label>
            <select class="form-select" name="serverSettingsPublicShareableLinksShowUserInfo"
                v-model="publicShareableLinksUserInfo" required>
                <option value="false">{{ $t("settingsServerSettingsZoneComponent.publicShareableLinksFalse") }}</option>
                <option value="true">{{ $t("settingsServerSettingsZoneComponent.publicShareableLinksTrue") }}</option>
            </select>
            <div class="alert alert-warning mt-2" role="alert">
                <font-awesome-icon :icon="['fas', 'triangle-exclamation']" />
                <span class="ms-2">{{
                    $t("settingsServerSettingsZoneComponent.serverSettingsPublicShareableLinksShowUserWarningAlert")
                }}</span>
            </div>
            <hr>
            <!-- Login photo set -->
            <h4 class="mt-4">{{ $t("settingsServerSettingsZoneComponent.photosLabel") }}</h4>
            <div class="row">
                <div class="col">
                    <label class="form-label" for="serverSettingsLoginPhotoLabel">{{
                        $t("settingsServerSettingsZoneComponent.loginPhotoLabel") }}</label>
                    <!-- add login photo button -->
                    <a class="w-100 btn btn-primary shadow-sm" href="#" role="button" data-bs-toggle="modal"
                        data-bs-target="#addLoginPhotoModal" v-if="!loginPhotoSet">
                        {{ $t("settingsServerSettingsZoneComponent.buttonAddPhoto") }}
                    </a>

                    <!-- Delete login photo section -->
                    <a class="w-100 btn btn-danger" href="#" role="button" data-bs-toggle="modal"
                        data-bs-target="#deleteLoginPhotoModal" v-else>{{
                            $t("settingsServerSettingsZoneComponent.buttonDeleteLoginPhoto") }}</a>

                    <!-- Modal add login photo -->
                    <ModalComponentUploadFile modalId="addLoginPhotoModal"
                        :title="$t('settingsServerSettingsZoneComponent.loginPhotoLabel')"
                        :fileFieldLabel="$t('settingsServerSettingsZoneComponent.logonPhotoAddLabel')"
                        filesAccepted=".png" actionButtonType="success"
                        :actionButtonText="$t('settingsServerSettingsZoneComponent.loginPhotoLabel')"
                        @fileToEmitAction="submitUploadFileForm" />

                    <!-- Modal delete login photo -->
                    <ModalComponent modalId="deleteLoginPhotoModal"
                        :title="t('settingsServerSettingsZoneComponent.buttonDeleteLoginPhoto')"
                        :body="`${t('settingsServerSettingsZoneComponent.modalDeleteLoginPhotoBody')}`"
                        actionButtonType="danger"
                        :actionButtonText="t('settingsServerSettingsZoneComponent.buttonDeleteLoginPhoto')"
                        @submitAction="submitDeleteLoginPhoto" />
                </div>
            </div>
        </form>
    </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useServerSettingsStore } from "@/stores/serverSettingsStore";
import { serverSettings } from "@/services/serverSettingsService";
import { push } from "notivue";
import ModalComponent from "@/components/Modals/ModalComponent.vue";
import ModalComponentUploadFile from "@/components/Modals/ModalComponentUploadFile.vue"

const { t } = useI18n();
const serverSettingsStore = useServerSettingsStore();
const units = ref(serverSettingsStore.serverSettings.units);
const currency = ref(serverSettingsStore.serverSettings.currency);
const numRecordsPerPage = ref(serverSettingsStore.serverSettings.num_records_per_page);
const publicShareableLinks = ref(serverSettingsStore.serverSettings.public_shareable_links);
const publicShareableLinksUserInfo = ref(serverSettingsStore.serverSettings.public_shareable_links_user_info);
const loginPhotoSet = ref(serverSettingsStore.serverSettings.login_photo_set);

async function updateServerSettings() {
    const data = {
        id: 1,
        units: units.value,
        currency: currency.value,
        num_records_per_page: numRecordsPerPage.value,
        public_shareable_links: publicShareableLinks.value,
        public_shareable_links_user_info: publicShareableLinksUserInfo.value,
        login_photo_set: loginPhotoSet.value,
    };
    try {
        // Update the server settings in the DB
        await serverSettings.editServerSettings(data);

        // Update the server settings in the store
        serverSettingsStore.setServerSettings(data);

        push.success(t("settingsServerSettingsZoneComponent.successUpdateServerSettings"));
    } catch (error) {
        push.error(t("settingsServerSettingsZoneComponent.errorUpdateServerSettings"));
    }
}

const submitUploadFileForm = async (file) => {
    // Set the loading message
    const notification = push.promise(t("settingsServerSettingsZoneComponent.processingPhotoUpload"));

    // If there is a file, create the form data and upload the file
    if (file) {
        try {
            // Upload the file
            await serverSettings.uploadLoginPhotoFile(file);
            // Set the login photo set to true
            loginPhotoSet.value = true;

            // Update the server settings in the store and DB
            await updateServerSettings();

            // Set the success message
            notification.resolve(t("settingsServerSettingsZoneComponent.successPhotoUpload"));
        } catch (error) {
            // Set the error message
            notification.reject(`${error}`);
        }
    }
};

const submitDeleteLoginPhoto = async () => {
    // Set the loading message
    const notification = push.promise(t("settingsServerSettingsZoneComponent.processingPhotoDelete"));

    try {
        // Delete the login photo
        await serverSettings.deleteLoginPhotoFile();
        // Set the login photo set to false
        loginPhotoSet.value = false;

        // Update the server settings in the store and DB
        await updateServerSettings();

        // Set the success message
        notification.resolve(t("settingsServerSettingsZoneComponent.successPhotoDelete"));
    } catch (error) {
        // Set the error message
        notification.reject(`${error}`);
    }
};

watch([units, currency, numRecordsPerPage, publicShareableLinks, publicShareableLinksUserInfo], async () => {
    await updateServerSettings();
}, { immediate: false });
</script>