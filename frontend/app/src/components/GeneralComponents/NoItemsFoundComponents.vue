<template>
    <div class="centered-card">
        <div class="card text-center bg-body-tertiary rounded p-3 border-0 shadow-sm">
            <div class="card-body">
                <!--<h5 class="card-title">{{ $t("noItemsFoundComponent.title") }}</h5>-->
                <h1 class="card-text"><font-awesome-icon :icon="['fas', 'fa-circle-info']" /></h1>
                <p class="card-text">{{ $t("noItemsFoundComponent.subtitle") }}</p>
            </div>
        </div>
    </div>
</template>