import axios from 'axios';

// Change this to your Render URL when deploying
const API_BASE_URL = 'https://student-project-5d6h.onrender.com/api';


export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Login function
export const loginUser = async (username, password) => {
    try {
        const response = await api.post('/token/', {
            username,
            password,
        });
        return response.data;
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

// Get dashboard data
export const fetchDashboard = async (token) => {
    try {
        const response = await api.get('/dashboard/', {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        return response.data;
    } catch (error) {
        throw error.response?.data || error.message;
    }
};

// Get user profile
export const fetchProfile = async (token) => {
    try {
        const response = await api.get('/profile/', {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });
        return response.data;
    } catch (error) {
        throw error.response?.data || error.message;
    }
};