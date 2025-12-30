import axios from 'axios';

const axiosInstance = axios.create({
    // Explicitly set the base URL to your backend port
    baseURL: 'http://localhost:5001', 
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true // Required for session cookies/cors
});

export default axiosInstance;