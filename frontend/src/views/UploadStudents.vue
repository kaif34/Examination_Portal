<template>
  <!-- Full gradient background -->
  <div class="min-h-screen p-10 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">

    <!-- Heading & Subheading OUTSIDE the card -->
    <div class="text-center mb-6">
      <h2 class="text-4xl font-bold text-blue-800 flex justify-center items-center gap-2">
        🧑‍🎓 Add Students via Upload
      </h2>      
    </div>

    <!-- Card -->
    <div class="max-w-3xl mx-auto bg-white p-10 rounded-2xl shadow-xl">

      <!-- Download CSV Format -->
      <div class="mb-6 text-sm text-gray-700 text-center">
        Need a format?
        <a
          href="/sample/Applicants.csv"
          download
          class="text-blue-600 underline hover:text-blue-800 transition duration-150"
        >
          Download Sample Excel Template
        </a>
      </div>

      <!-- File Input + Upload Button -->
      <div class="flex items-center border border-green-300 rounded-full overflow-hidden shadow-sm w-full">
        <input
          type="file"
          @change="handleFileUpload"
          accept=".xlsx, .csv"
          class="block w-full text-sm text-gray-500
                 file:mr-4 file:py-2 file:px-4
                 file:rounded-full file:border-0
                 file:text-sm file:font-semibold
                 file:bg-green-100 file:text-green-700
                 hover:file:bg-green-200 transition duration-150"
        />

        <button
          @click="uploadFile"
          :disabled="!selectedFile"
          class="ml-auto bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold text-sm px-6 py-2 transition duration-200 rounded-full rounded-l-none disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          Upload
        </button>
      </div>

      <!-- Upload Status Message -->
      <p v-if="message" class="mt-6 text-center text-green-700 font-semibold">
        {{ message }}
      </p>
      <p v-if="error" class="mt-6 text-center text-red-600 font-semibold">
        {{ error }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const examId = route.params.examId




const selectedFile = ref(null)
const message = ref('')
const error = ref('')

const handleFileUpload = (e) => {
  selectedFile.value = e.target.files[0]
}

const uploadFile = async () => {
  if (!selectedFile.value) return

  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('exam_id', examId)
  formData.append('email', localStorage.getItem('faculty_email'))
  formData.append('role', 'Faculty')


  try {
    const response = await fetch('http://localhost:5001/api/upload_students', {
      method: 'POST',
      body: formData
    })

    const result = await response.json()

    if (response.ok) {
      message.value = result.message || 'Students uploaded successfully!'
      error.value = ''
    } else {
      error.value = result.error || 'Upload failed. Please check the file format.'
      message.value = ''
    }
  } catch (err) {
    error.value = 'Server error or connection failed'
    message.value = ''
  }
}
</script>
