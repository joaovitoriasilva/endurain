<template>
    <!-- Modal edit activity -->
    <div class="modal fade" id="editActivityModal" tabindex="-1" aria-labelledby="editActivityModal" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h1 class="modal-title fs-5" id="editActivityModal">{{ $t("editActivityModal.modalEditActivityTitle") }}</h1>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <form  @submit.prevent="submitEditActivityForm">
                    <div class="modal-body">
                        <!-- name fields -->
                        <label for="activityNameEdit"><b>* {{ $t("editActivityModal.modalEditActivityNameLabel") }}</b></label>
                        <input class="form-control" type="text" name="activityNameEdit" :placeholder='$t("editActivityModal.modalEditActivityNamePlaceholder")' maxlength="45" v-model="editActivityName" required>
                        <!-- description fields -->
                        <label for="activityDescriptionEdit"><b>{{ $t("editActivityModal.modalEditActivityDescriptionLabel") }}</b></label>
                        <input class="form-control" type="text" name="activityDescriptionEdit" :placeholder='$t("editActivityModal.modalEditActivityDescriptionPlaceholder")' maxlength="2500" v-model="editActivityDescription">
                        <!-- visibility fields -->
                        <label for="activityVisibilityEdit"><b>* {{ $t("editActivityModal.modalEditActivityVisibilityPlaceholder") }}</b></label>
                        <select class="form-control" name="activityVisibilityEdit" v-model="editActivityVisibility" required>
                            <option value="0">{{ $t("editActivityModal.modalEditActivityVisibilityOption0") }}</option>
                            <option value="1">{{ $t("editActivityModal.modalEditActivityVisibilityOption1") }}</option>
                            <option value="2">{{ $t("editActivityModal.modalEditActivityVisibilityOption2") }}</option>
                        </select>
                        <p>* {{ $t("generalItens.requiredField") }}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{{ $t("generalItens.buttonClose") }}</button>
                        <button type="submit" class="btn btn-success" data-bs-dismiss="modal">{{ $t("editActivityModal.modalEditActivityTitle") }}</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

export default {
    components: {
        
    },
    props: {
        activity: {
            type: Object,
            required: true,
        },
    },
    setup(props) {
        const editActivityDescription = ref(props.activity.description);
        const editActivityName = ref(props.activity.name);
        const editActivityVisibility = ref(props.activity.visibility);

        return {
            editActivityDescription,
            editActivityName,
            editActivityVisibility,
        };
    },
};
</script>