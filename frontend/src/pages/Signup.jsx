import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus, Shield } from 'lucide-react';
import api from '../api/axios';
import FormInput from '../components/FormInput';
import Button from '../components/Button';

const Signup = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        first_name: '',
        last_name: '',
        role: 'logistics_officer', // Default role
        role_code: '', // Role verification code
        assigned_base_id: null,
    });

    // Default roles in case API fails
    const [roles, setRoles] = useState([
        { value: 'admin', label: 'Administrator' },
        { value: 'base_commander', label: 'Base Commander' },
        { value: 'logistics_officer', label: 'Logistics Officer' },
    ]);
    const [bases, setBases] = useState([]);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    // Debug: Verify component is loading
    console.log('Signup component loaded');

    // Fetch roles and bases on component mount
    useEffect(() => {
        const fetchData = async () => {
            try {
                const [rolesResponse, basesResponse] = await Promise.all([
                    api.get('/auth/roles/'),
                    api.get('/bases/')
                ]);
                // Only update roles if API returns data
                if (rolesResponse.data.roles && rolesResponse.data.roles.length > 0) {
                    setRoles(rolesResponse.data.roles);
                }
                setBases(basesResponse.data.results || basesResponse.data);
            } catch (err) {
                console.error('Error fetching data:', err);
                // Show error only if bases fetch failed (critical for base commanders)
                if (err.response?.status === 401 || err.response?.status === 403) {
                    console.warn('Authentication required for bases - this should not happen');
                }
                // Keep default roles if API fails
            }
        };
        fetchData();
    }, []);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Validation
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters long');
            return;
        }

        setLoading(true);

        try {
            const response = await api.post('/auth/register/', {
                username: formData.username,
                email: formData.email,
                password: formData.password,
                first_name: formData.first_name,
                last_name: formData.last_name,
                role: formData.role,
                role_code: formData.role_code,
                assigned_base_id: formData.assigned_base_id,
            });

            if (response.data) {
                // Store tokens and user data
                localStorage.setItem('access_token', response.data.tokens.access);
                localStorage.setItem('refresh_token', response.data.tokens.refresh);
                localStorage.setItem('user', JSON.stringify(response.data.user));

                // Redirect to dashboard
                navigate('/dashboard');
            }
        } catch (err) {
            if (err.response?.data) {
                // Handle validation errors from backend
                const errors = err.response.data;
                if (typeof errors === 'object') {
                    const errorMessages = Object.entries(errors)
                        .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
                        .join('\n');
                    setError(errorMessages);
                } else {
                    setError('Registration failed. Please try again.');
                }
            } else {
                setError('Network error. Please check your connection.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950 flex items-center justify-center p-4">
            {/* Background pattern */}
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzMzNDE1NSIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9wYXR0ZXJuPjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2dyaWQpIi8+PC9zdmc+')] opacity-20"></div>

            <div className="relative z-10 w-full max-w-md">
                {/* Logo and Title */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center p-4 bg-primary-600 rounded-2xl shadow-glow-lg mb-4">
                        <Shield className="w-12 h-12 text-white" />
                    </div>
                    <h1 className="text-4xl font-bold text-white mb-2">Military AMS</h1>
                    <p className="text-gray-400">Asset Management System</p>
                </div>

                {/* Signup Card */}
                <div className="card p-8 animate-slide-up">
                    <div className="flex items-center space-x-2 mb-6">
                        <UserPlus className="w-6 h-6 text-primary-500" />
                        <h2 className="text-2xl font-bold text-white">Create Account</h2>
                    </div>

                    {error && (
                        <div className="mb-4 p-4 bg-red-900/20 border border-red-700 rounded-lg">
                            <p className="text-sm text-red-400 whitespace-pre-line">{error}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit}>
                        <div className="grid grid-cols-2 gap-4">
                            <FormInput
                                label="First Name"
                                type="text"
                                name="first_name"
                                value={formData.first_name}
                                onChange={handleChange}
                                placeholder="John"
                                required
                            />

                            <FormInput
                                label="Last Name"
                                type="text"
                                name="last_name"
                                value={formData.last_name}
                                onChange={handleChange}
                                placeholder="Doe"
                                required
                            />
                        </div>

                        <FormInput
                            label="Username"
                            type="text"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            placeholder="Enter your username"
                            required
                        />

                        <FormInput
                            label="Email"
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="john.doe@military.gov"
                            required
                        />

                        <FormInput
                            label="Password"
                            type="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            placeholder="Enter your password (min 8 characters)"
                            required
                        />

                        <FormInput
                            label="Confirm Password"
                            type="password"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            placeholder="Confirm your password"
                            required
                        />

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Role *
                            </label>
                            <select
                                name="role"
                                value={formData.role}
                                onChange={handleChange}
                                className="w-full px-4 py-3 bg-gray-700 border-2 border-gray-600 rounded-lg text-white text-base focus:outline-none focus:border-primary-500 transition-colors cursor-pointer"
                                required
                            >
                                {roles.map((role) => (
                                    <option
                                        key={role.value}
                                        value={role.value}
                                    >
                                        {role.label}
                                    </option>
                                ))}
                            </select>
                            <p className="text-xs text-gray-400 mt-2">
                                Selected: <span className="text-primary-400 font-semibold">
                                    {roles.find(r => r.value === formData.role)?.label || 'Logistics Officer'}
                                </span>
                            </p>
                        </div>

                        <FormInput
                            label="Role Code"
                            type="text"
                            name="role_code"
                            value={formData.role_code}
                            onChange={handleChange}
                            placeholder="Enter your role verification code"
                            required
                        />
                        <div className="mb-4 -mt-2">
                            <p className="text-xs text-gray-500">
                                Demo Codes: Admin: <span className="text-primary-400 font-mono">ADMIN-2024-SECURE</span> |
                                Base Commander: <span className="text-primary-400 font-mono">CMDR-BASE-7891</span> |
                                Logistics: <span className="text-primary-400 font-mono">LOG-OFFICER-4523</span>
                            </p>
                        </div>

                        {formData.role === 'base_commander' && (
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Assigned Base *
                                </label>
                                <select
                                    name="assigned_base_id"
                                    value={formData.assigned_base_id || ''}
                                    onChange={handleChange}
                                    className="w-full px-4 py-3 bg-gray-700 border-2 border-gray-600 rounded-lg text-white text-base focus:outline-none focus:border-primary-500 transition-colors cursor-pointer"
                                    required={formData.role === 'base_commander'}
                                >
                                    <option value="">Select a base</option>
                                    {bases.map((base) => (
                                        <option key={base.id} value={base.id}>
                                            {base.name} ({base.code})
                                        </option>
                                    ))}
                                </select>
                                {bases.length === 0 && (
                                    <p className="text-xs text-yellow-400 mt-2">
                                        Loading bases... If this persists, please contact support.
                                    </p>
                                )}
                            </div>
                        )}

                        <Button
                            type="submit"
                            variant="primary"
                            className="w-full mt-6"
                            disabled={loading}
                        >
                            {loading ? (
                                <div className="flex items-center justify-center space-x-2">
                                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                                    <span>Creating account...</span>
                                </div>
                            ) : (
                                'Create Account'
                            )}
                        </Button>
                    </form>

                    <div className="mt-6 pt-6 border-t border-dark-700 text-center">
                        <p className="text-sm text-gray-400">
                            Already have an account?{' '}
                            <Link to="/login" className="text-primary-500 hover:text-primary-400 font-medium transition-colors">
                                Sign in
                            </Link>
                        </p>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-8 text-center text-sm text-gray-500">
                    <p>© 2024 Military Asset Management System. All rights reserved.</p>
                </div>
            </div>
        </div>
    );
};

export default Signup;
