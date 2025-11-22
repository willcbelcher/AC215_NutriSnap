<template>
	<div class="space-y-6">
		<h1 class="text-3xl font-extrabold text-gray-900">Health Dashboard</h1>

		<div class="grid grid-cols-1 gap-5 sm:grid-cols-3">
			<div class="bg-white overflow-hidden shadow rounded-lg px-4 py-5 sm:p-6">
				<p class="text-sm font-medium text-gray-500 truncate">
					Total Protein (Yesterday)
				</p>
				<p class="mt-1 text-3xl font-semibold text-gray-900">85 g</p>
			</div>
			<div class="bg-white overflow-hidden shadow rounded-lg px-4 py-5 sm:p-6">
				<p class="text-sm font-medium text-gray-500 truncate">
					Symptom-Free Days (Streak)
				</p>
				<p class="mt-1 text-3xl font-semibold text-green-600">4 days</p>
			</div>
			<div class="bg-white overflow-hidden shadow rounded-lg px-4 py-5 sm:p-6">
				<p class="text-sm font-medium text-gray-500 truncate">
					Trigger Foods Logged (Last 7 Days)
				</p>
				<p class="mt-1 text-3xl font-semibold text-red-600">12 items</p>
			</div>
		</div>

		<div class="bg-white shadow rounded-lg">
			<div class="px-4 py-5 sm:p-6">
				<h2 class="text-xl font-semibold text-gray-900 mb-4">
					Personalized Trigger Analysis
				</h2>
				<p class="text-gray-700 mb-4">
					Based on your recent logs and symptom entries, here are potential
					triggers to watch out for:
				</p>

				<div class="flex flex-wrap gap-2">
					<span
						class="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800"
					>
						Lactose
					</span>
					<span
						class="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-red-100 text-red-800"
					>
						Gluten (Wheat)
					</span>
					<span
						class="inline-flex items-center px-3 py-0.5 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800"
					>
						Fructose
					</span>
				</div>

				<h3 class="text-lg font-medium text-gray-900 mt-6 mb-3">
					Foods to Limit Today
				</h3>
				<ul class="list-disc list-inside space-y-2 text-gray-700">
					<li>
						Limit dairy intake, particularly whole milk or cream-based sauces.
					</li>
					<li>
						Opt for rice or corn-based side dishes instead of bread or pasta.
					</li>
					<li>
						Stay hydrated and track any symptoms after consuming fruit juices.
					</li>
				</ul>
			</div>
		</div>

		<div class="bg-white shadow rounded-lg p-6">
			<h2 class="text-xl font-semibold text-gray-900 mb-4">
				Symptom & Trigger Trends (Last 30 Days)
			</h2>
			<div
				class="h-64 flex items-center justify-center text-gray-400 border-2 border-dashed border-gray-300 rounded-lg"
			>
				[Placeholder for Chart component showing food/symptom correlation]
			</div>
		</div>
	</div>
</template>

<script setup>
// Page logic for fetching dashboard data
</script>
