<template>
  <div class="min-h-screen flex items-center justify-center bg-cover bg-center bg-no-repeat px-4" style="background-image: url('https://i.ibb.co/4Z8nwSwK/Picsart-25-06-11-14-38-24-117.png');">    
    <div class="bg-white p-8 rounded-2xl shadow-lg w-full max-w-md animate-fade-in">
      <div class="flex justify-center mb-4">
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTpCQrjNAF4Mn0LHjgvQizYtxEzhovvhVohzw&s" style="height:100px" class="nuvlogo" alt="Navrachna University Logo">
      </div>
      <h2 class="text-3xl font-bold text-center text-black-800 mb-2">Examination Portal</h2>
      <p class="text-center text-sm text-gray-500 mb-6">Login with your credentials</p>

      <div class="space-y-4">
        <div>
          <label class="text-sm font-semibold text-gray-700 mb-1 block">Email</label>
          <input
            v-model="email"
            type="email"
            placeholder="Enter Email"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            @keyup.enter="login"
          />
        </div>

        <div>
          <label class="text-sm font-semibold text-gray-700 mb-1 block">Password</label>
          <input
            v-model="password"
            type="password"
            placeholder="Enter Password"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            @keyup.enter="login"
          />
        </div>

        <button
          @click="login"
          class="w-full bg-blue-500 hover:bg-[#386dcd] text-white py-2 rounded-lg font-semibold transition"
        >
          Login
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from '../utils/axiosInstance'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const router = useRouter()

const login = async () => {
  if (!email.value || !password.value) {
    alert("Please enter both email and password")
    return
  }

  try {
    // Send only email and password
    const res = await axios.post('http://localhost:5001/api/auth/login', {
      email: email.value,
      password: password.value
    })

    if (res.data.status === 'success') {
      // Backend now returns the detected 'role'
      const userRole = res.data.role
      
      // Store common data
      localStorage.setItem('role', userRole)
      localStorage.setItem('token', res.data.token) // JWT or session token

      // Handle role-specific data storage and routing
      const lowerRole = userRole.toLowerCase()

      if (lowerRole === 'student') {
        localStorage.setItem('student_email', res.data.email)
        localStorage.setItem('student_name', res.data.name)
        localStorage.setItem('applicant_id', res.data.id)
        router.push('/student')
      } 
      else if (lowerRole === 'faculty') {
        localStorage.setItem('faculty_email', res.data.email)
        localStorage.setItem('faculty_name', res.data.name)
        router.push('/faculty')
      } 
      else if (lowerRole === 'admin') {
        localStorage.setItem('admin_email', res.data.email)
        localStorage.setItem('admin_name', res.data.name)
        router.push('/admin')
      }
      else {
        alert('Unknown role detected')
      }

    } else {
      alert(res.data.message || 'Invalid credentials')
    }
  } catch (err) {
    console.error(err)
    alert(err.response?.data?.error || 'Server error. Try again.')
  }
}
</script>

<style scoped>
.login-body::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: url('<defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1.5" fill="rgba(255,255,255,0.05)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/>');
  animation: float 20s ease-in-out infinite;
  pointer-events: none;
  z-index: 0;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(30px, -30px) rotate(120deg); }
  66% { transform: translate(-20px, 20px) rotate(240deg); }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out;
}
</style>