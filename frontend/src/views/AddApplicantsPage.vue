<template>
  <div class="p-6 max-w-2xl mx-auto">
    <h2 class="text-2xl font-bold mb-6">Add Applicant</h2>
    <form @submit.prevent="submitApplicant" class="space-y-4">

      <div>
        <label class="block font-semibold">Full Name</label>
        <input v-model="applicant.Full_Name" required class="w-full border px-3 py-2 rounded" />
      </div>

      <div>
        <label class="block font-semibold">Email</label>
        <input v-model="applicant.Email" type="email" required class="w-full border px-3 py-2 rounded" />
      </div>

      <div>
        <label class="block font-semibold">Password</label>
        <input v-model="applicant.Password" type="password" required class="w-full border px-3 py-2 rounded" />
      </div>

      <div>
        <label class="block font-semibold">Phone</label>
        <input v-model="applicant.Phone" class="w-full border px-3 py-2 rounded" />
      </div>

      <div>
        <label class="block font-semibold">DOB</label>
        <input v-model="applicant.DOB" type="date" class="w-full border px-3 py-2 rounded" />
      </div>

      <div>
        <label class="block font-semibold">Gender</label>
        <select v-model="applicant.Gender" class="w-full border px-3 py-2 rounded">
          <option value="">Select</option>
          <option>Male</option>
          <option>Female</option>
          <option>Other</option>
        </select>
      </div>

      <div>
        <label class="block font-semibold">Address</label>
        <textarea v-model="applicant.Address" class="w-full border px-3 py-2 rounded"></textarea>
      </div>

      <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
        Save Applicant
      </button>
    </form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import axios from 'axios'

const applicant = reactive({
  Full_Name: '',
  Email: '',
  Password: '',
  Phone: '',
  DOB: '',
  Gender: '',
  Address: ''
})

const submitApplicant = async () => {
  try {
    const res = await axios.post('http://localhost:5001/api/applicants/add', applicant)
    alert('Applicant added successfully!')
    Object.keys(applicant).forEach(key => applicant[key] = '')  // reset form
  } catch (err) {
    console.error(err)
    alert('Error adding applicant.')
  }
}
</script>
