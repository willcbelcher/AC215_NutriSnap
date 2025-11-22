<template>
	<div class="space-y-6">
		<h1 class="text-3xl font-extrabold text-gray-900">Log Your Meal</h1>
		<p class="text-gray-600">
			Simply upload a photo, and our AI will identify the foods and extract the
			nutritional data.
		</p>

		<div class="bg-white shadow rounded-lg p-6">
			<h2 class="text-xl font-semibold text-gray-900 mb-4">
				Photo Upload (AI Ingestion)
			</h2>

			<div
				class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md"
			>
				<div class="space-y-1 text-center">
					<svg
						class="mx-auto h-12 w-12 text-gray-400"
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M4 16l4.586-4.586a2 2 0 012.828 0L15 14m-2-4h3m-3 0V7m3 3h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
						/>
					</svg>
					<div class="flex text-sm text-gray-600">
						<label
							for="file-upload"
							class="relative cursor-pointer bg-white rounded-md font-medium text-green-600 hover:text-green-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-green-500"
						>
							<span>Upload a file or take a picture</span>
							<input
								id="file-upload"
								name="file-upload"
								type="file"
								class="sr-only"
								@change="handleFileUpload"
								accept="image/*"
							/>
						</label>
						<p class="pl-1">or drag and drop</p>
					</div>
					<p class="text-xs text-gray-500">PNG, JPG up to 10MB</p>
				</div>
			</div>

			<div class="mt-6">
				<button
					@click="logMeal"
					:disabled="!file"
					class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
				>
					Log Meal with AI
				</button>
			</div>

			<div
				v-if="mealLogged"
				class="mt-8 p-4 bg-lime-50 border-l-4 border-lime-400 text-green-800"
			>
				<p class="font-bold">Meal Logged! NutriSnap AI Analysis:</p>
				<ul class="list-disc list-inside">
					<li>**Identified:** Chicken, Broccoli, Brown Rice</li>
					<li>**Macros:** Protein: 40g, Carbs: 55g, Fat: 15g</li>
					<li>**Triggers:** Low risk (no lactose detected).</li>
				</ul>
			</div>
		</div>

		<div class="bg-white shadow rounded-lg p-6">
			<h2 class="text-xl font-semibold text-gray-900 mb-4">Log Symptoms</h2>
			<textarea
				placeholder="How do you feel? (e.g., Bloating, fatigue, high energy)"
				rows="3"
				class="shadow-sm focus:ring-green-500 focus:border-green-500 block w-full sm:text-sm border-gray-300 rounded-md"
			></textarea>
			<div class="mt-4">
				<button
					class="py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
				>
					Save Symptoms
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref } from 'vue';

const file = ref(null);
const mealLogged = ref(false);

const handleFileUpload = (event) => {
	file.value = event.target.files[0];
	mealLogged.value = false;
	console.log('File selected:', file.value.name);
};

const logMeal = () => {
	if (!file.value) return;

	// Simulate API call to the CV Food Identification Model (Cloud Run)
	setTimeout(() => {
		mealLogged.value = true;
		file.value = null; // Clear file after simulated upload
	}, 2000);
};
</script>
