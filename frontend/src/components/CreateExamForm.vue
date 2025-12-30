<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'

// Today's date in YYYY-MM-DD format
const today = ref(new Date().toISOString().split('T')[0])

const exam = ref({
  exam_name: '',
  exam_date: today.value,
  exam_time: '',
  duration: '',
  total_questions: '',
  max_marks: '',
  faculty_email: localStorage.getItem('faculty_email') || ''
})

const message = ref('')
const success = ref(false)
const minTime = ref('00:00')

// Live validation: watch date changes
watch(() => exam.value.exam_date, (newDate) => {
  message.value = ''
  success.value = false

  if (!newDate) return

  const selectedDateOnly = new Date(newDate)
  const todayOnly = new Date(today.value)

  if (selectedDateOnly < todayOnly) {
    message.value = '❌ Past dates are not allowed'
    return
  }

  // Update min time if today is selected
  if (newDate === today.value) {
    minTime.value = new Date().toTimeString().slice(0, 5)
  } else {
    minTime.value = '00:00'
  }
})

// Live validation: watch time changes (only if today)
watch(() => exam.value.exam_time, (newTime) => {
  if (!newTime) return

  if (exam.value.exam_date === today.value) {
    const now = new Date()
    const selectedDateTime = new Date(`${exam.value.exam_date}T${newTime}`)
    if (selectedDateTime < now) {
      message.value = '❌ Exam time cannot be in the past'
      return
    }
  }

  // Clear only time-related errors
  if (message.value.includes('time')) {
    message.value = ''
  }
})

const submitExam = async () => {
  if (message.value.startsWith('❌')) {
    success.value = false
    return
  }

  try {
    const res = await axios.post('http://localhost:5001/api/exam/create', exam.value)
    if (res.data.success) {
      success.value = true
      message.value = `✅ Exam created successfully! Exam ID: ${res.data.exam_id}`
      exam.value = {
        exam_name: '',
        exam_date: today.value,
        exam_time: '',
        duration: '',
        total_questions: '',
        max_marks: '',
        faculty_email: localStorage.getItem('faculty_email') || ''
      }
    } else {
      success.value = false
      message.value = res.data.message || 'Failed to create exam'
    }
  } catch (err) {
    success.value = false
    message.value = err.response?.data?.message || 'Server error occurred'
  }
}
</script>

<template>
  <div class="space-y-4 bg-white p-4 shadow rounded">
    <h2 class="text-xl font-semibold mb-2">Create Exam</h2>

    <form @submit.prevent="submitExam" class="space-y-4">
      <div>
        <label class="block font-semibold">Exam Name</label>
        <input v-model="exam.exam_name" type="text" class="w-full p-2 border rounded" required />
      </div>

      <div>
        <label class="block font-semibold">Exam Date</label>
        <input
          v-model="exam.exam_date"
          type="date"
          class="w-full p-2 border rounded"
          required
        />
      </div>

      <div>
        <label class="block font-semibold">Exam Time</label>
        <input
          v-model="exam.exam_time"
          type="time"
          class="w-full p-2 border rounded"
          :min="minTime"
          required
        />
      </div>

      <div>
        <label class="block font-semibold">Duration (Minutes)</label>
        <input v-model="exam.duration" type="number" min="1" class="w-full p-2 border rounded" required />
      </div>

      <div>
        <label class="block font-semibold">Total Questions</label>
        <input v-model="exam.total_questions" type="number" min="1" class="w-full p-2 border rounded" required />
      </div>

      <div>
        <label class="block font-semibold">Max Marks</label>
        <input v-model="exam.max_marks" type="number" min="1" class="w-full p-2 border rounded" required />
      </div>

      <div v-if="message" :class="success ? 'text-green-600' : 'text-red-600'" class="font-semibold">
        {{ message }}
      </div>

      <div class="flex gap-4">
        <button
          type="submit"
          class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Submit Exam
        </button>
        <button
          @click="$emit('closeForm')"
          type="button"
          class="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500"
        >
          Cancel
        </button>
      </div>
    </form>
  </div>
</template>
