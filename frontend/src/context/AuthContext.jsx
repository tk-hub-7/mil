import { createContext, useState, useContext, useEffect } from 'react';
import api from '../api/axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is logged in
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
        setLoading(false);
    }, []);

    const login = async (username, password) => {
        try {
            console.log('🔐 Attempting login with baseURL:', api.defaults.baseURL);
            console.log('🔐 Full URL will be:', api.defaults.baseURL + '/auth/login/');
            const response = await api.post('/auth/login/', { username, password });
            const { user, tokens } = response.data;

            localStorage.setItem('access_token', tokens.access);
            localStorage.setItem('refresh_token', tokens.refresh);
            localStorage.setItem('user', JSON.stringify(user));

            setUser(user);
            return { success: true };
        } catch (error) {
            console.error('❌ Login error:', error);
            console.error('❌ Error response:', error.response);
            return {
                success: false,
                error: error.response?.data?.error || 'Login failed',
            };
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        setUser(null);
    };

    const isAdmin = () => {
        return user?.role?.role === 'admin';
    };

    const isBaseCommander = () => {
        return user?.role?.role === 'base_commander';
    };

    const isLogisticsOfficer = () => {
        return user?.role?.role === 'logistics_officer';
    };

    const hasRole = (roles) => {
        if (!user?.role?.role) return false;
        return roles.includes(user.role.role);
    };

    const value = {
        user,
        login,
        logout,
        loading,
        isAdmin,
        isBaseCommander,
        isLogisticsOfficer,
        hasRole,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
