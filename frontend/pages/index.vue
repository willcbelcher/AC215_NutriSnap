<template>
	<div class="space-y-6">
		<div class="flex justify-between items-center">
			<h1 class="text-3xl font-extrabold text-gray-900">Health Dashboard</h1>
			<button
				@click="refresh"
				class="text-sm text-green-600 hover:text-green-800 font-medium"
			>
				Refresh Data ⟳
			</button>
		</div>

		<div v-if="pending" class="p-8 text-center text-gray-500">
			Loading your health data...
		</div>

		<div v-else-if="error" class="p-4 bg-red-50 text-red-700 rounded-lg">
			<p class="font-bold">Error loading dashboard</p>
			<p class="text-sm">Ensure your backend (localhost:8000) is running.</p>
		</div>

		<div v-else class="space-y-6">
			<div class="grid grid-cols-1 gap-5 lg:grid-cols-2">
                <!-- CHART SECTION -->
				<div class="bg-white overflow-hidden shadow rounded-lg px-4 py-5 sm:p-6">
					<p class="text-sm font-medium text-gray-500 truncate mb-4">
						Symptom Severity Trend
					</p>
                    <ClientOnly>
                        <div v-if="chartSeries.length > 0 && chartSeries[0].data.length > 1">
                            <apexchart
                                width="100%"
                                height="300"
                                type="area"
                                :options="chartOptions"
                                :series="chartSeries"
                            ></apexchart>
                        </div>
                        <div v-else class="flex items-center justify-center h-64 text-gray-500 text-center p-4">
                            <p>We need more data to give you your symptom severity chart!</p>
                        </div>
                    </ClientOnly>
				</div>

                <!-- TRIGGERS SECTION -->
				<div class="bg-white overflow-hidden shadow rounded-lg px-4 py-5 sm:p-6">
					<p class="text-sm font-medium text-gray-500 truncate mb-4">
						Potential Triggers Analysis
					</p>
					<div class="mt-1">
                        <span v-if="!triggers || triggers.length === 0" class="text-gray-500 text-sm">Not enough data to identify triggers.</span>
                        <div v-else class="space-y-4">
                            <div v-for="trigger in triggers" :key="trigger" class="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-100">
                                <div class="flex items-center">
                                    <span class="text-2xl mr-3">⚠️</span>
                                    <span class="font-medium text-red-900">{{ trigger }}</span>
                                </div>
                                <span class="text-xs font-bold text-red-600 uppercase tracking-wide">High Probability</span>
                            </div>
                        </div>
                        <div class="mt-6 text-sm text-gray-500">
                            <p>Based on your recent logs, these ingredients correlate with your reported symptoms.</p>
                        </div>
					</div>
				</div>
			</div>

            <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <!-- RECENT MEALS -->
                <div class="bg-white shadow rounded-lg overflow-hidden">
                    <div class="px-4 py-5 sm:px-6 border-b border-gray-200 bg-gray-50">
                        <h3 class="text-lg leading-6 font-medium text-gray-900">
                            Recent Meals
                        </h3>
                    </div>
                    <ul role="list" class="divide-y divide-gray-200">
                        <li v-for="meal in recentMeals" :key="meal.id" class="p-4 hover:bg-gray-50 transition">
                            <div class="flex justify-between items-start">
                                <div>
                                    <p class="text-md font-bold text-gray-900">
                                        {{ meal.identified_foods }}
                                    </p>
                                    <p class="text-xs text-gray-500">
                                        {{ new Date(meal.created_at).toLocaleDateString() }}
                                        {{ new Date(meal.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}
                                    </p>
                                    <div class="mt-2 flex items-center text-xs text-gray-600 space-x-3">
                                        <!-- Macros removed -->
                                    </div>
                                </div>
                                <div v-if="meal.triggers && meal.triggers !== 'None' && meal.triggers !== 'None detected'">
                                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                        {{ meal.triggers }}
                                    </span>
                                </div>
                            </div>
                        </li>
                        <li v-if="recentMeals.length === 0" class="p-6 text-center text-gray-500 text-sm">
                            No meals logged recently.
                        </li>
                    </ul>
                </div>

                <!-- RECENT SYMPTOMS -->
                <div class="bg-white shadow rounded-lg overflow-hidden">
                    <div class="px-4 py-5 sm:px-6 border-b border-gray-200 bg-gray-50">
                        <h3 class="text-lg leading-6 font-medium text-gray-900">
                            Recent Symptoms
                        </h3>
                    </div>
                    <ul role="list" class="divide-y divide-gray-200">
                        <li v-for="symptom in recentSymptoms" :key="symptom.id" class="p-4 hover:bg-gray-50 transition">
                            <div class="flex justify-between items-start">
                                <div>
                                    <p class="text-md font-bold text-red-700">
                                        {{ symptom.symptom_name }}
                                    </p>
                                    <p class="text-xs text-gray-500">
                                        {{ new Date(symptom.created_at).toLocaleDateString() }}
                                        {{ new Date(symptom.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}
                                    </p>
                                    <p v-if="symptom.notes" class="mt-1 text-sm text-gray-600 italic">
                                        "{{ symptom.notes }}"
                                    </p>
                                </div>
                                <div class="flex items-center">
                                    <span class="text-sm font-bold mr-1">Severity:</span>
                                    <span :class="[
                                        'px-2 py-1 rounded text-xs font-bold text-white',
                                        symptom.severity >= 7 ? 'bg-red-600' : symptom.severity >= 4 ? 'bg-orange-500' : 'bg-yellow-500'
                                    ]">
                                        {{ symptom.severity }}/10
                                    </span>
                                </div>
                            </div>
                        </li>
                        <li v-if="recentSymptoms.length === 0" class="p-6 text-center text-gray-500 text-sm">
                            No symptoms logged recently.
                        </li>
                    </ul>
                </div>
            </div>
		</div>
	</div>
</template>

<script setup>
import VueApexCharts from 'vue3-apexcharts';

// 1. Fetch data from backend
const config = useRuntimeConfig();
const apiBase = import.meta.server ? config.apiBase : config.public.apiBase;

const { data: triggers } = await useFetch('/dashboard/triggers', {
    baseURL: apiBase,
    default: () => [],
    server: false
});

const { data: allMeals } = await useFetch('/dashboard', {
    baseURL: apiBase,
    default: () => [],
    server: false
});

const { data: allSymptoms } = await useFetch('/dashboard/symptoms', {
    baseURL: apiBase,
    default: () => [],
    server: false
});

// 2. Computed Properties for logic
const recentMeals = computed(() => {
	if (!allMeals.value) return [];
	return allMeals.value.slice(0, 5);
});

const recentSymptoms = computed(() => {
    if (!allSymptoms.value) return [];
    return allSymptoms.value.slice(0, 5);
});

// Chart Data
const chartOptions = {
    chart: {
        id: 'symptom-trend',
        toolbar: { show: false }
    },
    xaxis: {
        type: 'datetime'
    },
    stroke: {
        curve: 'smooth'
    },
    colors: ['#EF4444'],
    dataLabels: { enabled: false }
};

const chartSeries = computed(() => {
    if (!allSymptoms.value) return [];
    
    // Map symptoms to [timestamp, severity]
    // Sort by date ascending for the chart
    const sorted = [...allSymptoms.value].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    
    const data = sorted.map(s => [
        new Date(s.created_at).getTime(),
        s.severity
    ]);
    
    return [{
        name: 'Symptom Severity',
        data: data
    }];
});
</script>
