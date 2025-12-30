<template>
  <div class="min-h-screen" style="background: linear-gradient(to bottom right, #E3F2FD, #F3E5F5, #FCE4EC);">
    <div class="px-6 py-6">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-4xl font-bold text-blue-600">Welcome, {{ adminName }}</h1>
        <button
          @click="logout"
          class="bg-red-500 hover:bg-red-600 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition-all duration-200 transform hover:scale-105"
        >
          Logout
        </button>
      </div>

      <div class="flex flex-wrap gap-4 mb-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-6 py-3 rounded-full font-semibold shadow-lg transition-all duration-200 transform hover:scale-105',
            activeTab === tab.id
              ? 'bg-blue-600 text-white'
              : 'bg-blue-500 hover:bg-blue-600 text-white'
          ]"
        >
          {{ tab.name }}
        </button>
      </div>

      <div v-if="activeTab === 'faculty'" class="space-y-6">
        <div class="bg-white/80 backdrop-blur-sm shadow-xl rounded-2xl p-8 border border-white/20">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold text-gray-800">Faculty Management</h2>
            <button
              @click="showAddFacultyModal = true"
              class="bg-blue-500 hover:bg-blue-600 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition-all duration-200 transform hover:scale-105"
            >
              Add Faculty
            </button>
          </div>

          <div class="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-200">
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-gradient-to-r from-blue-50 to-blue-100">
                  <tr>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">ID</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">Name</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">Email</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">School</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">Designation</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-100">
                  <tr v-for="(faculty, idx) in facultyList" :key="faculty.Faculty_Id" class="hover:bg-gray-50 transition-colors duration-200">
                    <td class="py-4 px-6 text-gray-900">{{ idx + 1 }}</td>
                    <td class="py-4 px-6 text-gray-900">{{ faculty.F_Name }}</td>
                    <td class="py-4 px-6 text-gray-900">{{ faculty.F_Email }}</td>
                    <td class="py-4 px-6 text-gray-900">{{ getSchoolName(faculty.School_Id) }}</td>
                    <td class="py-4 px-6 text-gray-900">{{ faculty.Designation }}</td>
                    <td class="py-4 px-6 space-x-2">
                      <button
                        @click="editFaculty(faculty)"
                        class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 transform hover:scale-105"
                      >
                        Edit
                      </button>
                      <button
                        @click="deleteFaculty(faculty.Faculty_Id)"
                        class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 transform hover:scale-105"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'schools'" class="space-y-6">
        <div class="bg-white/80 backdrop-blur-sm shadow-xl rounded-2xl p-8 border border-white/20">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold text-gray-800">Schools Management</h2>
            <button
              @click="showAddSchoolModal = true"
              class="bg-blue-500 hover:bg-blue-600 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition-all duration-200 transform hover:scale-105"
            >
              Add School
            </button>
          </div>

          <div class="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-200">
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-gradient-to-r from-blue-50 to-blue-100">
                  <tr>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">ID</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">School Name</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">Short Name</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-100">
                  <tr v-for="(school, idx) in schoolsList" :key="school.School_Id" class="hover:bg-gray-50 transition-colors duration-200">
                    <td class="py-4 px-6 text-gray-900">{{ idx + 1 }}</td>
                    <td class="py-4 px-6 text-gray-900">{{ school.School_Name }}</td>
                    <td class="py-4 px-6 text-gray-900">{{ school.School_Short }}</td>
                    <td class="py-4 px-6 space-x-2">
                      <button
                        @click="editSchool(school)"
                        class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 transform hover:scale-105"
                      >
                        Edit
                      </button>
                      <button
                        @click="deleteSchool(school.School_Id)"
                        class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 transform hover:scale-105"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'applicants'" class="space-y-6">
        <div class="flex gap-4 mb-6">
          <button
            @click="showAddApplicantForm = !showAddApplicantForm"
            class="bg-blue-500 hover:bg-blue-600 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition-all duration-200 transform hover:scale-105"
          >
            {{ showAddApplicantForm ? 'Close' : 'Add Applicants' }}
          </button>
          <button
            @click="navigateTo('UploadStudents')"
            class="bg-purple-500 hover:bg-purple-600 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition-all duration-200 transform hover:scale-105"
          >
            Upload Applicants
          </button>
        </div>

        <div v-if="showAddApplicantForm" class="bg-white/80 backdrop-blur-sm shadow-xl rounded-2xl p-8 border border-white/20 mb-6">
          <h3 class="text-2xl font-bold text-gray-800 mb-6">Add New Applicant</h3>
          <form @submit.prevent="submitApplicant">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Full Name</label>
                <input
                  v-model="newApplicant.Full_Name"
                  type="text"
                  required
                  class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter full name"
                >
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Email</label>
                <input
                  v-model="newApplicant.Email"
                  type="email"
                  required
                  class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter email address"
                >
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Password</label>
                <input
                  v-model="newApplicant.Password"
                  type="password"
                  required
                  class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter password"
                >
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Phone</label>
                <input
                  v-model="newApplicant.Phone"
                  type="tel"
                  class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter phone number"
                >
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Date of Birth</label>
                <input
                  v-model="newApplicant.DOB"
                  type="date"
                  class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                >
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Gender</label>
                <select
                  v-model="newApplicant.Gender"
                  class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                >
                  <option value="">Select Gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div class="md:col-span-2">
                <label class="block text-sm font-semibold text-gray-700 mb-2">Address</label>
                <textarea
                  v-model="newApplicant.Address"
                  rows="3"
                  class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter address"
                ></textarea>
              </div>
            </div>
            <div class="flex justify-end space-x-4 mt-8">
              <button
                type="button"
                @click="showAddApplicantForm = false"
                class="px-6 py-3 text-sm font-semibold text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-full transition-all duration-200 transform hover:scale-105"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-6 py-3 text-sm font-semibold text-white bg-blue-500 hover:bg-blue-600 rounded-full transition-all duration-200 transform hover:scale-105"
              >
                Add Applicant
              </button>
            </div>
          </form>
        </div>

        <div class="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-200">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gradient-to-r from-blue-50 to-blue-100">
                <tr>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">
                    <input type="checkbox" @change="toggleAllApplicants" :checked="selectedApplicants.length === applicantsList.length && applicantsList.length > 0" />
                  </th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">ID</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Name</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Email</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Phone</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Gender</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Registration Date</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-100">
                <tr v-for="(applicant, idx) in applicantsList" :key="applicant.Applicant_Id" class="hover:bg-gray-50 transition-colors duration-200">
                  <td class="py-4 px-6">
                    <input type="checkbox" :value="applicant.Applicant_Id" v-model="selectedApplicants" />
                  </td>
                  <td class="py-4 px-6 text-gray-900">{{ idx + 1 }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ applicant.Full_Name }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ applicant.Email }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ applicant.Phone }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ applicant.Gender }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ formatDate(applicant.Registration_Date) }}</td>
                  <td class="py-4 px-6 space-x-2">
                    <button
                      @click="viewApplicant(applicant)"
                      class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 transform hover:scale-105"
                    >
                      View
                    </button>
                    <button
                      @click="deleteApplicant(applicant.Applicant_Id)"
                      class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 transform hover:scale-105"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="applicantsList.length === 0" class="text-center py-12 text-gray-500">
            No applicants found. Add some applicants to get started.
          </div>
          <div v-else class="flex justify-end px-6 py-4 bg-gray-50">
            <button
              @click="bulkDeleteApplicants"
              :disabled="selectedApplicants.length === 0"
              class="bg-red-500 hover:bg-red-600 text-white font-semibold px-4 py-2 rounded-lg text-sm shadow-md disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
            >
              Delete Selected ({{ selectedApplicants.length }})
            </button>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'exams'" class="space-y-6">
        <div class="flex gap-4 mb-6">
          <button
            @click="showCreateExamForm = !showCreateExamForm"
            class="bg-blue-500 hover:bg-blue-600 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition-all duration-200 transform hover:scale-105"
          >
            {{ showCreateExamForm ? 'Close' : 'Create Exam' }}
          </button>
        </div>

        <div v-if="showCreateExamForm" class="bg-white/80 backdrop-blur-sm shadow-xl rounded-2xl p-8 border border-white/20 mb-6">
          <h3 class="text-2xl font-bold text-gray-800 mb-6">Create New Exam</h3>
          <form @submit.prevent="submitExam">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Exam Name</label>
                <input
                  v-model="examForm.exam_name"
                  type="text"
                  required
                  class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter exam name"
                >
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Exam Date</label>
                <input
                  v-model="examForm.exam_date"
                  type="date"
                  required
                  class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                >
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Exam Time</label>
                <input
                  v-model="examForm.exam_time"
                  type="time"
                  required
                  class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                >
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Duration (Minutes)</label>
                <input
                  v-model="examForm.duration"
                  type="number"
                  required
                  class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter duration in minutes"
                >
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Total Questions</label>
                <input
                  v-model="examForm.total_questions"
                  type="number"
                  required
                  class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter total questions"
                >
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Maximum Marks</label>
                <input
                  v-model="examForm.max_marks"
                  type="number"
                  required
                  class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  placeholder="Enter maximum marks"
                >
              </div>
            </div>
            <div class="flex justify-end space-x-4 mt-8">
              <button
                type="button"
                @click="showCreateExamForm = false"
                class="px-6 py-3 text-sm font-semibold text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-full transition-all duration-200 transform hover:scale-105"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-6 py-3 text-sm font-semibold text-white bg-blue-500 hover:bg-blue-600 rounded-full transition-all duration-200 transform hover:scale-105"
              >
                Create Exam
              </button>
            </div>
          </form>
        </div>

        <div class="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-200">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gradient-to-r from-blue-50 to-blue-100">
                <tr>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">ID</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Exam Name</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Date</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Time</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Duration (Min)</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Questions</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Max Marks</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-100">
                <tr v-for="(exam, idx) in visibleCreatedExams" :key="exam.Exam_Id" class="hover:bg-gray-50 transition-colors duration-200">
                  <td class="py-4 px-6 text-gray-900">{{ idx + 1 }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ exam.Exam_Name }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ formatDate(exam.Exam_Date) }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ exam.Exam_Time }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ exam.Duration_Minutes }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ exam.Total_Questions }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ exam.Max_Marks }}</td>
                  <td class="py-4 px-6 space-x-2">
                    <button
                      @click="navigateToAddStudents(exam.Exam_Id)"
                      class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 transform hover:scale-105"
                    >
                      Add Students
                    </button>
                    <button
                      @click="navigateToAddQuestions(exam.Exam_Id)"
                      class="bg-green-500 hover:bg-green-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 transform hover:scale-105"
                    >
                      Add Question Bank
                    </button>
                    <button
                      @click="navigateToMakeQuestionPaper(exam.Exam_Id)"
                      class="bg-purple-500 hover:bg-purple-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 transform hover:scale-105"
                    >
                      Make Question Paper
                    </button>
                    <button
                      @click="deleteExam(exam.Exam_Id)"
                      class="bg-red-500 hover:bg-red-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 transform hover:scale-105"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="visibleCreatedExams.length === 0" class="text-center py-12 text-gray-500">
            No exams created yet. Create your first exam to get started.
          </div>
        </div>

        <div v-if="conductedExams && conductedExams.length" class="mt-12 bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-200">
          <div class="px-6 py-4 bg-gradient-to-r from-purple-50 to-purple-100 border-b border-purple-200">
            <h2 class="text-2xl font-bold text-purple-900">Conducted Exams</h2>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gradient-to-r from-blue-50 to-blue-100">
                <tr>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">ID</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Exam Name</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Date</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Faculty Email</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Total Applicants</th>
                  <th class="text-left py-4 px-6 font-semibold text-blue-900">Attempted</th>
                  <th class="text-center py-4 px-6 font-semibold text-blue-900">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-100">
                <tr v-for="(exam, idx) in conductedExams" :key="exam.Exam_Id" class="hover:bg-gray-50 transition-colors duration-200">
                  <td class="py-4 px-6 text-gray-900">{{ idx + 1 }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ exam.Exam_Name || 'N/A' }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ formatDate(exam.Exam_Date) }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ exam.faculty_email || 'N/A' }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ exam.total_applicants || 0 }}</td>
                  <td class="py-4 px-6 text-gray-900">{{ exam.attempted_applicants || 0 }}</td>
                  <td class="py-4 px-6 text-center">
                   <button
                    @click="$router.push({ name: 'ViewResponsesAdmin', params: { examId: exam.Exam_Id } })"
                    class="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 transform hover:scale-105 shadow-md"
                  >
                    View Responses
                  </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'admins'" class="space-y-6">
        <div class="bg-white/80 backdrop-blur-sm shadow-xl rounded-2xl p-8 border border-white/20">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-2xl font-bold text-gray-800">Admins Management</h2>
            <button
              @click="showAddAdminModal = true"
              class="bg-blue-500 hover:bg-blue-600 text-white font-semibold px-6 py-3 rounded-full shadow-lg transition-all duration-200 transform hover:scale-105"
            >
              Add Admin
            </button>
          </div>

          <div class="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead>
                  <tr class="bg-gradient-to-r from-blue-50 to-blue-100 border-b border-blue-200">
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">ID</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">Name</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">Email</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-white">
                  <tr v-for="(admin, idx) in adminsList" :key="admin.Admin_ID" class="border-b border-gray-100 hover:bg-gray-50 transition-colors duration-200">
                    <td class="py-4 px-6 text-gray-700 font-medium">{{ idx + 1 }}</td>
                    <td class="py-4 px-6 text-gray-700">{{ admin.Name }}</td>
                    <td class="py-4 px-6 text-gray-700">{{ admin.Email }}</td>
                    <td class="py-4 px-6 space-x-2">
                      <button @click="editAdmin(admin)" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 transform hover:scale-105 shadow-md">Edit</button>
                      <button @click="deleteAdmin(admin.Admin_ID)" class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 transform hover:scale-105 shadow-md">Delete</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'logs'" class="space-y-6">
        <div class="bg-white/80 backdrop-blur-sm shadow-xl rounded-2xl p-8 border border-white/20">
          <h2 class="text-2xl font-bold text-gray-800 mb-6">Login Logs</h2>

          <div class="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead>
                  <tr class="bg-gradient-to-r from-blue-50 to-blue-100 border-b border-blue-200">
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">ID</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">User Email</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">Role</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">Login Time</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">Logout Time</th>
                    <th class="text-left py-4 px-6 font-semibold text-blue-900">Actions</th>
                  </tr>
                </thead>
                <tbody class="bg-white">
                  <tr v-for="(log, idx) in logsList" :key="log.Log_ID" class="border-b border-gray-100 hover:bg-gray-50 transition-colors duration-200">
                    <td class="py-4 px-6 text-gray-700 font-medium">{{ idx + 1 }}</td>
                    <td class="py-4 px-6 text-gray-700">{{ log.User_Email }}</td>
                    <td class="py-4 px-6">
                      <span :class="getRoleColor(log.Role)" class="px-3 py-1 rounded-full text-xs font-medium">
                        {{ log.Role }}
                      </span>
                    </td>
                    <td class="py-4 px-6 text-gray-700">{{ formatDateTime(log.Login_Time) || 'N/A' }}</td>
                    <td class="py-4 px-6 text-gray-700">{{ formatDateTime(log.Logout_Time) || 'N/A' }}</td>
                    <td class="py-4 px-6 space-x-2">
                      <button @click="viewLog(log)" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 transform hover:scale-105 shadow-md">View</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="message" class="fixed top-4 right-4 z-[100] max-w-md">
      <div
        :class="[
          'p-4 rounded-xl shadow-2xl border-l-4 transform transition-all duration-300 ease-in-out',
          messageType === 'error'
            ? 'bg-red-50 text-red-800 border-red-500'
            : 'bg-green-50 text-green-800 border-green-500'
        ]"
        class="animate-slide-in-right"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg v-if="messageType === 'error'" class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
              <svg v-else class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium">{{ message }}</p>
            </div>
          </div>
          <div class="ml-4 flex-shrink-0">
            <button @click="message = ''" class="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 transition ease-in-out duration-150">
              <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showAddFacultyModal || showEditFacultyModal" class="fixed inset-0 bg-black/60 backdrop-blur-md overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
      <div class="bg-white shadow-2xl rounded-3xl p-8 w-full max-w-md mx-auto border-0 relative">
        <h3 class="text-2xl font-bold text-gray-800 mb-8 text-center">
          {{ showAddFacultyModal ? 'Add Faculty' : 'Edit Faculty' }}
        </h3>
        <form @submit.prevent="showAddFacultyModal ? addFaculty() : updateFaculty()">
          <div class="space-y-4">
            <input v-model="facultyForm.Faculty_Id" type="hidden">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">Name</label>
              <input
                v-model="facultyForm.F_Name"
                type="text"
                required
                class="w-full border border-gray-200 rounded-2xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-purple-50 focus:bg-white"
              >
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">Email</label>
              <input
                v-model="facultyForm.F_Email"
                type="email"
                required
                class="w-full border border-gray-200 rounded-2xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-purple-50 focus:bg-white"
              >
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">School</label>
              <select
                v-model="facultyForm.School_Id"
                required
                class="w-full border border-gray-200 rounded-2xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-purple-50 focus:bg-white"
              >
                <option value="">Select School</option>
                <option v-for="school in schoolsList" :key="school.School_Id" :value="school.School_Id">
                  {{ school.School_Name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">Designation</label>
              <input
                v-model="facultyForm.Designation"
                type="text"
                required
                class="w-full border border-gray-200 rounded-2xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-purple-50 focus:bg-white"
              >
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">Password</label>
              <div class="relative">
                <input
                  v-model="facultyForm.Password"
                  :type="showFacultyPassword ? 'text' : 'password'"
                  required
                  class="w-full border border-gray-200 rounded-2xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-purple-50 focus:bg-white pr-10"
                >
                <button
                  type="button"
                  @click="showFacultyPassword = !showFacultyPassword"
                  class="absolute inset-y-0 right-0 flex items-center px-3 text-gray-500 hover:text-blue-500 focus:outline-none"
                >
                  <svg v-if="!showFacultyPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path></svg>
                </button>
              </div>
            </div>
          </div>
          <div class="flex justify-center space-x-4 mt-8">
            <button
              type="button"
              @click="closeFacultyModal"
              class="px-8 py-3 text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-full transition-all duration-200 transform hover:scale-105 min-w-[100px]"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-8 py-3 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-full transition-all duration-200 transform hover:scale-105 min-w-[100px]"
            >
              {{ showAddFacultyModal ? 'Add' : 'Update' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showAddSchoolModal || showEditSchoolModal" class="fixed inset-0 bg-black/60 backdrop-blur-md overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
      <div class="bg-white shadow-2xl rounded-3xl p-8 w-full max-w-md mx-auto border-0 relative">
        <h3 class="text-2xl font-bold text-gray-800 mb-8 text-center">
          {{ showAddSchoolModal ? 'Add School' : 'Edit School' }}
        </h3>
        <form @submit.prevent="showAddSchoolModal ? addSchool() : updateSchool()">
          <div class="space-y-4">
            <input v-model="schoolForm.School_Id" type="hidden">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">School Name</label>
              <input
                v-model="schoolForm.School_Name"
                type="text"
                required
                class="w-full border border-gray-200 rounded-2xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-purple-50 focus:bg-white"
              >
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">Short Name</label>
              <input
                v-model="schoolForm.School_Short"
                type="text"
                required
                class="w-full border border-gray-200 rounded-2xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-purple-50 focus:bg-white"
              >
            </div>
          </div>
          <div class="flex justify-center space-x-4 mt-8">
            <button
              type="button"
              @click="closeSchoolModal"
              class="px-8 py-3 text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-full transition-all duration-200 transform hover:scale-105 min-w-[100px]"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-8 py-3 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-full transition-all duration-200 transform hover:scale-105 min-w-[100px]"
            >
              {{ showAddSchoolModal ? 'Add' : 'Update' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showViewApplicantModal" class="fixed inset-0 bg-black/60 backdrop-blur-md overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
      <div class="bg-white shadow-2xl rounded-3xl p-8 w-full max-w-md mx-auto border-0 relative">
        <h3 class="text-2xl font-bold text-gray-800 mb-8 text-center">Applicant Details</h3>
        <div v-if="selectedApplicant" class="space-y-6">
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">Name:</span>
            <span class="text-gray-800 font-medium">{{ selectedApplicant.Full_Name }}</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">Email:</span>
            <span class="text-gray-800 font-medium">{{ selectedApplicant.Email }}</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">Phone:</span>
            <span class="text-gray-800 font-medium">{{ selectedApplicant.Phone }}</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">DOB:</span>
            <span class="text-gray-800 font-medium">{{ formatDate(selectedApplicant.DOB) }}</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">Gender:</span>
            <span class="text-gray-800 font-medium">{{ selectedApplicant.Gender }}</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">Address:</span>
            <span class="text-gray-800 font-medium">{{ selectedApplicant.Address }}</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">Registration Date:</span>
            <span class="text-gray-800 font-medium">{{ formatDate(selectedApplicant.Registration_Date) }}</span>
          </div>
        </div>
        <div class="flex justify-center space-x-4 mt-8">
          <button
            @click="showViewApplicantModal = false"
            class="px-8 py-3 text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-full transition-all duration-200 transform hover:scale-105 min-w-[100px]"
          >
            Close
          </button>
        </div>
      </div>
    </div>

    <div v-if="showAddAdminModal || showEditAdminModal" class="fixed inset-0 bg-black/60 backdrop-blur-md overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
      <div class="bg-white shadow-2xl rounded-3xl p-8 w-full max-w-md mx-auto border-0 relative">
        <h3 class="text-2xl font-bold text-gray-800 mb-8 text-center">
          {{ showAddAdminModal ? 'Add Admin' : 'Edit Admin' }}
        </h3>
        <form @submit.prevent="showAddAdminModal ? addAdmin() : updateAdmin()">
          <div class="space-y-4">
            <input v-model="adminForm.Admin_ID" type="hidden">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">Name</label>
              <input v-model="adminForm.Name" type="text" required class="w-full border border-gray-200 rounded-2xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-purple-50 focus:bg-white">
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">Email</label>
              <input v-model="adminForm.Email" type="email" required class="w-full border border-gray-200 rounded-2xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-purple-50 focus:bg-white">
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-3">Password</label>
              <div class="relative">
                <input v-model="adminForm.Password" :type="showAdminPassword ? 'text' : 'password'" required class="w-full border border-gray-200 rounded-2xl px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-purple-50 focus:bg-white pr-10">
                 <button
                  type="button"
                  @click="showAdminPassword = !showAdminPassword"
                  class="absolute inset-y-0 right-0 flex items-center px-3 text-gray-500 hover:text-blue-500 focus:outline-none"
                >
                  <svg v-if="!showAdminPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path></svg>
                </button>
              </div>
            </div>
          </div>
          <div class="flex justify-center space-x-4 mt-8">
            <button type="button" @click="closeAdminModal" class="px-8 py-3 text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-full transition-all duration-200 transform hover:scale-105 min-w-[100px]">Cancel</button>
            <button type="submit" class="px-8 py-3 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-full transition-all duration-200 transform hover:scale-105 min-w-[100px]">
              {{ showAddAdminModal ? 'Add' : 'Update' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showViewLogModal" class="fixed inset-0 bg-black/60 backdrop-blur-md overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
      <div class="bg-white shadow-2xl rounded-3xl p-8 w-full max-w-md mx-auto border-0 relative">
        <h3 class="text-2xl font-bold text-gray-800 mb-8 text-center">Login Log Details</h3>
        <div v-if="selectedLog" class="space-y-6">
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">Log ID:</span>
            <span>{{ selectedLog.Log_ID }}</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">User Email:</span>
            <span>{{ selectedLog.User_Email }}</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">Role:</span>
            <span>{{ selectedLog.Role }}</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">Login Time:</span>
            <span>{{ formatDateTime(selectedLog.Login_Time) || 'N/A' }}</span>
          </div>
          <div class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">Logout Time:</span>
            <span>{{ formatDateTime(selectedLog.Logout_Time) || 'N/A' }}</span>
          </div>
          <div v-if="selectedLog.Student_ID" class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">Student ID:</span>
            <span>{{ selectedLog.Student_ID }}</span>
          </div>
          <div v-if="selectedLog.Student_Name" class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">Student Name:</span>
            <span>{{ selectedLog.Student_Name }}</span>
          </div>
          <div v-if="selectedLog.Applicant_ID" class="flex justify-between items-center py-2 border-b border-gray-100">
            <span class="font-semibold text-gray-700">Applicant ID:</span>
            <span>{{ selectedLog.Applicant_ID }}</span>
          </div>
        </div>
        <div class="flex justify-center space-x-4 mt-8">
          <button @click="showViewLogModal = false" class="px-8 py-3 text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-full transition-all duration-200 transform hover:scale-105 min-w-[100px]">Close</button>
        </div>
      </div>
    </div>

    <div v-if="showUploadApplicantsModal" class="fixed inset-0 bg-black/60 backdrop-blur-md overflow-y-auto h-full w-full z-50 flex items-center justify-center p-4">
      <div class="bg-white shadow-2xl rounded-3xl p-8 w-full max-w-md mx-auto border-0 relative">
        <h3 class="text-2xl font-bold text-gray-800 mb-8 text-center">Upload Applicants</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              Select CSV/Excel File
            </label>
            <input
              ref="fileInput"
              type="file"
              accept=".csv,.xlsx,.xls"
              @change="handleFileSelect"
              class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            >
          </div>
          
          <div class="bg-purple-100 p-4 rounded-xl border border-purple-200">
            <p class="text-sm font-semibold text-gray-700 mb-2">Expected CSV Format:</p>
            <code class="text-xs text-gray-600">
              Full_Name,Email,Password,Phone,DOB,Gender,Address<br>
              John Doe,john@example.com,password123,1234567890,1990-01-01,Male,123 Street
            </code>
          </div>
          
          <div v-if="uploadProgress > 0" class="w-full bg-gray-200 rounded-full h-3">
            <div 
              class="bg-blue-600 h-3 rounded-full transition-all duration-300" 
              :style="{ width: uploadProgress + '%' }"
            ></div>
          </div>
          
          <div v-if="uploadResults" class="space-y-2">
            <div v-if="uploadResults.success > 0" class="text-green-600 text-sm font-medium">
              ✅ Successfully uploaded: {{ uploadResults.success }} applicants
            </div>
            <div v-if="uploadResults.errors.length > 0" class="text-red-600 text-sm font-medium">
              ❌ Errors: {{ uploadResults.errors.length }}
              <ul class="list-disc list-inside mt-1 max-h-20 overflow-y-auto">
                <li v-for="error in uploadResults.errors.slice(0, 5)" :key="error" class="text-xs">
                  {{ error }}
                </li>
                <li v-if="uploadResults.errors.length > 5" class="text-xs">
                  ... and {{ uploadResults.errors.length - 5 }} more errors
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <div class="flex justify-center space-x-4 mt-8">
          <button
            type="button"
            @click="closeUploadModal"
            class="px-8 py-3 text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-full transition-all duration-200 transform hover:scale-105 min-w-[100px]"
          >
            Close
          </button>
          <button
            @click="uploadApplicants"
            :disabled="!selectedFile || isUploading"
            class="px-8 py-3 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-full transition-all duration-200 transform hover:scale-105 min-w-[100px]"
          >
            {{ isUploading ? 'Uploading...' : 'Upload' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable react-hooks/rules-of-hooks, react-hooks/exhaustive-deps */
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import axios from 'axios'
import { useRouter, useRoute } from 'vue-router'

// --- Vue Router Setup ---
const route = useRoute()
const router = useRouter()
// --- End Vue Router Setup ---

// Data
// Initialize activeTab from the query string (fallback to 'faculty')
const activeTab = ref(typeof route.query.tab === 'string' ? route.query.tab : 'faculty')
const facultyList = ref([])
const schoolsList = ref([])
const applicantsList = ref([])
const adminsList = ref([])
const logsList = ref([])

// Added for conducted exams
const conductedExamsList = ref([]) // Updated initialization

// Message system
const message = ref('')
const messageType = ref('success')

// Selection for bulk operations
const selectedApplicants = ref([])

// Modals
const showAddFacultyModal = ref(false)
const showEditFacultyModal = ref(false)
const showAddSchoolModal = ref(false)
const showEditSchoolModal = ref(false)
const showViewApplicantModal = ref(false)
const showAddAdminModal = ref(false)
const showEditAdminModal = ref(false)
const showViewLogModal = ref(false)
const showUploadApplicantsModal = ref(false) // Added for upload modal

// Password Visibility States
const showFacultyPassword = ref(false)
const showAdminPassword = ref(false)

// Forms
const facultyForm = ref({
  Faculty_Id: null,
  F_Name: '',
  F_Email: '',
  School_Id: '',
  Designation: '',
  Password: ''
})

const schoolForm = ref({
  School_Id: null,
  School_Name: '',
  School_Short: ''
})

const adminForm = ref({
  Admin_ID: null,
  Name: '',
  Email: '',
  Password: ''
})

const selectedApplicant = ref(null)
const selectedLog = ref(null)

// Add these new reactive variables
const showAddApplicantForm = ref(false)
const selectedFile = ref(null)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadResults = ref(null)

const newApplicant = ref({
  Full_Name: '',
  Email: '',
  Password: '',
  Phone: '',
  DOB: '',
  Gender: '',
  Address: ''
})

// Exam management
const showCreateExamForm = ref(false)
const examsList = ref([])
// const conductedExamsList = ref([]) // This was moved up

const examForm = ref({
  exam_name: '',
  exam_date: '',
  exam_time: '',
  duration: '',
  total_questions: '',
  max_marks: '',
  faculty_email: localStorage.getItem('admin_email') || ''
})

// Admin user info
const adminName = ref('Admin')
const adminEmail = ref(localStorage.getItem('admin_email') || '') // Reuse same key as mentioned in the code

// Tabs
const tabs = [
  { id: 'faculty', name: 'Faculty' },
  { id: 'schools', name: 'Schools' },
  { id: 'applicants', name: 'Applicants' },
  { id: 'exams', name: 'Exams' },
  { id: 'admins', name: 'Admins' },
  { id: 'logs', name: 'Login Logs' }
]

// API Base URL
const API_BASE = 'http://localhost:5001/api'

// Computed property for conducted exams
const conductedExams = computed(() => conductedExamsList.value) // Added computed property

const isExamEnded = (exam) => {
  try {
    const dateStr = typeof exam.Exam_Date === 'string'
      ? exam.Exam_Date
      : new Date(exam.Exam_Date).toISOString().slice(0, 10)
    const timeStr = (exam.Exam_Time ?? '00:00:00').toString()
    const start = new Date(`${dateStr}T${timeStr}`)
    if (Number.isNaN(start.getTime())) return false
    const durationMin = Number(exam.Duration_Minutes || 0)
    const end = new Date(start.getTime() + durationMin * 60_000)
    return end.getTime() <= Date.now()
  } catch {
    return false
  }
}

// Created exams: only show exams that have NOT ended yet
const visibleCreatedExams = computed(() => examsList.value.filter(exam => !isExamEnded(exam)))

// Message system helper
const showMessage = (msg, type = 'success') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 6000) // Auto-hide after 6 seconds
}

// Bulk operations
const toggleAllApplicants = () => {
  if (selectedApplicants.value.length === applicantsList.value.length) {
    selectedApplicants.value = []
  } else {
    selectedApplicants.value = applicantsList.value.map(a => a.Applicant_Id)
  }
}

const bulkDeleteApplicants = async () => {
  if (selectedApplicants.value.length === 0) return
  
  if (confirm(`Are you sure you want to delete ${selectedApplicants.value.length} applicants? This will also delete their exam attempts and login logs.`)) {
    try {
      await axios.post(`${API_BASE}/admin/applicants/bulk-delete`, {
        applicant_ids: selectedApplicants.value
      })
      await fetchApplicants()
      selectedApplicants.value = []
      showMessage(`Successfully deleted applicants`)
    } catch (error) {
      console.error('Error in bulk delete:', error)
      showMessage(error.response?.data?.error || 'Error deleting applicants', 'error')
    }
  }
}

const fetchAdmins = async () => {
  try {
    const response = await axios.get(`${API_BASE}/admin/admins`)
    adminsList.value = response.data
  } catch (error) {
    console.error('Error fetching admins:', error)
    showMessage('Error fetching admins data', 'error')
  }
}

const fetchLogs = async () => {
  try {
    const response = await axios.get(`${API_BASE}/admin/logs`)
    logsList.value = response.data
  } catch (error) {
    console.error('Error fetching logs:', error)
    showMessage('Error fetching logs data', 'error')
  }
}

// Admin methods
const addAdmin = async () => {
  try {
    await axios.post(`${API_BASE}/admin/admins`, adminForm.value)
    await fetchAdmins()
    closeAdminModal()
    showMessage('Admin added successfully')
  } catch (error) {
    console.error('Error adding admin:', error)
    showMessage(error.response?.data?.error || 'Error adding admin', 'error')
  }
}

const editAdmin = (admin) => {
  adminForm.value = { ...admin }
  showEditAdminModal.value = true
  showAdminPassword.value = false // Reset password visibility
}

const updateAdmin = async () => {
  try {
    await axios.put(`${API_BASE}/admin/admins/${adminForm.value.Admin_ID}`, adminForm.value)
    await fetchAdmins()
    closeAdminModal()
    showMessage('Admin updated successfully')
  } catch (error) {
    console.error('Error updating admin:', error)
    showMessage(error.response?.data?.error || 'Error updating admin', 'error')
  }
}

const deleteAdmin = async (id) => {
  if (confirm('Are you sure you want to delete this admin?')) {
    try {
      await axios.delete(`${API_BASE}/admin/admins/${id}`)
      await fetchAdmins()
      showMessage('Admin deleted successfully')
    } catch (error) {
      console.error('Error deleting admin:', error)
      showMessage(error.response?.data?.error || 'Error deleting admin', 'error')
    }
  }
}

// Log methods
const viewLog = (log) => {
  selectedLog.value = log
  showViewLogModal.value = true
}

// Modal close methods
const closeAdminModal = () => {
  showAddAdminModal.value = false
  showEditAdminModal.value = false
  adminForm.value = {
    Admin_ID: null,
    Name: '',
    Email: '',
    Password: ''
  }
  showAdminPassword.value = false
}

// Methods
const fetchFaculty = async () => {
  try {
    const response = await axios.get(`${API_BASE}/admin/faculty`)
    facultyList.value = response.data
  } catch (error) {
    console.error('Error fetching faculty:', error)
    showMessage('Error fetching faculty data', 'error')
  }
}

const fetchSchools = async () => {
  try {
    const response = await axios.get(`${API_BASE}/admin/schools`)
    schoolsList.value = response.data
  } catch (error) {
    console.error('Error fetching schools:', error)
    showMessage('Error fetching schools data', 'error')
  }
}

const fetchApplicants = async () => {
  try {
    const response = await axios.get(`${API_BASE}/admin/applicants`)
    applicantsList.value = response.data
  } catch (error) {
    console.error('Error fetching applicants:', error)
    showMessage('Error fetching applicants data', 'error')
  }
}

const addFaculty = async () => {
  try {
    await axios.post(`${API_BASE}/admin/faculty`, facultyForm.value)
    await fetchFaculty()
    closeFacultyModal()
    showMessage('Faculty added successfully')
  } catch (error) {
    console.error('Error adding faculty:', error)
    showMessage(error.response?.data?.error || 'Error adding faculty', 'error')
  }
}

const editFaculty = (faculty) => {
  facultyForm.value = { ...faculty }
  showEditFacultyModal.value = true
  showFacultyPassword.value = false // Reset visibility
}

const updateFaculty = async () => {
  try {
    await axios.put(`${API_BASE}/admin/faculty/${facultyForm.value.Faculty_Id}`, facultyForm.value)
    await fetchFaculty()
    closeFacultyModal()
    showMessage('Faculty updated successfully')
  } catch (error) {
    console.error('Error updating faculty:', error)
    showMessage(error.response?.data?.error || 'Error updating faculty', 'error')
  }
}

const deleteFaculty = async (id) => {
  if (confirm('Are you sure you want to delete this faculty member?')) {
    try {
      await axios.delete(`${API_BASE}/admin/faculty/${id}`)
      await fetchFaculty()
      showMessage('Faculty deleted successfully')
    } catch (error) {
      console.error('Error deleting faculty:', error)
      showMessage(error.response?.data?.error || 'Error deleting faculty', 'error')
    }
  }
}

const addSchool = async () => {
  try {
    await axios.post(`${API_BASE}/admin/schools`, schoolForm.value)
    await fetchSchools()
    closeSchoolModal()
    showMessage('School added successfully')
  } catch (error) {
    console.error('Error adding school:', error)
    showMessage(error.response?.data?.error || 'Error adding school', 'error')
  }
}

const editSchool = (school) => {
  schoolForm.value = { ...school }
  showEditSchoolModal.value = true
}

const updateSchool = async () => {
  try {
    await axios.put(`${API_BASE}/admin/schools/${schoolForm.value.School_Id}`, schoolForm.value)
    await fetchSchools()
    closeSchoolModal()
    showMessage('School updated successfully')
  } catch (error) {
    console.error('Error updating school:', error)
    showMessage(error.response?.data?.error || 'Error updating school', 'error')
  }
}

const deleteSchool = async (id) => {
  if (confirm('Are you sure you want to delete this school?')) {
    try {
      await axios.delete(`${API_BASE}/admin/schools/${id}`)
      await fetchSchools()
      showMessage('School deleted successfully')
    } catch (error) {
      console.error('Error deleting school:', error)
      showMessage(error.response?.data?.error || 'Error deleting school', 'error')
    }
  }
}

const viewApplicant = (applicant) => {
  selectedApplicant.value = applicant
  showViewApplicantModal.value = true
}

const deleteApplicant = async (id) => {
  if (confirm('Are you sure you want to delete this applicant? This will also delete their exam attempts and login logs.')) {
    try {
      const response = await axios.delete(`${API_BASE}/admin/applicants/${id}`)
      await fetchApplicants()
      showMessage(response.data.message)
    } catch (error) {
      console.error('Error deleting applicant:', error)
      showMessage(error.response?.data?.error || 'Error deleting applicant', 'error')
    }
  }
}

const closeFacultyModal = () => {
  showAddFacultyModal.value = false
  showEditFacultyModal.value = false
  facultyForm.value = {
    Faculty_Id: null,
    F_Name: '',
    F_Email: '',
    School_Id: '',
    Designation: '',
    Password: ''
  }
  showFacultyPassword.value = false
}

const closeSchoolModal = () => {
  showAddSchoolModal.value = false
  showEditSchoolModal.value = false
  schoolForm.value = {
    School_Id: null,
    School_Name: '',
    School_Short: ''
  }
}

// Submit new applicant
const submitApplicant = async () => {
  try {
    const response = await axios.post(`${API_BASE}/applicants/add`, newApplicant.value)
    if (response.data.success) {
      showMessage('Applicant added successfully!')
      await fetchApplicants()
      showAddApplicantForm.value = false
      // Reset form
      newApplicant.value = {
        Full_Name: '',
        Email: '',
        Password: '',
        Phone: '',
        DOB: '',
        Gender: '',
        Address: ''
      }
    } else {
      showMessage(response.data.message || 'Failed to add applicant Duplicate entry ', 'error')
    }
  } catch (error) {
    console.error('Error adding applicant:', error)
    showMessage(error.response?.data?.error || 'Error adding applicant', 'error')
  }
}

// Handle file selection
const handleFileSelect = (event) => {
  selectedFile.value = event.target.files[0]
  uploadResults.value = null
  uploadProgress.value = 0
}

// Upload applicants from file
const uploadApplicants = async () => {
  if (!selectedFile.value) {
    showMessage('Please select a file first', 'error')
    return
  }

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    isUploading.value = true
    uploadProgress.value = 0
    
    // Simulate progress
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)

    const response = await axios.post(`${API_BASE}/applicants/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    clearInterval(progressInterval)
    uploadProgress.value = 100

    if (response.data.success) {
      uploadResults.value = {
        success: response.data.successful_uploads || 0,
        errors: response.data.errors || []
      }
      await fetchApplicants()
      showMessage(`Successfully uploaded ${response.data.successful_uploads} applicants!`)
    } else {
      uploadResults.value = {
        success: 0,
        errors: [response.data.message || 'Upload failed']
      }
      showMessage('Upload failed', 'error')
    }
  } catch (error) {
    console.error('Error uploading applicants:', error)
    uploadResults.value = {
      success: 0,
      errors: [error.response?.data?.error || 'Upload failed']
    }
    showMessage('Error uploading applicants', 'error')
  } finally {
    isUploading.value = false
  }
}

// Close upload modal
const closeUploadModal = () => {
  showUploadApplicantsModal.value = false
  selectedFile.value = null
  uploadResults.value = null
  uploadProgress.value = 0
  isUploading.value = false
}

// Exam methods
const fetchExams = async () => {
  if (!adminEmail.value) return;
  try {
    const response = await axios.get(`${API_BASE}/exam/get_exams/${adminEmail.value}`)
    if (response.data.success) {
      examsList.value = response.data.exams
    }
  } catch (error) {
    console.error('Error fetching exams:', error)
    showMessage('Error fetching exams data', 'error')
  }
}

// Updated fetchConductedExams function
const fetchConductedExams = async () => {
  try {
    const response = await axios.get(`${API_BASE}/admin/conducted_exams`)
    if (response.data.success) {
      conductedExamsList.value = response.data.exams
    }
  } catch (error) {
    console.error('Error fetching conducted exams:', error)
    showMessage('Error fetching conducted exams', 'error')
  }
}

const submitExam = async () => {
  try {
    const response = await axios.post(`${API_BASE}/exam/create`, examForm.value)
    if (response.data.success) {
      showMessage('Exam created successfully!')
      await fetchExams()
      showCreateExamForm.value = false
      // Reset form
      examForm.value = {
        exam_name: '',
        exam_date: '',
        exam_time: '',
        duration: '',
        total_questions: '',
        max_marks: '',
        admin_email: adminEmail.value
      }
    } else {
      showMessage(response.data.message || 'Failed to create exam', 'error')
    }
  } catch (error) {
    console.error('Error creating exam:', error)
    showMessage('Error creating exam', 'error')
  }
}

const deleteExam = async (examId) => {
  if (confirm('Are you sure you want to delete this exam?')) {
    try {
      const response = await axios.delete(`${API_BASE}/exam/delete/${examId}`)
      if (response.data.success) {
        showMessage('Exam deleted successfully!')
        await fetchExams()
        await fetchConductedExams()
      } else {
        showMessage(response.data.error || 'Failed to delete exam', 'error')
      }
    } catch (error) {
      console.error('Error deleting exam:', error)
      const errorMsg = error.response?.data?.error || error.message || 'Error deleting exam'
      showMessage(errorMsg, 'error')
    }
  }
}

// Navigation function with route mapping (same as Faculty.vue)
const navigateTo = (action, examId) => {
  const routeMap = {
    AddApplicants_exam: 'AddApplicantsexam',
    AddQuestion: 'AddQuestion',
    MakeQuestionPaper: 'MakeQuestionPaper',
    UploadStudents: 'UploadStudents', // Added for the upload button
    ViewResponses: 'ViewResponses'
  }
  if (examId) {
    router.push({ name: routeMap[action], params: { examId } })
  } else {
    router.push({ name: routeMap[action] })
  }
}

// Navigation methods for exam actions
const navigateToAddStudents = (examId) => {
  navigateTo('AddApplicants_exam', examId)
}

const navigateToAddQuestions = (examId) => {
  navigateTo('AddQuestion', examId)
}

const navigateToMakeQuestionPaper = (examId) => {
  navigateTo('MakeQuestionPaper', examId)
}

const getSchoolName = (schoolId) => {
  const school = schoolsList.value.find(s => s.School_Id === schoolId)
  return school ? school.School_Name : 'Unknown'
}

const logout = async () => {
  const email = localStorage.getItem('admin_email') // Again, adjust if you use different keys for admin
  const role = 'Admin'
  
  try {
    // Call backend logout API
    await axios.post('http://localhost:5001/api/auth/logout', {
      email,
      role
    });
    
    // Clear local storage
    localStorage.removeItem('admin_email')
    localStorage.removeItem('admin_name')
    
    // Redirect to login page
    window.location.href = '/'
  } catch (err) {
    console.error('Logout error:', err);
    alert('Logout failed. Try again.');
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  
  const isoString = dateString.includes('T') ? dateString : dateString.replace(' ', 'T')
  const date = new Date(isoString)
  return isNaN(date.getTime()) ? 'Invalid Date' : date.toLocaleDateString('en-IN')
}

// Utility methods
const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  // Convert MySQL datetime to ISO format
  const isoString = dateString.includes('T') ? dateString : dateString.replace(' ', 'T')
  const date = new Date(isoString)
  return isNaN(date.getTime()) ? 'Invalid Date' : date.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })
}

const getRoleColor = (role) => {
  switch (role) {
    case 'Admin': return 'bg-purple-100 text-purple-800'
    case 'Faculty': return 'bg-blue-100 text-blue-800'
    case 'Student': return 'bg-green-100 text-green-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

// Watcher to update URL when activeTab changes
watch(activeTab, (val) => {
  // Keep other existing query params
  const q = { ...route.query, tab: val }
  router.replace({ name: 'Admin', query: q })
})

let refreshTimer
onMounted(async () => {
  adminName.value = localStorage.getItem('admin_name') || 'Admin';
  adminEmail.value = localStorage.getItem('admin_email') || '';
  examForm.value.admin_email = adminEmail.value; // Set email for exam form
  
  await fetchSchools()
  await fetchFaculty()
  await fetchApplicants()
  await fetchAdmins()
  await fetchLogs()
  await fetchExams()
  await fetchConductedExams() // Call the updated function

  // refresh every 60s to auto-move ended exams
  refreshTimer = setInterval(async () => {
    await fetchExams()
    await fetchConductedExams()
  }, 60_000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<style scoped>
@keyframes slide-in-right {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.animate-slide-in-right {
  animation: slide-in-right 0.3s ease-out;
}
</style>