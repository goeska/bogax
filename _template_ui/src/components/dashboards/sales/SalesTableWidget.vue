<script setup>
import { ProductService } from '@/service/ProductService';
import { onMounted, ref } from 'vue';

const products = ref(null);

onMounted(() => {
    ProductService.getProducts().then((data) => (products.value = data));
});

function formatCurrency(value) {
    return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}
</script>

<template>
    <div class="card h-full">
        <DataTable :value="products" :paginator="true" :rows="8" scrollable :tableStyle="{ minWidth: '40rem' }">
            <Column header="Logo" class="w-20" bodyStyle="height:5rem;">
                <template #body="slotProps">
                    <img :src="'/demo/images/product/' + slotProps.data.image" class="shadow-lg w-12" :alt="slotProps.data.image" />
                </template>
            </Column>
            <Column field="name" header="Name" :sortable="true" headerStyle=" min-width:14rem;">
                <template #body="slotProps">
                    {{ slotProps.data.name }}
                </template>
            </Column>
            <Column field="category" header="Category" :sortable="true" headerStyle="min-width:8rem;">
                <template #body="slotProps">
                    {{ slotProps.data.category }}
                </template>
            </Column>
            <Column field="price" header="Price" :sortable="true" headerStyle="min-width:8rem;">
                <template #body="slotProps">
                    {{ formatCurrency(slotProps.data.price) }}
                </template>
            </Column>
            <Column header="View" class="w-20">
                <template #body>
                    <Button icon="pi pi-search" class="mb-1" rounded text></Button>
                </template>
            </Column>
        </DataTable>
    </div>
</template>
