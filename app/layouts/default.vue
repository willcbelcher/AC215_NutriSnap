<template>
	<div class="min-h-screen bg-gray-50">
		<header class="bg-white shadow-md">
			<nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="flex justify-between h-16">
					<div class="flex">
						<div class="flex-shrink-0 flex items-center">
							<span class="text-2xl font-bold text-green-600">NutriSnap</span>
						</div>
						<div class="hidden sm:ml-6 sm:flex sm:space-x-8">
							<NuxtLink
								to="/"
								class="border-b-2 border-transparent text-gray-500 hover:border-green-500 hover:text-green-600 inline-flex items-center px-1 pt-1 text-sm font-medium"
							>
								Dashboard
							</NuxtLink>
							<NuxtLink
								to="/log"
								class="border-b-2 border-transparent text-gray-500 hover:border-green-500 hover:text-green-600 inline-flex items-center px-1 pt-1 text-sm font-medium"
							>
								Log Meal
							</NuxtLink>
						</div>
					</div>

					<div class="flex items-center">
						<div class="ml-3 relative">
							<button
								class="flex items-center p-1 rounded-full bg-white text-gray-500 hover:text-green-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
							>
								<span class="sr-only">Open user menu</span>
								<img
									class="h-8 w-8 rounded-full"
									src="https://via.placeholder.com/150/059669/FFFFFF?text=P"
									alt="Profile Avatar Placeholder"
								/>
								<span
									class="ml-2 hidden lg:block text-sm font-medium text-gray-700"
									>User Profile</span
								>

								<svg
									class="ml-1 h-5 w-5"
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 20 20"
									fill="currentColor"
								>
									<path
										fill-rule="evenodd"
										d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
										clip-rule="evenodd"
									/>
								</svg>
							</button>
						</div>
					</div>
				</div>
			</nav>
		</header>

		<main class="py-6">
			<div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
				<slot />
			</div>
		</main>
	</div>
</template>

<script setup>
// Nuxt 3 uses the setup script for component logic
</script>
