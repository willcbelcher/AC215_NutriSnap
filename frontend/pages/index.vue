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
			<div class="grid grid-cols-1 gap-5 sm:grid-cols-3">
				<div
					class="bg-white overflow-hidden shadow rounded-lg px-4 py-5 sm:p-6"
				>
					<p class="text-sm font-medium text-gray-500 truncate">
						Total Protein (Logged)
					</p>
					<p class="mt-1 text-3xl font-semibold text-gray-900">
						{{ totalProtein.toFixed(0) }}g
					</p>
				</div>
				<div
					class="bg-white overflow-hidden shadow rounded-lg px-4 py-5 sm:p-6"
				>
					<p class="text-sm font-medium text-gray-500 truncate">
						Symptom-Free Streak
					</p>
					<p class="mt-1 text-3xl font-semibold text-green-600">3 Days</p>
				</div>
				<div
					class="bg-white overflow-hidden shadow rounded-lg px-4 py-5 sm:p-6"
				>
					<p class="text-sm font-medium text-gray-500 truncate">
						Triggers Found
					</p>
					<p class="mt-1 text-3xl font-semibold text-red-600">
						{{ triggerCount }}
					</p>
				</div>
			</div>

			<div class="bg-white shadow rounded-lg overflow-hidden">
				<div class="px-4 py-5 sm:px-6 border-b border-gray-200">
					<h3 class="text-lg leading-6 font-medium text-gray-900">
						Recent Meals
					</h3>
					<p class="mt-1 text-sm text-gray-500">
						Your last 3 AI-analyzed food logs.
					</p>
				</div>

				<ul role="list" class="divide-y divide-gray-200">
					<li
						v-for="meal in recentMeals"
						:key="meal.id"
						class="p-4 hover:bg-gray-50 transition"
					>
						<div class="flex space-x-4">
							<div class="flex-shrink-0">
								<img
									class="h-20 w-20 rounded-lg object-cover bg-gray-100"
									:src="meal.image_url"
									alt="Meal image"
									@error="
										$event.target.src =
											'https://via.placeholder.com/150?text=No+Image'
									"
								/>
							</div>

							<div class="flex-1 min-w-0">
								<div class="flex justify-between">
									<p class="text-lg font-bold text-gray-900 truncate">
										{{ meal.identified_foods }}
									</p>
									<p class="text-sm text-gray-500">
										{{ new Date(meal.created_at).toLocaleDateString() }}
									</p>
								</div>

								<div
									class="mt-1 flex items-center text-sm text-gray-600 space-x-4"
								>
									<span>🍖 {{ meal.protein }}g Protein</span>
									<span>🍞 {{ meal.carbs }}g Carbs</span>
									<span>🥑 {{ meal.fat }}g Fat</span>
								</div>

								<div
									v-if="
										meal.triggers &&
										meal.triggers !== 'None' &&
										meal.triggers !== 'None detected'
									"
									class="mt-2"
								>
									<span
										class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
									>
										⚠️ Trigger: {{ meal.triggers }}
									</span>
								</div>
								<div v-else class="mt-2">
									<span
										class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
									>
										✅ Safe Meal
									</span>
								</div>
							</div>
						</div>
					</li>

					<li
						v-if="recentMeals.length === 0"
						class="p-8 text-center text-gray-500"
					>
						No meals logged yet.
						<NuxtLink to="/log" class="text-green-600 hover:underline"
							>Log your first meal!</NuxtLink
						>
					</li>
				</ul>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue';

// 1. Fetch data from backend
// Note: In Docker, the browser (client) can't access 'backend:8000', it must use localhost:8000
const {
	data: meals,
	pending,
	error,
	refresh,
} = await useFetch('http://localhost:8000/dashboard');

// 2. Computed Properties for logic
const recentMeals = computed(() => {
	if (!meals.value) return [];
	// Take the first 3 (backend already sorts by descending date)
	return meals.value.slice(0, 3);
});

const totalProtein = computed(() => {
	if (!meals.value) return 0;
	// Sum of protein in all fetched meals
	return meals.value.reduce((sum, meal) => sum + (meal.protein || 0), 0);
});

const triggerCount = computed(() => {
	if (!meals.value) return 0;
	// Count meals that have a non-empty trigger field
	return meals.value.filter(
		(m) => m.triggers && m.triggers !== 'None' && m.triggers !== 'None detected'
	).length;
});
</script>
