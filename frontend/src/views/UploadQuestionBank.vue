<template>
  <!-- Full gradient background -->
  <div class="min-h-screen p-10 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">

    <!-- Heading & Subheading (OUTSIDE CARD) -->
    <div class="text-center mb-6">
      <h2 class="text-4xl font-bold text-blue-800 flex justify-center items-center gap-2">
        📤 Upload Question Bank (CSV)
      </h2>
      <p class="text-gray-600">
        Uploading for <strong class="text-purple-700">Exam ID: {{ examId }}</strong>
      </p>
    </div>

    <!-- Card -->
    <div class="max-w-3xl mx-auto bg-white p-10 rounded-2xl shadow-xl">

      <!-- Download CSV Format -->
      <div class="mb-6 text-sm text-gray-700 text-center">
        Need a format?
        <a
          href="http://localhost:5001/static/sample_question_bank.csv"
          download
          class="text-blue-600 underline hover:text-blue-800 transition duration-150"
        >
          Download Sample CSV Format
        </a>
      </div>

      <!-- File Input + Upload Button -->
      <div class="flex items-center border border-green-300 rounded-full overflow-hidden shadow-sm w-full">
        <input
          type="file"
          @change="handleFileChange"
          accept=".csv"
          class="block w-full text-sm text-gray-500
                 file:mr-4 file:py-2 file:px-4
                 file:rounded-full file:border-0
                 file:text-sm file:font-semibold
                 file:bg-green-100 file:text-green-700
                 hover:file:bg-green-200 transition duration-150"
        />

        <button
          @click="uploadCSV"
          class="ml-auto bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold text-sm px-6 py-2 transition duration-200 rounded-full rounded-l-none"
        >
          Upload
        </button>
      </div>

      <!-- Upload Status Message -->
      <p v-if="message" class="mt-6 text-center text-green-700 font-semibold">
        {{ message }}
      </p>

    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      examId: this.$route.params.examId,
      file: null,
      message: ''
    };
  },
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0];
    },
    async uploadCSV() {
      if (!this.file) {
        this.message = "Please select a CSV file.";
        return;
      }

      const formData = new FormData();
      formData.append('file', this.file);
      formData.append('exam_id', this.examId); // Form Id 
      formData.append('email', localStorage.getItem('faculty_email'))
      formData.append('role', 'Faculty')


      try {
        const response = await fetch('http://localhost:5001/api/questions/upload-csv', {
          method: 'POST',
          body: formData
        });

        const result = await response.json();
        if (response.ok) {
          this.message = result.message;
        } else {
          this.message = result.error ? `Error: ${result.error}` : 'Unknown error occurred.';
          console.error("Upload error response:", result);
        }
      } catch (err) {
        this.message = 'An error occurred during upload.';
        console.error(err);
      }
    }
  },
  mounted() {
    this.examId = this.$route.params.examId; 
  }
};
</script>

