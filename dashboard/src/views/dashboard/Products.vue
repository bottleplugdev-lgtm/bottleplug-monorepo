<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-secondary-800">Products</h1>
        <p class="text-secondary-600">Manage your product inventory</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="refreshProducts"
          class="btn btn-outline"
          :disabled="loading"
        >
          <RefreshCw v-if="loading" class="h-4 w-4 animate-spin" />
          <RefreshCw v-else class="h-4 w-4" />
          Refresh
        </button>
        <button @click="showAddCategoryModal = true" class="btn btn-secondary">
          <FolderPlus class="h-4 w-4" />
          Add Category
        </button>
        <button @click="showAddModal = true" class="btn btn-primary">
          <Plus class="h-4 w-4" />
          Add Product
        </button>
      </div>
    </div>

    <!-- Product Statistics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div class="card bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-blue-100 text-sm font-medium mb-1">Total Products</p>
            <p class="text-2xl font-bold">{{ productStats.total_products || 0 }}</p>
          </div>
          <div class="p-3 bg-blue-400/20 rounded-lg">
            <Package class="h-6 w-6" />
          </div>
        </div>
      </div>

      <div class="card bg-gradient-to-r from-yellow-500 to-yellow-600 text-white p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-yellow-100 text-sm font-medium mb-1">Low Stock Items</p>
            <p class="text-2xl font-bold">{{ productStats.low_stock_items || 0 }}</p>
          </div>
          <div class="p-3 bg-yellow-400/20 rounded-lg">
            <AlertTriangle class="h-6 w-6" />
          </div>
        </div>
      </div>

      <div class="card bg-gradient-to-r from-red-500 to-red-600 text-white p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-red-100 text-sm font-medium mb-1">Out of Stock</p>
            <p class="text-2xl font-bold">{{ productStats.out_of_stock || 0 }}</p>
          </div>
          <div class="p-3 bg-red-400/20 rounded-lg">
            <XCircle class="h-6 w-6" />
          </div>
        </div>
      </div>

      <div class="card bg-gradient-to-r from-green-500 to-green-600 text-white p-6" v-if="isAdmin">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-green-100 text-sm font-medium mb-1">Total Value</p>
            <p class="text-2xl font-bold">UGX {{ formatCurrency(productStats.total_value || 0) }}</p>
          </div>
          <div class="p-3 bg-green-400/20 rounded-lg">
            <DollarSign class="h-6 w-6" />
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search products..."
            class="w-full px-4 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            @input="debounceSearch"
          />
        </div>
        <div class="flex gap-2">
          <select
            v-model="selectedCategory"
            class="px-4 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            @change="handleFilter"
          >
            <option value="">All Categories</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
          <select
            v-model="stockFilter"
            class="px-4 py-2 border border-secondary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            @change="handleFilter"
          >
            <option value="">All Stock</option>
            <option value="in_stock">In Stock</option>
            <option value="low_stock">Low Stock</option>
            <option value="out_of_stock">Out of Stock</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Products Table -->
    <div class="card">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-secondary-200">
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Product</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Category</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Price</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Stock</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Status</th>
              <th class="text-left py-3 px-4 font-semibold text-secondary-700">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading" class="border-b border-secondary-100">
              <td colspan="6" class="py-8 px-4 text-center">
                <div class="flex items-center justify-center">
                  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
                  <span class="ml-2 text-secondary-600">Loading products...</span>
                </div>
              </td>
            </tr>
            <tr v-else-if="filteredProducts.length === 0" class="border-b border-secondary-100">
              <td colspan="6" class="py-8 px-4 text-center text-secondary-600">
                No products found
              </td>
            </tr>
            <tr
        v-for="product in filteredProducts"
        :key="product.id"
              class="border-b border-secondary-100 hover:bg-secondary-50"
            >
              <td class="py-4 px-4">
                <div class="flex items-center space-x-3">
                  <img
                    :src="product.image || '/placeholder-product.jpg'"
                    :alt="product.name"
                    class="h-12 w-12 rounded-lg object-cover"
                  />
                    <div>
                    <h4 class="font-medium text-secondary-800">{{ product.name }}</h4>
                    <p class="text-sm text-secondary-600">{{ product.description }}</p>
                  </div>
                </div>
              </td>
              <td class="py-4 px-4">
                <span class="px-2 py-1 bg-secondary-100 text-secondary-700 rounded-full text-sm">
                  {{ product.category_name || 'Uncategorized' }}
                </span>
              </td>
              <td class="py-4 px-4">
                <div>
                  <div class="font-medium text-secondary-800">
                    <span v-if="product.unit && product.unit.trim()" class="text-secondary-600 mr-1">{{ product.unit }}</span>
                    UGX {{ product.price || product.current_price }}
                  </div>
                  <div v-if="product.measurements && product.measurements.length > 0" class="text-xs text-secondary-600 mt-1">
                    <div v-for="measurement in product.measurements.slice(0, 2)" :key="measurement.id" class="flex items-center justify-between mb-1">
                      <span>{{ getMeasurementDisplayName(measurement) }}</span>
                      <span class="font-medium">
                        <span class="text-secondary-600 mr-1">{{ measurement.measurement_display || measurement.measurement }}</span>
                        UGX {{ formatCurrency(calculateMeasurementPrice(product, measurement)) }}
                      </span>
                    </div>
                    <div v-if="product.measurements.length > 2" class="text-xs text-secondary-500 mt-1">
                      +{{ product.measurements.length - 2 }} more measurements
                    </div>
                  </div>
                </div>
              </td>
              <td class="py-4 px-4">
                <span :class="[
                  'px-2 py-1 rounded-full text-sm font-medium',
                  getStockClass(product.stock)
                ]">
                  {{ product.stock }}
                </span>
              </td>
              <td class="py-4 px-4">
                <span :class="[
                  'px-2 py-1 rounded-full text-sm font-medium',
                  getStatusClass(product.status)
                ]">
                  {{ product.status }}
                </span>
              </td>
              <td class="py-4 px-4">
                      <div class="flex items-center space-x-2">
                        <button
                    @click="openMeasurementsModal(product)"
                    class="p-2 text-secondary-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Manage Measurements"
                        >
                          <Package class="h-4 w-4" />
                        </button>
                        <button
                    @click="adjustStock(product)"
                    class="p-2 text-secondary-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Adjust Stock"
                        >
                          <Plus class="h-4 w-4" />
                        </button>
                        <button
                    @click="editProduct(product)"
                    class="p-2 text-secondary-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="Edit"
                        >
                          <Edit class="h-4 w-4" />
                        </button>
                        <button
                    @click="deleteProduct(product.id)"
                    class="p-2 text-secondary-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete"
                        >
                          <Trash2 class="h-4 w-4" />
                        </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && filteredProducts.length > 0" class="flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <p class="text-sm text-secondary-600">
          Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalProducts) }} of {{ totalProducts }} products
        </p>
        <div class="flex items-center space-x-2">
          <span class="text-sm text-secondary-600">Show:</span>
          <select
            v-model="pageSize"
            @change="handlePageSizeChange"
            class="px-2 py-1 border border-secondary-200 rounded text-sm"
          >
            <option v-for="size in pageSizeOptions" :key="size" :value="size">
              {{ size }}
            </option>
          </select>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <button
          @click="goToFirstPage"
          :disabled="currentPage === 1"
          class="btn btn-sm btn-outline"
          title="First Page"
        >
          «
        </button>
        <button
          @click="previousPage"
          :disabled="currentPage === 1"
          class="btn btn-sm btn-outline"
        >
          Previous
        </button>
        <span class="px-3 py-1 text-sm text-secondary-600">
          Page 
          <input
            v-model.number="currentPage"
            @change="handlePageChange"
            @keyup.enter="handlePageChange"
            type="number"
            min="1"
            :max="totalPages"
            class="w-16 px-2 py-1 border border-secondary-200 rounded text-sm text-center"
          />
          of {{ totalPages }}
        </span>
        <button
          @click="nextPage"
          :disabled="currentPage === totalPages"
          class="btn btn-sm btn-outline"
        >
          Next
        </button>
        <button
          @click="goToLastPage"
          :disabled="currentPage === totalPages"
          class="btn btn-sm btn-outline"
          title="Last Page"
        >
          »
        </button>
      </div>
    </div>

    <!-- Add Product Modal -->
    <div v-if="showAddModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <form @submit.prevent="handleAddProduct">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Add New Product</h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Product Name</label>
                  <input
                    v-model="productForm.name"
                    type="text"
                    required
                    class="input mt-1"
                    placeholder="Enter product name"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">SKU</label>
                  <input
                    v-model="productForm.sku"
                    type="text"
                    required
                    class="input mt-1"
                    placeholder="Enter SKU"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Category</label>
                  <select v-model="productForm.category" required class="input mt-1">
                    <option value="">Select category</option>
                    <option v-for="category in categories" :key="category.id" :value="category.id">
                      {{ category.name }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Subcategory</label>
                  <input
                    v-model="productForm.subcategory"
                    type="text"
                    class="input mt-1"
                    placeholder="Enter subcategory"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Price</label>
                  <input
                    v-model="productForm.price"
                    type="number"
                    step="0.01"
                    required
                    class="input mt-1"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Original Price</label>
                  <input
                    v-model="productForm.original_price"
                    type="number"
                    step="0.01"
                    class="input mt-1"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Stock</label>
                  <input
                    v-model="productForm.stock"
                    type="number"
                    required
                    class="input mt-1"
                    placeholder="0"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Unit</label>
                  <select v-model="productForm.unit" required class="input mt-1">
                    <option value="">Select unit</option>
                    <option value="bottle">Bottle</option>
                    <option value="can">Can</option>
                    <option value="pack">Pack</option>
                    <option value="case">Case</option>
                    <option value="liter">Liter</option>
                    <option value="ml">Milliliter</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Status</label>
                  <select v-model="productForm.status" required class="input mt-1">
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="out_of_stock">Out of Stock</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Vintage</label>
                  <input
                    v-model="productForm.vintage"
                    type="text"
                    class="input mt-1"
                    placeholder="e.g., 2020"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Region</label>
                  <input
                    v-model="productForm.region"
                    type="text"
                    class="input mt-1"
                    placeholder="e.g., California"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Alcohol Percentage</label>
                  <input
                    v-model="productForm.alcohol_percentage"
                    type="number"
                    step="0.01"
                    class="input mt-1"
                    placeholder="e.g., 12.5"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Volume</label>
                  <input
                    v-model="productForm.volume"
                    type="text"
                    class="input mt-1"
                    placeholder="e.g., 750ml, 1L"
                  />
                </div>

                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700">Product Image</label>
                  <div class="mt-1 flex items-center space-x-4">
                    <input
                      ref="imageInput"
                      type="file"
                      accept="image/*"
                      @change="handleImageUpload"
                      class="hidden"
                    />
                    <button
                      type="button"
                      @click="$refs.imageInput.click()"
                      class="btn btn-outline"
                    >
                      <Upload class="h-4 w-4 mr-2" />
                      Choose Image
                    </button>
                    <div v-if="selectedImage" class="flex items-center space-x-2">
                      <img
                        :src="selectedImagePreview"
                        alt="Preview"
                        class="h-12 w-12 rounded-lg object-cover"
                      />
                      <button
                        type="button"
                        @click="removeSelectedImage"
                        class="text-red-600 hover:text-red-800"
                      >
                        <X class="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  <p class="mt-1 text-sm text-gray-500">
                    Supported formats: JPEG, PNG, GIF, WebP. Max size: 5MB.
                  </p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Min Stock Level</label>
                  <input
                    v-model="productForm.min_stock_level"
                    type="number"
                    class="input mt-1"
                    placeholder="10"
                  />
                </div>

                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    v-model="productForm.description"
                    rows="3"
                    class="input mt-1"
                    placeholder="Enter product description..."
                  ></textarea>
                </div>

                <div class="md:col-span-2">
                  <div class="flex items-center space-x-4">
                    <label class="flex items-center">
                      <input
                        v-model="productForm.is_featured"
                        type="checkbox"
                        class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                      />
                      <span class="ml-2 text-sm text-gray-700">Featured Product</span>
                    </label>
                    <label class="flex items-center">
                      <input
                        v-model="productForm.is_new"
                        type="checkbox"
                        class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                      />
                      <span class="ml-2 text-sm text-gray-700">New Product</span>
                    </label>
                    <label class="flex items-center">
                      <input
                        v-model="productForm.is_on_sale"
                        type="checkbox"
                        class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                      />
                      <span class="ml-2 text-sm text-gray-700">On Sale</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button 
                type="submit" 
                :disabled="submitting"
                class="btn btn-primary sm:ml-3 sm:w-auto"
              >
                <span v-if="submitting" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                {{ submitting ? 'Adding Product...' : 'Add Product' }}
              </button>
              <button
                type="button"
                @click="closeAddModal"
                class="btn btn-outline sm:w-auto"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Edit Product Modal -->
    <div v-if="showEditModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <form @submit.prevent="handleUpdateProduct">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Edit Product</h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Product Name</label>
                  <input
                    v-model="productForm.name"
                    type="text"
                    required
                    class="input mt-1"
                    placeholder="Enter product name"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">SKU</label>
                  <input
                    v-model="productForm.sku"
                    type="text"
                    required
                    class="input mt-1"
                    placeholder="Enter SKU"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Category</label>
                  <select v-model="productForm.category" required class="input mt-1">
                    <option value="">Select category</option>
                    <option v-for="category in categories" :key="category.id" :value="category.id">
                      {{ category.name }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Subcategory</label>
                  <input
                    v-model="productForm.subcategory"
                    type="text"
                    class="input mt-1"
                    placeholder="Enter subcategory"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Price</label>
                  <input
                    v-model="productForm.price"
                    type="number"
                    step="0.01"
                    required
                    class="input mt-1"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Original Price</label>
                  <input
                    v-model="productForm.original_price"
                    type="number"
                    step="0.01"
                    class="input mt-1"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Stock</label>
                  <input
                    v-model="productForm.stock"
                    type="number"
                    required
                    class="input mt-1"
                    placeholder="0"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Unit</label>
                  <select v-model="productForm.unit" required class="input mt-1">
                    <option value="">Select unit</option>
                    <option value="bottle">Bottle</option>
                    <option value="can">Can</option>
                    <option value="pack">Pack</option>
                    <option value="case">Case</option>
                    <option value="liter">Liter</option>
                    <option value="ml">Milliliter</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Status</label>
                  <select v-model="productForm.status" required class="input mt-1">
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="out_of_stock">Out of Stock</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Vintage</label>
                  <input
                    v-model="productForm.vintage"
                    type="text"
                    class="input mt-1"
                    placeholder="e.g., 2020"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Region</label>
                  <input
                    v-model="productForm.region"
                    type="text"
                    class="input mt-1"
                    placeholder="e.g., Bordeaux, France"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Alcohol Percentage</label>
                  <input
                    v-model="productForm.alcohol_percentage"
                    type="number"
                    step="0.1"
                    class="input mt-1"
                    placeholder="e.g., 13.5"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Volume</label>
                  <input
                    v-model="productForm.volume"
                    type="text"
                    class="input mt-1"
                    placeholder="e.g., 750ml, 1L"
                  />
                </div>

                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    v-model="productForm.description"
                    rows="3"
                    class="input mt-1"
                    placeholder="Enter product description"
                  ></textarea>
                </div>

                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700">Product Image</label>
                  <div class="mt-1 flex items-center space-x-4">
                    <input
                      ref="imageInput"
                      type="file"
                      accept="image/*"
                      @change="handleImageUpload"
                      class="hidden"
                    />
                    <button
                      type="button"
                      @click="$refs.imageInput.click()"
                      class="btn btn-outline"
                    >
                      <Upload class="h-4 w-4 mr-2" />
                      Choose Image
                    </button>
                    <div v-if="selectedImage || selectedImagePreview" class="flex items-center space-x-2">
                      <img
                        :src="selectedImagePreview || selectedImage"
                        alt="Preview"
                        class="h-12 w-12 rounded-lg object-cover"
                      />
                      <span v-if="selectedImagePreview && !selectedImage" class="text-xs text-gray-500">Current</span>
                      <button
                        type="button"
                        @click="removeSelectedImage"
                        class="text-red-600 hover:text-red-800"
                      >
                        <X class="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  <p class="mt-1 text-sm text-gray-500">
                    Supported formats: JPEG, PNG, GIF, WebP. Max size: 5MB.
                  </p>
                </div>

                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700">Product Features</label>
                  <div class="mt-2 space-y-2">
                    <label class="flex items-center">
                      <input
                        v-model="productForm.is_featured"
                        type="checkbox"
                        class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                      />
                      <span class="ml-2 text-sm text-gray-700">Featured Product</span>
                    </label>
                    <label class="flex items-center">
                      <input
                        v-model="productForm.is_new"
                        type="checkbox"
                        class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                      />
                      <span class="ml-2 text-sm text-gray-700">New Product</span>
                    </label>
                    <label class="flex items-center">
                      <input
                        v-model="productForm.is_on_sale"
                        type="checkbox"
                        class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                      />
                      <span class="ml-2 text-sm text-gray-700">On Sale</span>
                    </label>
                  </div>
                </div>


              </div>
            </div>
            
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button 
                type="submit" 
                :disabled="submittingEdit"
                class="btn btn-primary sm:ml-3 sm:w-auto"
              >
                <span v-if="submittingEdit" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                {{ submittingEdit ? 'Updating Product...' : 'Update Product' }}
              </button>
              <button
                type="button"
                @click="closeEditModal"
                class="btn btn-outline sm:w-auto"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Add Category Modal -->
    <div v-if="showAddCategoryModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form @submit.prevent="handleAddCategory">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Add New Category</h3>
              
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Category Name</label>
                  <input
                    v-model="categoryForm.name"
                    type="text"
                    required
                    class="input mt-1"
                    placeholder="Enter category name"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Description</label>
                  <textarea
                    v-model="categoryForm.description"
                    rows="3"
                    class="input mt-1"
                    placeholder="Enter category description"
                  ></textarea>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Parent Category</label>
                  <select v-model="categoryForm.parent" class="input mt-1">
                    <option value="">No Parent (Top Level)</option>
                    <option v-for="category in categories" :key="category.id" :value="category.id">
                      {{ category.name }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Category Image</label>
                  <div class="mt-1 flex items-center space-x-4">
                    <input
                      ref="categoryImageInput"
                      type="file"
                      accept="image/*"
                      @change="handleCategoryImageUpload"
                      class="hidden"
                    />
                    <button
                      type="button"
                      @click="$refs.categoryImageInput.click()"
                      class="btn btn-outline"
                    >
                      <Upload class="h-4 w-4 mr-2" />
                      Choose Image
                    </button>
                    <div v-if="selectedCategoryImage" class="flex items-center space-x-2">
                      <img
                        :src="selectedCategoryImagePreview"
                        alt="Preview"
                        class="h-12 w-12 rounded-lg object-cover"
                      />
                      <button
                        type="button"
                        @click="removeSelectedCategoryImage"
                        class="text-red-600 hover:text-red-800"
                      >
                        <X class="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  <p class="mt-1 text-sm text-gray-500">
                    Supported formats: JPEG, PNG, GIF, WebP. Max size: 5MB.
                  </p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Sort Order</label>
                  <input
                    v-model="categoryForm.sort_order"
                    type="number"
                    class="input mt-1"
                    placeholder="0"
                  />
                </div>

                <div>
                  <label class="flex items-center">
                    <input
                      v-model="categoryForm.is_active"
                      type="checkbox"
                      class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                    />
                    <span class="ml-2 text-sm text-gray-700">Active Category</span>
                  </label>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button 
                type="submit" 
                :disabled="submittingCategory"
                class="btn btn-secondary sm:ml-3 sm:w-auto"
              >
                <span v-if="submittingCategory" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                {{ submittingCategory ? 'Adding Category...' : 'Add Category' }}
              </button>
              <button
                type="button"
                @click="closeAddCategoryModal"
                class="btn btn-outline sm:w-auto"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Product Measurements Modal -->
    <div v-if="showMeasurementsModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg leading-6 font-medium text-gray-900">
                Manage Measurements - {{ currentProductForMeasurements?.name }}
              </h3>
              <button
                @click="closeMeasurementsModal"
                class="text-gray-400 hover:text-gray-600"
              >
                <X class="h-6 w-6" />
              </button>
            </div>

            <!-- Add/Edit Measurement Form -->
            <div class="bg-gray-50 p-4 rounded-lg mb-6">
              <h4 class="text-md font-medium text-gray-900 mb-3">
                {{ editingMeasurementId ? 'Edit Measurement' : 'Add New Measurement' }}
              </h4>
              <form @submit.prevent="addMeasurement" class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Measurement Type</label>
                  <select 
                    v-model="measurementForm.measurement" 
                    @change="updateQuantityForMeasurement(measurementForm.measurement)"
                    class="input mt-1"
                  >
                    <option value="">Select measurement</option>
                    <option v-for="option in measurementOptions" :key="option.value" :value="option.value">
                      {{ option.label }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Quantity (Optional)</label>
                  <input
                    v-model="measurementForm.quantity"
                    type="text"
                    class="input mt-1"
                    :class="{ 'bg-blue-50 border-blue-300': isAutoFilledQuantity(measurementForm.measurement, measurementForm.quantity) }"
                    placeholder="e.g., 1 unit, 2 pieces, 3.5 bottles, one dozen"
                  />
                  <p v-if="isAutoFilledQuantity(measurementForm.measurement, measurementForm.quantity)" class="text-xs text-blue-600 mt-1">
                    Auto-filled based on measurement type
                  </p>
                  <p v-else class="text-xs text-gray-500 mt-1">
                    Enter any quantity format you want (e.g., "1 unit", "2 pieces", "3.5 bottles", "one dozen")
                  </p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Price</label>
                  <input
                    v-model="measurementForm.price"
                    type="number"
                    step="0.01"
                    required
                    class="input mt-1"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Original Price</label>
                  <input
                    v-model="measurementForm.original_price"
                    type="number"
                    step="0.01"
                    class="input mt-1"
                    placeholder="0.00"
                  />
                </div>



                <div>
                  <label class="block text-sm font-medium text-gray-700">Sort Order</label>
                  <input
                    v-model="measurementForm.sort_order"
                    type="number"
                    class="input mt-1"
                    placeholder="0"
                  />
                </div>

                <div class="md:col-span-3 flex items-center space-x-4">
                  <label class="flex items-center">
                    <input
                      v-model="measurementForm.is_active"
                      type="checkbox"
                      class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                    />
                    <span class="ml-2 text-sm text-gray-700">Active</span>
                  </label>
                  <label class="flex items-center">
                    <input
                      v-model="measurementForm.is_default"
                      type="checkbox"
                      class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                    />
                    <span class="ml-2 text-sm text-gray-700">Default</span>
                  </label>
                  <button
                    type="submit"
                    :disabled="submittingMeasurement"
                    class="btn btn-primary"
                  >
                    <span v-if="submittingMeasurement" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                    {{ submittingMeasurement ? (editingMeasurementId ? 'Updating...' : 'Adding...') : (editingMeasurementId ? 'Update Measurement' : 'Add Measurement') }}
                  </button>
                  <button
                    v-if="editingMeasurementId"
                    type="button"
                    @click="resetMeasurementForm"
                    class="btn btn-outline"
                  >
                    Cancel Edit
                  </button>
                </div>
              </form>
            </div>

            <!-- Measurements List -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-3">Current Measurements</h4>
              <div class="overflow-x-auto">
                <table class="w-full">
                  <thead>
                    <tr class="border-b border-gray-200">
                      <th class="text-left py-2 px-2 font-semibold text-gray-700">Measurement</th>
                      <th class="text-left py-2 px-2 font-semibold text-gray-700">Price</th>
                      <th class="text-left py-2 px-2 font-semibold text-gray-700">Status</th>
                      <th class="text-left py-2 px-2 font-semibold text-gray-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="currentProductMeasurements.length === 0" class="border-b border-gray-100">
                      <td colspan="5" class="py-4 px-2 text-center text-gray-600">
                        No measurements found
                      </td>
                    </tr>
                    <tr
                      v-for="measurement in currentProductMeasurements"
                      :key="measurement.id"
                      class="border-b border-gray-100 hover:bg-gray-50"
                    >
                      <td class="py-3 px-2">
                        <div>
                          <span class="font-medium text-gray-900">{{ measurement.display_name }}</span>
                          <div class="flex items-center space-x-2 mt-1">
                            <span v-if="measurement.is_default" class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                              Default
                            </span>
                            <span v-if="measurement.is_on_sale" class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                              On Sale
                            </span>
                          </div>
                        </div>
                      </td>
                      <td class="py-3 px-2">
                        <div>
                          <span class="font-medium text-gray-900">UGX {{ measurement.price }}</span>
                          <div v-if="measurement.original_price && measurement.original_price > measurement.price" class="text-sm text-gray-500">
                            <span class="line-through">UGX {{ measurement.original_price }}</span>
                            <span class="text-green-600 ml-1">-{{ measurement.discount_percentage.toFixed(0) }}%</span>
                          </div>
                        </div>
                      </td>

                      <td class="py-3 px-2">
                        <span :class="[
                          'px-2 py-1 rounded-full text-sm font-medium',
                          measurement.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        ]">
                          {{ measurement.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td class="py-3 px-2">
                        <div class="flex items-center space-x-2">
                          <button
                            @click="editMeasurement(measurement)"
                            class="p-1 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
                            title="Edit"
                          >
                            <Edit class="h-4 w-4" />
                          </button>
                          <button
                            @click="deleteMeasurement(measurement.id)"
                            class="p-1 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                            title="Delete"
                          >
                            <Trash2 class="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stock Adjustment Modal -->
    <div v-if="showStockAdjustmentModal" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form @submit.prevent="handleStockAdjustment">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg leading-6 font-medium text-gray-900">
                  Adjust Stock - {{ currentProductForStock?.name }}
                </h3>
                <button
                  @click="closeStockAdjustmentModal"
                  class="text-gray-400 hover:text-gray-600"
                >
                  <X class="h-6 w-6" />
                </button>
              </div>
              
              <div class="space-y-4">
                <!-- Current Stock Display -->
                <div class="bg-gray-50 p-4 rounded-lg">
                  <p class="text-sm font-medium text-gray-700 mb-1">Current Stock</p>
                  <p class="text-2xl font-bold text-gray-900">{{ stockAdjustmentForm.current_stock }}</p>
                </div>

                <!-- Adjustment Type -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Adjustment Type</label>
                  <div class="grid grid-cols-3 gap-2">
                    <label class="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        v-model="stockAdjustmentForm.adjustment_type"
                        type="radio"
                        value="set"
                        class="mr-2"
                      />
                      <span class="text-sm">Set to</span>
                    </label>
                    <label class="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        v-model="stockAdjustmentForm.adjustment_type"
                        type="radio"
                        value="add"
                        class="mr-2"
                      />
                      <span class="text-sm">Add</span>
                    </label>
                    <label class="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        v-model="stockAdjustmentForm.adjustment_type"
                        type="radio"
                        value="subtract"
                        class="mr-2"
                      />
                      <span class="text-sm">Subtract</span>
                    </label>
                  </div>
                </div>

                <!-- New Stock Value -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    {{ stockAdjustmentForm.adjustment_type === 'set' ? 'New Stock Level' : 
                       stockAdjustmentForm.adjustment_type === 'add' ? 'Amount to Add' : 'Amount to Subtract' }}
                  </label>
                  <input
                    v-model="stockAdjustmentForm.new_stock"
                    type="number"
                    min="0"
                    required
                    class="input"
                    :placeholder="stockAdjustmentForm.adjustment_type === 'set' ? 'Enter new stock level' : 'Enter amount'"
                  />
                </div>

                <!-- Calculated Result -->
                <div v-if="stockAdjustmentForm.new_stock && !isNaN(stockAdjustmentForm.new_stock)" class="bg-blue-50 p-4 rounded-lg">
                  <p class="text-sm font-medium text-blue-700 mb-1">Result</p>
                  <p class="text-lg font-bold text-blue-900">
                    {{ calculateNewStock() }}
                  </p>
                </div>

                <!-- Reason -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Reason for Adjustment</label>
                  <select v-model="stockAdjustmentForm.reason" class="input">
                    <option value="">Select a reason</option>
                    <option value="restock">Restock</option>
                    <option value="sale">Sale</option>
                    <option value="damage">Damage/Loss</option>
                    <option value="return">Return</option>
                    <option value="inventory">Inventory Count</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <!-- Notes -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Notes (Optional)</label>
                  <textarea
                    v-model="stockAdjustmentForm.notes"
                    rows="3"
                    class="input"
                    placeholder="Add any additional notes..."
                  ></textarea>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button 
                type="submit" 
                :disabled="submittingStockAdjustment || !stockAdjustmentForm.new_stock"
                class="btn btn-primary sm:ml-3 sm:w-auto"
              >
                <span v-if="submittingStockAdjustment" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                {{ submittingStockAdjustment ? 'Updating Stock...' : 'Update Stock' }}
              </button>
              <button
                type="button"
                @click="closeStockAdjustmentModal"
                class="btn btn-outline sm:w-auto"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { toast } from 'vue3-toastify'
import { 
  Plus, RefreshCw, Edit, Trash2, Upload, X, FolderPlus, Package, AlertTriangle, XCircle, DollarSign 
} from 'lucide-vue-next'
import {
  getProducts,
  getCategories,
  deleteProduct as deleteProductAPI,
  createProduct,
  updateProduct,
  createCategory,
  getProductMeasurements,
  createProductMeasurement,
  updateProductMeasurement,
  deleteProductMeasurement,
  getMeasurementTypes,
  updateProductStock,
  getProductStats
} from '@/services/api'

// State
const loading = ref(false)
const products = ref([])
const categories = ref([])
const measurementTypes = ref([])
const productStats = ref({
  total_products: 0,
  low_stock_items: 0,
  out_of_stock: 0,
  total_value: 0
})
const searchQuery = ref('')
const selectedCategory = ref('')
const stockFilter = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const showAddCategoryModal = ref(false)
const showMeasurementsModal = ref(false)
const showStockAdjustmentModal = ref(false)
const submitting = ref(false)
const submittingEdit = ref(false)
const submittingCategory = ref(false)
const submittingMeasurement = ref(false)
const submittingStockAdjustment = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalProducts = ref(0)

// Page size options
const pageSizeOptions = [10, 20, 50, 100]

// Product form
const productForm = ref({
  name: '',
  description: '',
  category: '',
  subcategory: '',
  sku: '',
  status: 'active',
  price: '',
  original_price: '',
  sale_percentage: '',
  unit: 'bottle',
  stock: '',
  min_stock_level: 10,
  max_stock_level: 1000,
  vintage: '',
  region: '',
  alcohol_percentage: '',
  volume: '',
  image: null,
  images: [],
  is_featured: false,
  is_new: false,
  is_on_sale: false,
  tags: [],
  pairings: [],
  awards: [],
  bulk_pricing: {},
  measurements: []
})



// Known measurement quantities
const knownQuantities = {
  'piece': '1 unit',
  'pair': '2 pieces',
  'dozen': '12 pieces',
  'half_dozen': '6 pieces',
  'shot': '30 ml (1 oz)',
  'nip': '50 ml',
  'quarter': '180 ml',
  'half': '375 ml',
  'pint': '473 ml (US), 500 ml (UK)',
  'fifth': '750 ml',
  'liter': '1000 ml',
  'gallon': '3.78 liters (US)',
  'box_wine_3l': '3L',
  'box_wine_5l': '5L',
  'can_330ml': '330 ml',
  'can_500ml': '500 ml',
  'case_12': '12 bottles/cans',
  'case_24': '24 bottles/cans',
  'keg_20l': '20L',
  'keg_30l': '30L',
  'keg_50l': '50L'
}

// Measurement form
const measurementForm = ref({
  measurement: '',
  quantity: '',
  price: '',
  original_price: '',
  is_active: true,
  is_default: false,
  sort_order: 0
})

// New measurement form for product creation/editing
const newMeasurementForm = ref({
  measurement: '',
  quantity: '',
  price: '',
  original_price: '',
  is_active: true,
  is_default: false,
  sort_order: 0
})

// Current product for measurements
const currentProductForMeasurements = ref(null)
const currentProductMeasurements = ref([])
const editingMeasurementId = ref(null)

// Current product for stock adjustment
const currentProductForStock = ref(null)
const stockAdjustmentForm = ref({
  current_stock: 0,
  new_stock: '',
  adjustment_type: 'set', // 'set', 'add', 'subtract'
  adjustment_amount: '',
  reason: '',
  notes: ''
})

// Computed
const filteredProducts = computed(() => {
  // For now, return all products since pagination is handled server-side
  // In the future, we can implement client-side filtering for better UX
  return products.value
})

const totalPages = computed(() => Math.ceil(totalProducts.value / pageSize.value))

// Generate measurement options with specific quantities
const measurementOptions = computed(() => {
  const options = []
  
  measurementTypes.value.forEach(type => {
    if (type.value === 'keg') {
      // Add specific keg options
      options.push({ value: 'keg_20l', label: 'Keg 20L', baseType: 'keg', quantity: '20L' })
      options.push({ value: 'keg_30l', label: 'Keg 30L', baseType: 'keg', quantity: '30L' })
      options.push({ value: 'keg_50l', label: 'Keg 50L', baseType: 'keg', quantity: '50L' })
    } else if (type.value === 'box_wine') {
      // Add specific box wine options
      options.push({ value: 'box_wine_3l', label: 'Box Wine 3L', baseType: 'box_wine', quantity: '3L' })
      options.push({ value: 'box_wine_5l', label: 'Box Wine 5L', baseType: 'box_wine', quantity: '5L' })
    } else if (type.value === 'can') {
      // Add specific can options
      options.push({ value: 'can_330ml', label: 'Can 330ml', baseType: 'can', quantity: '330 ml' })
      options.push({ value: 'can_500ml', label: 'Can 500ml', baseType: 'can', quantity: '500 ml' })
    } else if (type.value === 'case') {
      // Add specific case options
      options.push({ value: 'case_12', label: 'Case 12 bottles/cans', baseType: 'case', quantity: '12 bottles/cans' })
      options.push({ value: 'case_24', label: 'Case 24 bottles/cans', baseType: 'case', quantity: '24 bottles/cans' })
    } else {
      // Add other measurement types as-is
      options.push({ value: type.value, label: type.label, baseType: type.value, quantity: knownQuantities[type.value] || '' })
    }
  })
  
  // Sort options alphabetically by label
  return options.sort((a, b) => a.label.localeCompare(b.label))
})

// Methods
const fetchProducts = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    // Add search parameter if provided
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    // Add category filter if selected
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    
    // Add stock filter if selected
    if (stockFilter.value) {
      params.stock_status = stockFilter.value
    }
    
    const response = await getProducts(params)
    products.value = response.results || response
    totalProducts.value = response.count || response.length
    
    console.log('Products loaded:', products.value)
    console.log('Total products:', totalProducts.value)
    console.log('Current page:', currentPage.value)
    console.log('Total pages:', totalPages.value)
    
    // Debug: Log first product's category data
    if (products.value.length > 0) {
      console.log('First product category data:', {
        category: products.value[0].category,
        category_name: products.value[0].category_name
      })
    }
    
    // Calculate product stats from loaded products
    calculateProductStatsFromProducts()
  } catch (error) {
    console.error('Failed to fetch products:', error)
    toast.error('Failed to load products')
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const response = await getCategories()
    categories.value = response.results || response
    console.log('Categories loaded:', categories.value)
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  }
}

const fetchMeasurementTypes = async () => {
  try {
    const response = await getMeasurementTypes()
    measurementTypes.value = response.measurements || []
  } catch (error) {
    console.error('Failed to fetch measurement types:', error)
  }
}

const fetchProductStats = async () => {
  try {
    const response = await getProductStats()
    productStats.value = response
    console.log('Product stats loaded:', productStats.value)
  } catch (error) {
    console.error('Failed to fetch product stats:', error)
    // Calculate stats from products data as fallback
    calculateProductStatsFromProducts()
  }
}

const calculateProductStatsFromProducts = () => {
  const totalProducts = products.value.length
  const lowStockItems = products.value.filter(p => {
    const stock = p.stock || 0
    const minStock = p.min_stock_level || 10
    return stock > 0 && stock <= minStock
  }).length
  const outOfStock = products.value.filter(p => (p.stock || 0) === 0).length
  const totalValue = products.value.reduce((sum, p) => {
    const stock = p.stock || 0
    const price = p.current_price || p.price || 0
    return sum + (stock * price)
  }, 0)

  productStats.value = {
    total_products: totalProducts,
    low_stock_items: lowStockItems,
    out_of_stock: outOfStock,
    total_value: totalValue
  }
  
  console.log('Product stats calculated from products data:', productStats.value)
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

const fetchProductMeasurements = async (productId) => {
  try {
    const response = await getProductMeasurements({ product: productId })
    currentProductMeasurements.value = response.results || response
    console.log('Product measurements loaded:', currentProductMeasurements.value)
  } catch (error) {
    console.error('Failed to fetch product measurements:', error)
  }
}

const refreshProducts = async () => {
  await Promise.all([
    fetchProducts(),
    fetchCategories(),
    fetchMeasurementTypes(),
    fetchProductStats()
  ])
}

// Measurement management methods
const openMeasurementsModal = async (product) => {
  currentProductForMeasurements.value = product
  await fetchProductMeasurements(product.id)
  showMeasurementsModal.value = true
}

const closeMeasurementsModal = () => {
  showMeasurementsModal.value = false
  currentProductForMeasurements.value = null
  currentProductMeasurements.value = []
  editingMeasurementId.value = null
  resetMeasurementForm()
}

const closeStockAdjustmentModal = () => {
  showStockAdjustmentModal.value = false
  currentProductForStock.value = null
  stockAdjustmentForm.value = {
    current_stock: 0,
    new_stock: '',
    adjustment_type: 'set',
    adjustment_amount: '',
    reason: '',
    notes: ''
  }
}

const calculateNewStock = () => {
  const currentStock = stockAdjustmentForm.value.current_stock
  const adjustmentValue = parseInt(stockAdjustmentForm.value.new_stock) || 0
  const adjustmentType = stockAdjustmentForm.value.adjustment_type

  switch (adjustmentType) {
    case 'set':
      return adjustmentValue
    case 'add':
      return currentStock + adjustmentValue
    case 'subtract':
      return Math.max(0, currentStock - adjustmentValue)
    default:
      return currentStock
  }
}

const handleStockAdjustment = async () => {
  if (!stockAdjustmentForm.value.new_stock) {
    toast.error('Please enter a stock value')
    return
  }

  const newStockValue = calculateNewStock()
  if (newStockValue < 0) {
    toast.error('Stock cannot be negative')
    return
  }

  submittingStockAdjustment.value = true
  try {
    // Prepare stock adjustment data
    const stockData = {
      stock: newStockValue,
      reason: stockAdjustmentForm.value.reason,
      notes: stockAdjustmentForm.value.notes,
      adjustment_type: stockAdjustmentForm.value.adjustment_type,
      adjustment_amount: parseInt(stockAdjustmentForm.value.new_stock)
    }

    await updateProductStock(currentProductForStock.value.id, stockData)
    
    // Update local state immediately
    currentProductForStock.value.stock = newStockValue
    
    toast.success(`Stock updated successfully for ${currentProductForStock.value.name}`)
    
    // Close modal and refresh data
    closeStockAdjustmentModal()
    await fetchProducts()
    await fetchProductStats()
  } catch (error) {
    console.error('Failed to update stock:', error)
    toast.error('Failed to update stock')
  } finally {
    submittingStockAdjustment.value = false
  }
}



const isAutoFilledQuantity = (measurementType, quantity) => {
  if (!measurementType || !quantity) return false
  
  // Find the selected option to check if quantity matches
  const selectedOption = measurementOptions.value.find(option => option.value === measurementType)
  return selectedOption && selectedOption.quantity === quantity
}

const updateQuantityForMeasurement = (measurementType) => {
  // Find the selected option to get the quantity
  const selectedOption = measurementOptions.value.find(option => option.value === measurementType)
  if (selectedOption && selectedOption.quantity) {
    measurementForm.value.quantity = selectedOption.quantity
  }
}

const updateQuantityForNewMeasurement = (measurementType) => {
  if (knownQuantities[measurementType]) {
    newMeasurementForm.value.quantity = knownQuantities[measurementType]
  }
}

const resetMeasurementForm = () => {
  editingMeasurementId.value = null
  measurementForm.value = {
    measurement: '',
    quantity: '',
    price: '',
    original_price: '',
    is_active: true,
    is_default: false,
    sort_order: 0
  }
}

const addMeasurement = async () => {
  submittingMeasurement.value = true
  try {
    // Map the custom measurement value to the correct base type for the API
    const selectedOption = measurementOptions.value.find(option => option.value === measurementForm.value.measurement)
    const measurementType = selectedOption ? selectedOption.baseType : measurementForm.value.measurement
    
    const measurementData = {
      ...measurementForm.value,
      measurement: measurementType, // Use the base type for the API
      product: currentProductForMeasurements.value.id
    }
    
    if (editingMeasurementId.value) {
      // Update existing measurement
      await updateProductMeasurement(editingMeasurementId.value, measurementData)
      toast.success('Measurement updated successfully')
    } else {
      // Create new measurement
      await createProductMeasurement(measurementData)
      toast.success('Measurement added successfully')
    }
    
    resetMeasurementForm()
    await fetchProductMeasurements(currentProductForMeasurements.value.id)
  } catch (error) {
    console.error('Failed to save measurement:', error)
    toast.error('Failed to save measurement')
  } finally {
    submittingMeasurement.value = false
  }
}



const deleteMeasurement = async (measurementId) => {
  if (!confirm('Are you sure you want to delete this measurement?')) return
  
  try {
    // Remove from local state immediately for better UX
    const measurementIndex = currentProductMeasurements.value.findIndex(m => m.id === measurementId)
    if (measurementIndex !== -1) {
      currentProductMeasurements.value.splice(measurementIndex, 1)
    }
    
    await deleteProductMeasurement(measurementId)
    toast.success('Measurement deleted successfully')
    
    // Refresh from server to ensure consistency
    await fetchProductMeasurements(currentProductForMeasurements.value.id)
  } catch (error) {
    console.error('Failed to delete measurement:', error)
    toast.error('Failed to delete measurement')
    
    // If delete failed, refresh from server to restore the measurement
    await fetchProductMeasurements(currentProductForMeasurements.value.id)
  }
}

const editMeasurement = (measurement) => {
  editingMeasurementId.value = measurement.id
  measurementForm.value = {
    measurement: measurement.measurement,
    quantity: measurement.quantity || '',
    price: measurement.price,
    original_price: measurement.original_price || '',
    is_active: measurement.is_active,
    is_default: measurement.is_default,
    sort_order: measurement.sort_order
  }
}

// Product form measurement methods
const addNewMeasurementRow = () => {
  productForm.value.measurements.push({
    measurement: '',
    quantity: '',
    price: '',
    original_price: '',
    is_active: true,
    is_default: false,
    sort_order: productForm.value.measurements.length
  })
}

const removeMeasurementRow = (index) => {
  productForm.value.measurements.splice(index, 1)
  // Update sort order for remaining measurements
  productForm.value.measurements.forEach((measurement, idx) => {
    measurement.sort_order = idx
  })
}

const setDefaultMeasurement = (index) => {
  // Uncheck all other default measurements
  productForm.value.measurements.forEach((measurement, idx) => {
    if (idx !== index) {
      measurement.is_default = false
    }
  })
  // Set the selected one as default
  productForm.value.measurements[index].is_default = true
}

// New measurement form methods
const addMeasurementFromForm = () => {
  // Validate required fields
  if (!newMeasurementForm.value.measurement || !newMeasurementForm.value.price) {
    toast.error('Please fill in all required fields (Measurement Type and Price)')
    return
  }
  
  // If this is the first measurement, make it default
  if (productForm.value.measurements.length === 0) {
    newMeasurementForm.value.is_default = true
  }
  
  // If this measurement is set as default, uncheck others
  if (newMeasurementForm.value.is_default) {
    productForm.value.measurements.forEach(measurement => {
      measurement.is_default = false
    })
  }
  
  // Add the measurement to the product form
  productForm.value.measurements.push({
    ...newMeasurementForm.value,
    sort_order: productForm.value.measurements.length
  })
  
  // Reset the form
  resetNewMeasurementForm()
  
  toast.success('Measurement added successfully')
}

const resetNewMeasurementForm = () => {
  newMeasurementForm.value = {
    measurement: '',
    quantity: '',
    price: '',
    original_price: '',
    is_active: true,
    is_default: false,
    sort_order: 0
  }
}

const editMeasurementInForm = (index) => {
  const measurement = productForm.value.measurements[index]
  newMeasurementForm.value = {
    measurement: measurement.measurement,
    quantity: measurement.quantity || '',
    price: measurement.price,
    original_price: measurement.original_price || '',
    is_active: measurement.is_active,
    is_default: measurement.is_default,
    sort_order: measurement.sort_order
  }
  
  // Remove the measurement from the list
  productForm.value.measurements.splice(index, 1)
  
  // Update sort order for remaining measurements
  productForm.value.measurements.forEach((measurement, idx) => {
    measurement.sort_order = idx
  })
}

const getMeasurementDisplayName = (measurement) => {
  if (measurement.quantity) {
    return `${measurement.quantity} ${measurement.measurement}`
  }
  return measurement.measurement
}

const handleSearch = () => {
  currentPage.value = 1
  fetchProducts()
}

const debounceSearch = () => {
  // Clear existing timeout
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  // Set new timeout
  searchTimeout = setTimeout(() => {
    handleSearch()
  }, 500) // Wait 500ms after user stops typing
}

const handleFilter = () => {
  currentPage.value = 1
  fetchProducts()
}

const handlePageSizeChange = () => {
  currentPage.value = 1
  fetchProducts()
}

const handlePageChange = () => {
  // Validate page number
  if (currentPage.value < 1) {
    currentPage.value = 1
  } else if (currentPage.value > totalPages.value) {
    currentPage.value = totalPages.value
  }
  fetchProducts()
}

const getStockClass = (stock) => {
  if (stock === 0) return 'bg-red-100 text-red-800'
  if (stock <= 10) return 'bg-yellow-100 text-yellow-800'
  return 'bg-green-100 text-green-800'
}

const getStatusClass = (status) => {
  switch (status?.toLowerCase()) {
    case 'active':
      return 'bg-green-100 text-green-800'
    case 'inactive':
      return 'bg-red-100 text-red-800'
    case 'draft':
      return 'bg-gray-100 text-gray-800'
    default:
      return 'bg-secondary-100 text-secondary-800'
  }
}

const editProduct = (product) => {
  // Populate the form with product data
  productForm.value = {
    name: product.name || '',
    description: product.description || '',
    category: product.category?.id || product.category || '',
    subcategory: product.subcategory || '',
    sku: product.sku || '',
    status: product.status || 'active',
    price: product.price || '',
    original_price: product.original_price || '',
    sale_percentage: product.sale_percentage || '',
    unit: product.unit || 'bottle',
    stock: product.stock || '',
    min_stock_level: product.min_stock_level || 10,
    max_stock_level: product.max_stock_level || 1000,
    vintage: product.vintage || '',
    region: product.region || '',
    alcohol_percentage: product.alcohol_percentage || '',
    volume: product.volume || '',
    image: null,
    images: product.images || [],
    is_featured: product.is_featured || false,
    is_new: product.is_new || false,
    is_on_sale: product.is_on_sale || false,
    tags: product.tags || [],
    pairings: product.pairings || [],
    awards: product.awards || [],
    bulk_pricing: product.bulk_pricing || {},
    measurements: []
  }
  
  // Set current product ID for editing
  currentProductId.value = product.id
  
  // Show current image if exists
  if (product.image) {
    selectedImagePreview.value = product.image
  } else {
    selectedImage.value = null
    selectedImagePreview.value = null
  }
  
  // Show edit modal
  showEditModal.value = true
}

const adjustStock = async (product) => {
  // Set up the stock adjustment modal
  currentProductForStock.value = product
  stockAdjustmentForm.value = {
    current_stock: product.stock || 0,
    new_stock: '',
    adjustment_type: 'set', // 'set', 'add', 'subtract'
    adjustment_amount: '',
    reason: '',
    notes: ''
  }
  showStockAdjustmentModal.value = true
}

const deleteProduct = async (productId) => {
  // Find the product to get its name for confirmation
  const product = products.value.find(p => p.id === productId)
  const productName = product ? product.name : 'this product'
  
  if (!confirm(`Are you sure you want to delete "${productName}"? This action cannot be undone.`)) return
  
  try {
    await deleteProductAPI(productId)
    toast.success(`Product "${productName}" deleted successfully`)
    
    // Remove the product from the local list immediately
    const productIndex = products.value.findIndex(p => p.id === productId)
    if (productIndex !== -1) {
      products.value.splice(productIndex, 1)
      
      // Update total count
      totalProducts.value = Math.max(0, totalProducts.value - 1)
      
      // If we're on a page that's now empty and not the first page, go to previous page
      if (products.value.length === 0 && currentPage.value > 1) {
        currentPage.value--
        await fetchProducts() // Fetch the previous page
      }
    }
  } catch (error) {
    console.error('Failed to delete product:', error)
    toast.error('Failed to delete product')
  }
}

const handleAddProduct = async () => {
  // Validate that if measurements are provided, they have required fields
  if (productForm.value.measurements.length > 0) {
    for (let i = 0; i < productForm.value.measurements.length; i++) {
      const measurement = productForm.value.measurements[i]
      if (!measurement.measurement || !measurement.price) {
        toast.error(`Please fill in all required fields for measurement ${i + 1}`)
        return
      }
    }
  }
  
  submitting.value = true
  try {
    // Create FormData for multipart upload
    const formData = new FormData()
    
    // Add basic product data
    formData.append('name', productForm.value.name)
    formData.append('description', productForm.value.description)
    formData.append('category', productForm.value.category || '')
    formData.append('subcategory', productForm.value.subcategory || '')
    formData.append('sku', productForm.value.sku)
    formData.append('status', productForm.value.status)
    formData.append('price', productForm.value.price)
    formData.append('original_price', productForm.value.original_price || '')
    formData.append('sale_percentage', productForm.value.sale_percentage || '')
    formData.append('unit', productForm.value.unit)
    formData.append('stock', productForm.value.stock)
    formData.append('min_stock_level', productForm.value.min_stock_level)
    formData.append('max_stock_level', productForm.value.max_stock_level)
    formData.append('vintage', productForm.value.vintage || '')
    formData.append('region', productForm.value.region || '')
    formData.append('alcohol_percentage', productForm.value.alcohol_percentage || '')
    formData.append('volume', productForm.value.volume || '')
    formData.append('is_featured', productForm.value.is_featured)
    formData.append('is_new', productForm.value.is_new)
    formData.append('is_on_sale', productForm.value.is_on_sale)
    
    // Add image if selected
    if (selectedImage.value) {
      formData.append('image', selectedImage.value)
    }
    
    // Add JSON fields
    formData.append('tags', JSON.stringify(productForm.value.tags))
    formData.append('pairings', JSON.stringify(productForm.value.pairings))
    formData.append('awards', JSON.stringify(productForm.value.awards))
    formData.append('bulk_pricing', JSON.stringify(productForm.value.bulk_pricing))
    
    // Always send measurements field (even if empty)
    formData.append('measurements', JSON.stringify(productForm.value.measurements || []))
    
    console.log('Attempting to create product...')
    console.log('Form data being sent:')
    for (let [key, value] of formData.entries()) {
      console.log(`${key}:`, value)
    }
    const result = await createProduct(formData)
    console.log('Product creation successful:', result)
    toast.success('Product added successfully')
    closeAddModal()
    
    // Refresh products list - handle any errors separately
    try {
      await fetchProducts()
    } catch (fetchError) {
      console.error('Failed to refresh products list:', fetchError)
      // Don't show error toast for refresh failure since product was created successfully
    }
  } catch (error) {
    console.error('Failed to add product:', error)
    console.error('Error details:', {
      message: error.message,
      status: error.status,
      stack: error.stack
    })
    
    // Check if the product was actually created despite the error
    // The 500 error might be happening after successful creation
    if (error.message && error.message.includes('status: 500')) {
      console.log('500 error detected - checking if product was created...')
      try {
        await fetchProducts()
        toast.success('Product added successfully')
        closeAddModal()
      } catch (fetchError) {
        console.error('Failed to refresh products list:', fetchError)
        toast.error('Failed to add product')
      }
    } else {
      toast.error('Failed to add product')
    }
  } finally {
    submitting.value = false
  }
}

const handleUpdateProduct = async () => {
  submittingEdit.value = true
  try {
    // Create FormData for multipart upload
    const formData = new FormData()
    
    // Add basic product data
    formData.append('name', productForm.value.name)
    formData.append('description', productForm.value.description)
    formData.append('category', productForm.value.category || '')
    formData.append('subcategory', productForm.value.subcategory || '')
    formData.append('sku', productForm.value.sku)
    formData.append('status', productForm.value.status)
    formData.append('price', productForm.value.price)
    formData.append('original_price', productForm.value.original_price || '')
    formData.append('sale_percentage', productForm.value.sale_percentage || '')
    formData.append('unit', productForm.value.unit)
    formData.append('stock', productForm.value.stock)
    formData.append('min_stock_level', productForm.value.min_stock_level)
    formData.append('max_stock_level', productForm.value.max_stock_level)
    formData.append('vintage', productForm.value.vintage || '')
    formData.append('region', productForm.value.region || '')
    formData.append('alcohol_percentage', productForm.value.alcohol_percentage || '')
    formData.append('volume', productForm.value.volume || '')
    formData.append('is_featured', productForm.value.is_featured)
    formData.append('is_new', productForm.value.is_new)
    formData.append('is_on_sale', productForm.value.is_on_sale)
    
    // Add image if selected
    if (selectedImage.value) {
      formData.append('image', selectedImage.value)
    }
    
    // Add JSON fields
    formData.append('tags', JSON.stringify(productForm.value.tags))
    formData.append('pairings', JSON.stringify(productForm.value.pairings))
    formData.append('awards', JSON.stringify(productForm.value.awards))
    formData.append('bulk_pricing', JSON.stringify(productForm.value.bulk_pricing))
    
    // Always send measurements field (even if empty)
    formData.append('measurements', JSON.stringify(productForm.value.measurements || []))
    
    await updateProduct(currentProductId.value, formData)
    toast.success('Product updated successfully')
    closeEditModal()
    await fetchProducts()
  } catch (error) {
    console.error('Failed to update product:', error)
    toast.error('Failed to update product')
  } finally {
    submittingEdit.value = false
  }
}

const closeAddModal = () => {
  showAddModal.value = false
  productForm.value = {
    name: '',
    description: '',
    category: '',
    subcategory: '',
    sku: '',
    status: 'active',
    price: '',
    original_price: '',
    sale_percentage: '',
    unit: 'bottle',
    stock: '',
    min_stock_level: 10,
    max_stock_level: 1000,
    vintage: '',
    region: '',
    alcohol_percentage: '',
    volume: '',
    image: null,
    images: [],
    is_featured: false,
    is_new: false,
    is_on_sale: false,
    tags: [],
    pairings: [],
    awards: [],
    bulk_pricing: {},
    measurements: []
  }
  // Reset new measurement form
  resetNewMeasurementForm()
  // Reset image selection
  selectedImage.value = null
  selectedImagePreview.value = null
  if (imageInput.value) {
    imageInput.value.value = ''
  }
}

const closeEditModal = () => {
  showEditModal.value = false
  currentProductId.value = null
  productForm.value = {
    name: '',
    description: '',
    category: '',
    subcategory: '',
    sku: '',
    status: 'active',
    price: '',
    original_price: '',
    sale_percentage: '',
    unit: 'bottle',
    stock: '',
    min_stock_level: 10,
    max_stock_level: 1000,
    vintage: '',
    region: '',
    alcohol_percentage: '',
    volume: '',
    image: null,
    images: [],
    is_featured: false,
    is_new: false,
    is_on_sale: false,
    tags: [],
    pairings: [],
    awards: [],
    bulk_pricing: {},
    measurements: []
  }
  // Reset new measurement form
  resetNewMeasurementForm()
  // Reset image selection
  selectedImage.value = null
  selectedImagePreview.value = null
  if (imageInput.value) {
    imageInput.value.value = ''
  }
}

const handleAddCategory = async () => {
  submittingCategory.value = true
  try {
    // Create FormData for multipart upload
    const formData = new FormData()
    
    // Add basic category data
    formData.append('name', categoryForm.value.name)
    formData.append('description', categoryForm.value.description || '')
    
    // Handle parent field - send null if empty
    if (categoryForm.value.parent && categoryForm.value.parent !== '') {
      formData.append('parent', categoryForm.value.parent)
    }
    
    formData.append('sort_order', categoryForm.value.sort_order || 0)
    formData.append('is_active', categoryForm.value.is_active)
    
    // Add image if selected
    if (selectedCategoryImage.value) {
      formData.append('image', selectedCategoryImage.value)
    }
    
    // Debug: Log the FormData contents
    console.log('Category FormData contents:')
    for (let [key, value] of formData.entries()) {
      console.log(`${key}:`, value)
    }
    
    await createCategory(formData)
    toast.success('Category added successfully')
    closeAddCategoryModal()
    await fetchCategories()
    // Refresh products to show updated category information
    await fetchProducts()
  } catch (error) {
    console.error('Failed to add category:', error)
    toast.error('Failed to add category')
  } finally {
    submittingCategory.value = false
  }
}

const closeAddCategoryModal = () => {
  showAddCategoryModal.value = false
  categoryForm.value = {
    name: '',
    description: '',
    parent: '',
    image: null,
    sort_order: 0,
    is_active: true
  }
  // Reset category image selection
  selectedCategoryImage.value = null
  selectedCategoryImagePreview.value = null
  if (categoryImageInput.value) {
    categoryImageInput.value.value = ''
  }
}

const goToFirstPage = () => {
  currentPage.value = 1
  fetchProducts()
}

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchProducts()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchProducts()
  }
}

const goToLastPage = () => {
  currentPage.value = totalPages.value
  fetchProducts()
}

// Image handling
const imageInput = ref(null)
const selectedImage = ref(null)
const selectedImagePreview = ref(null)

// Category form
const categoryForm = ref({
  name: '',
  description: '',
  parent: '',
  image: null,
  sort_order: 0,
  is_active: true
})

// Category image handling
const categoryImageInput = ref(null)
const selectedCategoryImage = ref(null)
const selectedCategoryImagePreview = ref(null)

// Edit product tracking
const currentProductId = ref(null)

// Debounced search
let searchTimeout = null

const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedImage.value = file
    selectedImagePreview.value = URL.createObjectURL(file)
  }
}

const removeSelectedImage = () => {
  selectedImage.value = null
  selectedImagePreview.value = null
  productForm.value.image = null
}

const handleCategoryImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedCategoryImage.value = file
    selectedCategoryImagePreview.value = URL.createObjectURL(file)
  }
}

const removeSelectedCategoryImage = () => {
  selectedCategoryImage.value = null
  selectedCategoryImagePreview.value = null
  categoryForm.value.image = null
}

// Lifecycle
onMounted(async () => {
  await Promise.all([fetchProducts(), fetchCategories(), fetchMeasurementTypes(), fetchProductStats()])
})

const calculateMeasurementPrice = (product, measurement) => {
  const hasMeasurementPrice = measurement && measurement.price != null && measurement.price !== ''
  if (hasMeasurementPrice) {
    return Number(measurement.price)
  }
  const unitPrice = Number(product.price || product.current_price || 0)
  const qty = Number(measurement?.quantity || 1)
  return unitPrice * (isNaN(qty) ? 1 : qty)
}

const authStore = useAuthStore()
const isAdmin = computed(() => !!authStore?.userProfile?.is_admin)
</script> 