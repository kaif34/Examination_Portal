<template>
  <div class="min-h-screen w-full bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex flex-col items-center py-10">
    <div class="w-full max-w-[1600px] px-8">
      <h1 class="text-3xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-purple-700 to-pink-500 tracking-tight">
        Submitted Answers for Attempt {{ attemptId }}
      </h1>
      <div v-if="error" class="mb-6 p-4 bg-red-100 text-red-700 border border-red-400 rounded w-full">
        {{ error }}
      </div>
      <div class="rounded-xl shadow-xl overflow-x-auto bg-white">
        <table class="min-w-full border-separate border-spacing-0">
          <thead>
            <tr class="bg-gradient-to-r from-purple-200 to-pink-200 text-purple-900 font-bold">
              <th class="py-4 px-6 text-left">Question</th>
              <th class="py-4 px-6 text-left">Selected Option</th>
              <th class="py-4 px-6 text-left">Answer Text</th>
              <th class="py-4 px-6 text-left">Correct Answer</th>
              <th class="py-4 px-6 text-left">Result</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in answers" :key="a.Answer_Id" class="hover:bg-pink-50 transition-colors duration-150 border-b border-gray-100">
              <td class="py-3 px-6">{{ a.Question_Text }}</td>
              <td class="py-3 px-6 break-words">{{ a.Selected_Option_Id || '-' }}</td>
              <td class="py-3 px-6 break-words">{{ a.Answer_Text || '-' }}</td>
              <td class="py-3 px-6 break-words">{{ a.Correct_Answer || '-' }}</td>
              <td class="py-3 px-6">
                <span :class="isCorrect(a) ? 'text-green-600 font-bold' : 'text-red-600 font-bold'">
                  {{ isCorrect(a) ? 'Correct' : 'Incorrect' }}
                </span>
              </td>
            </tr>
            <tr v-if="answers.length === 0">
              <td colspan="5" class="text-center py-8 text-gray-500 italic">No answers found.</td>
            </tr>
          </tbody>
        </table>
      </div>
      <button
        @click="goBack"
        class="mt-8 bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-full font-semibold shadow transition"
      >
        Back to Attempts
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const attemptId = ref(route.params.attemptId)
const answers = ref([])
const error = ref('')

const fetchAnswers = async () => {
  error.value = ''
  try {
    const response = await fetch(`http://localhost:5001/api/answers/${attemptId.value}`)
    const data = await response.json()
    if (!response.ok) {
      error.value = data.error || 'Failed to load answers'
    } else {
      answers.value = data.answers
    }
  } catch (e) {
    error.value = 'Error fetching answers: ' + e.message
  }
}

const isCorrect = (answer) => {
  if (!answer.Correct_Answer) return false
  return (answer.Answer_Text || '').trim().toLowerCase() === (answer.Correct_Answer || '').trim().toLowerCase()
}

const goBack = () => {
  router.back()
}

onMounted(fetchAnswers)
</script>

<style scoped>
/* Tailwind handles styling */
</style>
