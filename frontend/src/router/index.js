import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Admin from '../views/Admin.vue'
import Faculty from '../views/Faculty.vue'
import Student from '../views/Student.vue'
import AddQuestion from '../components/AddQuestion.vue'
import UploadQuestionBank from '../views/UploadQuestionBank.vue'
import CreateExamForm from '../components/CreateExamForm.vue'
import MakeQuestionPaperPage from '../views/MakeQuestionPaperPage.vue'
import UploadStudents from '../views/UploadStudents.vue'
import AddApplicantsPage from '../views/AddApplicantsPage.vue'
import AddApplicants_exam from '../views/AddApplicants_exam.vue'
import ViewResponsesAdmin from '../views/ViewResponsesAdmin.vue'
import ViewResponsesFaculty from '../views/ViewResponses.vue'
import ViewAnswers from '../views/ViewAnswers.vue'

// ✅ Define routes
const routes = [
  { path: '/', component: Login, name: 'Login' },
  { path: '/admin', name: 'Admin', component: Admin, meta: { requiresAuth: true, role: 'Admin' } },
  { path: '/faculty', name: 'Faculty', component: Faculty, meta: { requiresAuth: true, role: 'Faculty' } },
  { path: '/student', name: 'Student', component: Student, meta: { requiresAuth: true, role: 'Student' } },

  // Admin + Faculty shared routes
  { path: '/exam/:examId/upload-question-bank', name: 'UploadQuestionBank', component: UploadQuestionBank, meta: { requiresAuth: true, role: ['Admin', 'Faculty'] } },
  { path: '/create-exam', component: CreateExamForm, meta: { requiresAuth: true, role: ['Admin', 'Faculty'] } },
  { path: '/upload-students', name: 'UploadStudents', component: UploadStudents, meta: { requiresAuth: true, role: ['Admin', 'Faculty'] } },
  { path: '/exam/:examId/add-applicants-exam', name: 'AddApplicantsexam', component: AddApplicants_exam, meta: { requiresAuth: true, role: ['Admin', 'Faculty'] } },
  { path: '/exam/:examId/add-question', name: 'AddQuestion', component: AddQuestion, meta: { requiresAuth: true, role: ['Admin', 'Faculty'] } },
  { path: '/exam/:examId/make-question-paper', name: 'MakeQuestionPaper', component: MakeQuestionPaperPage, meta: { requiresAuth: true, role: ['Admin', 'Faculty'] } },
  { path: '/add-applicants', name: 'AddApplicants', component: AddApplicantsPage, meta: { requiresAuth: true, role: ['Admin', 'Faculty'] } },
  { path: '/view-answers/:attemptId', name: 'ViewAnswers', component: ViewAnswers, props: true, meta: { requiresAuth: true, role: ['Admin', 'Faculty'] } },

  // Admin specific
  { path: '/responses/:examId', name: 'ViewResponsesAdmin', component: ViewResponsesAdmin, props: true, meta: { requiresAuth: true, role: 'Admin' } },

  // Faculty specific
  { path: '/faculty/view-responses/:examId', name: 'ViewResponses', component: ViewResponsesFaculty, props: true, meta: { requiresAuth: true, role: 'Faculty' } },

  // 404 Redirect
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

// ✅ Create router
const router = createRouter({
  history: createWebHistory(),
  routes
})

// ✅ Enhanced Navigation Guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('role') // saved during login

  // Find meta.role for matched route
  const routeMeta = to.matched.find(record => record.meta && record.meta.role)
  const requiredRole = routeMeta ? routeMeta.meta.role : null

  console.log(`🔒 Navigating to: ${to.path} | Required role: ${requiredRole} | User role: ${userRole}`)

  // --- AUTH REQUIRED ---
  if (to.meta.requiresAuth) {
    if (!token || !userRole) {
      alert('Please login first.')
      return next({ name: 'Login' })
    }

    // Role check
    const hasAccess = Array.isArray(requiredRole)
      ? requiredRole.map(r => r.toLowerCase()).includes(userRole.toLowerCase())
      : requiredRole?.toLowerCase() === userRole.toLowerCase()

    if (!hasAccess) {
      alert('Access denied! Unauthorized role.')
      return next({ path: `/${userRole.toLowerCase()}` })
    }

    console.log('✅ Authorized access')
    return next()
  }

  /* --- PUBLIC ROUTE ---
  if (to.name === 'Login' && userRole && token) {
    // already logged in, redirect to dashboard
    console.log('🔁 Already logged in, redirecting to dashboard')
    return next({ path: `/${userRole.toLowerCase()}` })
  }*/

  next()
})

export default router
