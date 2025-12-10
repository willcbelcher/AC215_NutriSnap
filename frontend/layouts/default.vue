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
                                active-class="border-green-500 text-gray-900"
							>
								Dashboard
							</NuxtLink>
							<NuxtLink
								to="/log"
								class="border-b-2 border-transparent text-gray-500 hover:border-green-500 hover:text-green-600 inline-flex items-center px-1 pt-1 text-sm font-medium"
                                active-class="border-green-500 text-gray-900"
							>
								Log Activity
							</NuxtLink>
						</div>
					</div>

					<div class="hidden sm:ml-6 sm:flex sm:items-center">
						<div class="ml-3 relative flex items-center space-x-3">
                            <div class="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center text-green-800 font-bold">
                                U
                            </div>
                            <span class="text-sm font-medium text-gray-700">User Profile</span>
						</div>
					</div>

                    <!-- Mobile menu button -->
                    <div class="-mr-2 flex items-center sm:hidden">
                        <button @click="mobileMenuOpen = !mobileMenuOpen" type="button" class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-green-500" aria-controls="mobile-menu" aria-expanded="false">
                            <span class="sr-only">Open main menu</span>
                            <!-- Icon when menu is closed. -->
                            <svg v-if="!mobileMenuOpen" class="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                            <!-- Icon when menu is open. -->
                            <svg v-else class="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
				</div>
			</nav>

            <!-- Mobile menu, show/hide based on menu state. -->
            <div v-show="mobileMenuOpen" class="sm:hidden" id="mobile-menu">
                <div class="pt-2 pb-3 space-y-1">
                    <NuxtLink
                        to="/"
                        class="border-l-4 border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700 block pl-3 pr-4 py-2 text-base font-medium"
                        active-class="bg-green-50 border-green-500 text-green-700"
                        @click="mobileMenuOpen = false"
                    >
                        Dashboard
                    </NuxtLink>
                    <NuxtLink
                        to="/log"
                        class="border-l-4 border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700 block pl-3 pr-4 py-2 text-base font-medium"
                        active-class="bg-green-50 border-green-500 text-green-700"
                        @click="mobileMenuOpen = false"
                    >
                        Log Activity
                    </NuxtLink>
                </div>
                <div class="pt-4 pb-4 border-t border-gray-200">
                    <div class="flex items-center px-4">
                        <div class="flex-shrink-0">
                            <div class="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center text-green-800 font-bold">
                                U
                            </div>
                        </div>
                        <div class="ml-3">
                            <div class="text-base font-medium text-gray-800">Demo User</div>
                            <div class="text-sm font-medium text-gray-500">demo@test.com</div>
                        </div>
                    </div>
                </div>
            </div>
		</header>

		<main class="py-6">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<slot />
			</div>
		</main>
	</div>
</template>

<script setup>
import { ref } from 'vue';

const mobileMenuOpen = ref(false);
</script>
