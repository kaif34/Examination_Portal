<template>
  <div class="min-h-screen p-10 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
    <!-- Heading -->
    <div class="text-center mb-6">
      <h2 class="text-4xl font-bold text-blue-800">🧑‍🎓 Add Applicants to Exam</h2>
      <p class="text-lg text-gray-600 mt-2">
        Exam ID: {{ examId }} | Exam Name: {{ examName || 'Loading...' }}
      </p>
    </div>

    <!-- Card -->
    <div class="max-w-4xl mx-auto bg-white p-10 rounded-2xl shadow-xl">
      <!-- All Applicants -->
      <h3 class="text-xl font-semibold mb-4">All Applicants</h3>
      <div v-if="loadingApplicants" class="text-gray-600 mb-4">Loading applicants...</div>
      <div v-if="error" class="text-red-600 mb-4">{{ error }}</div>

      <ul v-if="!loadingApplicants">
        <li
          v-for="applicant in applicants"
          :key="applicant.Applicant_Id"
          class="flex justify-between items-center py-2 border-b"
        >
          <span>{{ applicant.Full_Name }} ({{ applicant.Email }})</span>
          <div class="space-x-2">
            <span
              v-if="isAlreadyAssigned(applicant.Applicant_Id)"
              class="text-green-600 font-semibold text-sm"
            >
              ✅ Already Assigned
            </span>
            <button
              v-else-if="!selectedApplicants.includes(applicant.Applicant_Id)"
              @click="toggleAdd(applicant.Applicant_Id)"
              class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded"
            >
              Add
            </button>
            <button
              v-else
              @click="toggleAdd(applicant.Applicant_Id)"
              class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded"
            >
              Remove
            </button>
          </div>
        </li>
      </ul>

      <!-- Confirm Button -->
      <div class="mt-6 text-center">
        <p class="text-sm mb-2 text-gray-700">Selected: {{ selectedApplicants.length }} applicants</p>
        <button
          @click="confirmAdd"
          :disabled="selectedApplicants.length === 0"
          class="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded disabled:bg-gray-400"
        >
          Confirm
        </button>
      </div>

      <!-- Success & Error Messages -->
      <p v-if="message" class="mt-4 text-center text-green-600 font-semibold">{{ message }}</p>
      <p v-if="error && !message" class="mt-4 text-center text-red-600 font-semibold">{{ error }}</p>

      <!-- Send Email Button or Loading Spinner -->
      <div v-if="assignedApplicants.length > 0" class="mt-4 text-center">
        <button
          v-if="!sendingEmails"
          @click="sendEmails"
          class="bg-green-600 hover:bg-green-700 text-white font-semibold px-6 py-2 rounded shadow"
        >
          📧 Send Email to Assigned Applicants
        </button>

        <div v-else class="text-gray-600 text-sm flex justify-center items-center gap-2 mt-2">
          <svg class="animate-spin h-5 w-5 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor"
              d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
          </svg>
          Sending emails...
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const examId = route.params.examId

const applicants = ref([])
const selectedApplicants = ref([])
const assignedApplicants = ref([])
const examName = ref('')
const examDate = ref('')
const examTime = ref('')
const message = ref('')
const error = ref('')
const loadingApplicants = ref(true)
const sendingEmails = ref(false)

const fetchExamDetails = async () => {
  try {
    const res = await fetch(`http://localhost:5001/api/exam/get_exam_by_id/${examId}`)
    const data = await res.json()
    if (res.ok && data.exam) {
      examName.value = data.exam.Exam_Name
      examDate.value = data.exam.Exam_Date
      examTime.value = data.exam.Exam_Time
    } else {
      error.value = 'Failed to fetch exam details'
    }
  } catch (err) {
    console.error('Failed to fetch exam details', err)
    error.value = 'Error loading exam details'
  }
}

const fetchAssignedApplicants = async () => {
  try {
    const res = await fetch(`http://localhost:5001/api/get_assigned_applicants/${examId}`)
    const data = await res.json()
    if (res.ok && data.success) {
      assignedApplicants.value = data.assignedApplicants
    } else {
      error.value = data.message || 'Failed to load assigned applicants'
    }
  } catch (err) {
    console.error('Error fetching assigned applicants:', err)
    error.value = 'Error loading assigned applicants'
  }
}

const fetchApplicants = async () => {
  loadingApplicants.value = true
  try {
    const res = await fetch('http://localhost:5001/api/applicants')
    const data = await res.json()
    if (res.ok && data.success) {
      applicants.value = data.applicants
    } else {
      error.value = data.message || 'Failed to load applicants'
    }
  } catch (err) {
    console.error('Error fetching applicants:', err)
    error.value = 'Error loading applicants'
  } finally {
    loadingApplicants.value = false
  }
}

const toggleAdd = (id) => {
  if (selectedApplicants.value.includes(id)) {
    selectedApplicants.value = selectedApplicants.value.filter(i => i !== id)
  } else {
    selectedApplicants.value.push(id)
  }
}

const isAlreadyAssigned = (id) => {
  return assignedApplicants.value.some(a => a.Applicant_Id === id)
}

const confirmAdd = async () => {
  try {
    const newApplicants = selectedApplicants.value.filter(id =>
      !assignedApplicants.value.some(a => a.Applicant_Id === id)
    )

    if (newApplicants.length === 0) {
      message.value = 'No new applicants to assign.'
      return
    }

    const response = await fetch('http://localhost:5001/api/assign_applicants', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        exam_id: examId,
        applicant_ids: newApplicants
      })
    })
    const result = await response.json()
    if (response.ok) {
      message.value = `${newApplicants.length} applicants assigned successfully.`
      const newlyAssigned = applicants.value.filter(app =>
        newApplicants.includes(app.Applicant_Id)
      )
      assignedApplicants.value.push(...newlyAssigned)
      selectedApplicants.value = []
    } else {
      error.value = result.error || 'Failed to assign applicants'
    }
  } catch (err) {
    console.error('Error assigning applicants:', err)
    error.value = 'Failed to assign applicants'
  }
}

const sendEmails = async () => {
  sendingEmails.value = true
  message.value = ''
  error.value = ''

  try {
    const response = await fetch('http://localhost:5001/api/send_exam_emails', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        exam: {
          Exam_Id: examId,
          Exam_Name: examName.value,
          Exam_Date: examDate.value,
          Exam_Time: examTime.value
        },
        applicants: assignedApplicants.value
      })
    })
    const data = await response.json()
    if (data.success) {
      message.value = '✅ Emails sent successfully!'
    } else {
      error.value = data.message || '❌ Failed to send emails'
    }
  } catch (err) {
    console.error('Email sending error:', err)
    error.value = '❌ Failed to send emails'
  } finally {
    sendingEmails.value = false
  }
}

onMounted(async () => {
  await fetchExamDetails()
  await fetchAssignedApplicants()
  await fetchApplicants()
})
</script>
