<template>
  <div class="max-w-3xl mx-auto space-y-8">
    <div class="md:flex md:items-center md:justify-between">
      <div class="min-w-0 flex-1">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
          Log Activity
        </h2>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex sm:space-x-8" aria-label="Tabs">
        <button
          @click="activeTab = 'food'"
          :class="[
            activeTab === 'food'
              ? 'border-green-500 text-green-600'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
            'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium w-1/2 sm:w-auto text-center',
          ]"
        >
          Log Food
        </button>
        <button
          @click="activeTab = 'symptom'"
          :class="[
            activeTab === 'symptom'
              ? 'border-red-500 text-red-600'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
            'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium w-1/2 sm:w-auto text-center',
          ]"
        >
          Log Symptom
        </button>
      </nav>
    </div>

    <!-- Food Logging Section -->
    <div v-if="activeTab === 'food'" class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-base font-semibold leading-6 text-gray-900">Upload Meal Photo</h3>
        <div class="mt-2 max-w-xl text-sm text-gray-500">
          <p>Upload a photo of your meal. Our AI will analyze it for potential triggers.</p>
        </div>
        
        <div class="mt-5">
            <div class="flex items-center justify-center w-full">
                <label for="dropzone-file" class="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                    <div class="flex flex-col items-center justify-center pt-5 pb-6">
                        <svg class="w-8 h-8 mb-4 text-gray-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                        </svg>
                        <p class="mb-2 text-sm text-gray-500"><span class="font-semibold">Click to upload</span> or drag and drop</p>
                        <p class="text-xs text-gray-500">SVG, PNG, JPG or GIF (MAX. 800x400px)</p>
                    </div>
                    <input id="dropzone-file" type="file" class="hidden" @change="handleFileUpload" accept="image/*" />
                </label>
            </div>
        </div>

        <div v-if="uploading" class="mt-4 text-center text-blue-600">
            Analyzing image...
        </div>

        <div v-if="loggedMeal" class="mt-6 border-t border-gray-100 pt-4">
            <h4 class="text-lg font-bold text-gray-900">Analysis Result</h4>
            <div class="mt-2 bg-green-50 p-4 rounded-md">
                <p class="font-medium text-green-800">Detected: {{ loggedMeal.identified_foods }}</p>
                <div v-if="loggedMeal.triggers && loggedMeal.triggers !== 'None'" class="mt-2 text-red-600 text-sm font-bold">
                    ⚠️ Potential Triggers: {{ loggedMeal.triggers }}
                </div>
            </div>
            <div class="mt-4">
                <button @click="resetFood" class="text-sm text-gray-600 underline">Log another meal</button>
            </div>
        </div>
      </div>
    </div>

    <!-- Symptom Logging Section -->
    <div v-if="activeTab === 'symptom'" class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-base font-semibold leading-6 text-gray-900">Log a Symptom</h3>
        <form @submit.prevent="submitSymptom" class="mt-5 space-y-4">
            
            <div>
                <label for="symptom" class="block text-sm font-medium leading-6 text-gray-900">Symptom</label>
                <select id="symptom" v-model="symptomForm.symptom_name" class="mt-2 block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-green-600 sm:text-sm sm:leading-6">
                    <option>Bloating</option>
                    <option>Headache</option>
                    <option>Nausea</option>
                    <option>Fatigue</option>
                    <option>Stomach Pain</option>
                    <option>Diarrhea</option>
                    <option>Skin Rash</option>
                    <option>Other</option>
                </select>
            </div>

            <div>
                <label for="severity" class="block text-sm font-medium leading-6 text-gray-900">Severity (1-10)</label>
                <input type="range" id="severity" v-model.number="symptomForm.severity" min="1" max="10" class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer mt-2">
                <div class="text-center text-sm font-bold text-gray-700">{{ symptomForm.severity }}</div>
            </div>

            <div>
                <label for="notes" class="block text-sm font-medium leading-6 text-gray-900">Notes</label>
                <textarea id="notes" v-model="symptomForm.notes" rows="3" class="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-green-600 sm:text-sm sm:leading-6"></textarea>
            </div>

            <div class="pt-4">
                <button type="submit" class="rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-600">
                    Log Symptom
                </button>
            </div>
        </form>

        <div v-if="symptomSuccess" class="mt-4 p-4 bg-green-50 text-green-700 rounded-lg">
            Symptom logged successfully!
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const config = useRuntimeConfig();
const apiBase = import.meta.server ? config.apiBase : config.public.apiBase;

const activeTab = ref('food');

// Food Logic
const uploading = ref(false);
const loggedMeal = ref(null);

async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    uploading.value = true;
    loggedMeal.value = null;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await $fetch(`${apiBase}/log/food`, {
            method: 'POST',
            body: formData
        });
        loggedMeal.value = response;
    } catch (e) {
        console.error("Upload failed", e);
        alert("Failed to upload image");
    } finally {
        uploading.value = false;
    }
}

function resetFood() {
    loggedMeal.value = null;
}

// Symptom Logic
const symptomForm = ref({
    symptom_name: 'Bloating',
    severity: 5,
    notes: ''
});
const symptomSuccess = ref(false);

async function submitSymptom() {
    symptomSuccess.value = false;
    try {
        await $fetch(`${apiBase}/log/symptom`, {
            method: 'POST',
            body: {
                user_id: 1, // Hardcoded for prototype
                ...symptomForm.value
            }
        });
        symptomSuccess.value = true;
        // Reset form slightly
        symptomForm.value.notes = '';
        setTimeout(() => symptomSuccess.value = false, 3000);
    } catch (e) {
        console.error("Symptom log failed", e);
        alert("Failed to log symptom");
    }
}
</script>
