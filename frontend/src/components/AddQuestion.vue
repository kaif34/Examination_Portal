<template>
  <div class="p-10 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 rounded-2xl shadow-xl">
    <!-- Header -->
    <h2 class="text-4xl font-bold text-blue-800 mb-2 text-center">📝 Add Question Bank</h2>
    <p class="text-black-600 text-center mb-8">
      Adding questions for <strong class="text-purple-700">Exam ID: {{ $route.params.examId }}</strong>
    </p>

    <!-- Upload CSV Button and File Input -->
    <div class="mb-8 text-center">
      <input type="file" ref="csvFile" @change="handleFileChange" accept=".csv" class="mb-6"/>
      <button
        @click="uploadCSV"
        :disabled="!selectedFile"
        class="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white px-6 py-2 rounded-full shadow-md transition duration-300 ease-in-out ml-2"
      >
        📤 Upload CSV
      </button>
      <div v-if="csvErrors.length" class="mt-4 text-left max-w-2xl mx-auto">
        <div class="font-bold text-red-600 mb-2">CSV Errors:</div>
        <ul class="text-red-700 pl-6 list-disc">
          <li v-for="err in csvErrors" :key="err">{{ err }}</li>
        </ul>
      </div>
    </div>

    <!-- Add Question Form -->
    <form @submit.prevent="submitForm" class="max-w-4xl mx-auto space-y-6 bg-white p-8 rounded-xl shadow-lg">
      <!-- Question Type -->
      <div>
        <label class="block text-gray-800 font-semibold mb-2">Question Type</label>
        <select v-model="form.question_type" @change="handleTypeChange" class="input-box" required>
          <option value="MCQ">MCQ</option>
          <option value="Fill">Fill in the Blanks</option>
          <option value="TF">True/False</option>
          <option value="OneWord">One Word</option>
        </select>
      </div>

      <!-- Question Text -->
      <div>
        <label class="block text-gray-800 font-semibold mb-2">Question</label>
        <textarea v-model="form.question_text" class="input-box h-28 resize-none" required></textarea>
      </div>

      <!-- MCQ Options -->
      <div v-if="form.question_type === 'MCQ'" class="grid grid-cols-2 gap-4">
        <input v-model="form.option_a" placeholder="Option A" class="input-box" required />
        <input v-model="form.option_b" placeholder="Option B" class="input-box" required />
        <input v-model="form.option_c" placeholder="Option C" class="input-box" required />
        <input v-model="form.option_d" placeholder="Option D" class="input-box" required />
      </div>

      <!-- True/False Options (auto handled, so only show info) -->
      <div v-if="form.question_type === 'TF'" class="p-4 bg-gray-100 rounded-md text-gray-700">
        Options will be automatically set as: <br />
        <strong>Option A = True</strong>, <strong>Option B = False</strong>
      </div>

      <!-- Correct Answer -->
      <div>
        <label class="block text-gray-800 font-semibold mb-2">Correct Answer</label>
        <!-- MCQ: Dropdown of the options -->
        <select
          v-if="form.question_type === 'MCQ'"
          v-model="form.correct_answer"
          class="input-box"
          required
        >
          <option disabled value="">Select Correct Answer</option>
          <option v-if="form.option_a" :value="form.option_a">{{ form.option_a }}</option>
          <option v-if="form.option_b" :value="form.option_b">{{ form.option_b }}</option>
          <option v-if="form.option_c" :value="form.option_c">{{ form.option_c }}</option>
          <option v-if="form.option_d" :value="form.option_d">{{ form.option_d }}</option>
        </select>

        <!-- TF: True/False select -->
        <select
          v-else-if="form.question_type === 'TF'"
          v-model="form.correct_answer"
          class="input-box"
          required
        >
          <option value="True">True</option>
          <option value="False">False</option>
        </select>

        <!-- Others: Free input -->
        <input
          v-else
          v-model="form.correct_answer"
          placeholder="Enter correct answer"
          class="input-box"
          required
        />
      </div>

      <!-- Marks -->
      <div>
        <label class="block text-gray-800 font-semibold mb-2">Marks</label>
        <input v-model="form.marks" type="number" class="input-box" />
      </div>

      <!-- Submit Button -->
      <div class="text-center pt-4">
        <button
          type="submit"
          class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold px-8 py-3 rounded-full shadow-lg transition duration-300"
        >
           Submit Question
        </button>
      </div>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: {
        exam_id: '',
        question_type: 'MCQ',
        question_text: '',
        option_a: '',
        option_b: '',
        option_c: '',
        option_d: '',
        correct_answer: '',
        marks: 1
      },
      selectedFile: null,
      csvErrors: []
    };
  },
  methods: {
    handleTypeChange() {
      if (this.form.question_type === 'TF') {
        this.form.option_a = 'True';
        this.form.option_b = 'False';
        this.form.option_c = '';
        this.form.option_d = '';
        this.form.correct_answer = '';
      } else if (this.form.question_type === 'MCQ') {
        this.form.option_a = '';
        this.form.option_b = '';
        this.form.option_c = '';
        this.form.option_d = '';
        this.form.correct_answer = '';
      } else {
        this.form.option_a = '';
        this.form.option_b = '';
        this.form.option_c = '';
        this.form.option_d = '';
      }
    },
    async submitForm() {
      // MCQ validation
      if (this.form.question_type === 'MCQ') {
        const options = [
          (this.form.option_a || '').trim(),
          (this.form.option_b || '').trim(),
          (this.form.option_c || '').trim(),
          (this.form.option_d || '').trim()
        ];
        const correct = (this.form.correct_answer || '').trim();
        if (!options.includes(correct)) {
          alert('Error: Correct answer must be one of the MCQ options.');
          return;
        }
      }
      // General validation
      if (!String(this.form.correct_answer).trim()) {
        alert('Error: Please enter the correct answer.');
        return;
      }
      try {
        const response = await fetch('http://localhost:5001/api/questions/add', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        });
        const result = await response.json();
        if (response.ok) {
          alert(result.message);
          this.resetForm();
        } else {
          alert('Error: ' + (result.error || 'Failed to add question.'));
        }
      } catch (err) {
        console.error('Request failed:', err);
        alert('An error occurred.');
      }
    },
    resetForm() {
      const examId = this.$route.params.examId;
      this.form = {
        exam_id: examId,
        question_type: 'MCQ',
        question_text: '',
        option_a: '',
        option_b: '',
        option_c: '',
        option_d: '',
        correct_answer: '',
        marks: 1
      };
    },
    handleFileChange(e) {
      this.selectedFile = e.target.files[0] || null;
      this.csvErrors = [];
    },
    async uploadCSV() {
      if (!this.selectedFile) {
        alert('Please select a CSV file before uploading.');
        return;
      }
      this.csvErrors = [];
      try {
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        formData.append('exam_id', this.$route.params.examId);
        formData.append('email', localStorage.getItem('faculty_email'));
        formData.append('role', 'Faculty');
        const response = await fetch('http://localhost:5000/api/questions/upload-csv', {
          method: 'POST',
          body: formData
        });
        const result = await response.json();
        if (response.ok) {
          alert(result.message);
          this.csvErrors = [];
          this.$refs.csvFile.value = '';
          this.selectedFile = null;
        } else {
          // Show all row errors
          if (result.details) {
            this.csvErrors = result.details;
          } else {
            alert('Error: ' + (result.error || 'CSV upload failed.'));
          }
        }
      } catch (err) {
        console.error('CSV upload failed:', err);
        alert('An error occurred while uploading CSV.');
      }
    }
  },
  mounted() {
    this.form.exam_id = this.$route.params.examId;
  }
};
</script>

