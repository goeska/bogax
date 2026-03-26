<template>
    <div class="h-full bg-primary text-primary-contrast flex justify-between items-center pl-8 py-4 rounded-md overflow-hidden">
        <div class="flex flex-col justify-center">
            <div><span class="font-bold text-white text-sm">Carry your team on top</span></div>
            <div>
                <span class="font-bold text-white mt-1 text-4xl m-0">Upgrade Now</span>
            </div>
            <div>
                <Button icon="pi pi-database" label="See All Plans" class="bg-white! mt-4" outlined></Button>
            </div>
        </div>
        <div><img class="-mr-4" :draggable="false" src="/demo/images/dashboard/saas-card.png" alt="" /></div>
    </div>
</template>
