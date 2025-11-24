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
								Log Activity
							</NuxtLink>
						</div>
					</div>

					<div class="flex items-center">
						<div class="ml-3 relative flex items-center space-x-3">
                            <div class="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center text-green-800 font-bold">
                                U
                            </div>
                            <span class="hidden lg:block text-sm font-medium text-gray-700">User Profile</span>
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
