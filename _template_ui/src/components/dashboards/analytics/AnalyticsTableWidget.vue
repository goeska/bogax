<script setup>
import { ProductService } from '@/service/ProductService';
import { onMounted, ref } from 'vue';

const products = ref(null);

function formatCurrency(value) {
    return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}

onMounted(() => {
    ProductService.getProducts().then((data) => (products.value = data));
});
</script>

<template>
    <div class="card">
        <DataTable :value="products" :rows="4" style="margin-bottom: 20px" :paginator="true">
            <Column header="Logo" headerStyle="width:20%; min-width:10rem;">
                <template #body="slotProps">
                    <img :src="'/demo/images/product/' + slotProps.data.image" class="shadow-lg" :alt="slotProps.data.image" width="50" />
                </template>
            </Column>
            <Column field="name" header="Name" :sortable="true" headerStyle="width:20%; min-width:10rem;">
                <template #body="slotProps">
                    {{ slotProps.data.name }}
                </template>
            </Column>
            <Column field="category" header="Category" :sortable="true" headerStyle="width:20%; min-width:10rem;">
                <template #body="slotProps">
                    {{ slotProps.data.category }}
                </template>
            </Column>
            <Column field="price" header="Price" :sortable="true" headerStyle="width:20%; min-width:10rem;">
                <template #body="slotProps">
                    {{ formatCurrency(slotProps.data.price) }}
                </template>
            </Column>
            <Column header="View" headerStyle="width:20%; min-width:10rem;">
                <template #body>
                    <Button icon="pi pi-search" class="mb-1" rounded text></Button>
                </template>
            </Column>
        </DataTable>
    </div>
</template>
