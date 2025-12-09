import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { LogIn, Package, Shield } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import FormInput from '../components/FormInput';
import Button from '../components/Button';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const result = await login(username, password);

        if (result.success) {
            navigate('/dashboard');
        } else {
            setError(result.error);
        }

        setLoading(false);
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

                {/* Login Card */}
                <div className="card p-8 animate-slide-up">
                    <div className="flex items-center space-x-2 mb-6">
                        <LogIn className="w-6 h-6 text-primary-500" />
                        <h2 className="text-2xl font-bold text-white">Sign In</h2>
                    </div>

                    {error && (
                        <div className="mb-4 p-4 bg-red-900/20 border border-red-700 rounded-lg">
                            <p className="text-sm text-red-400">{error}</p>
                        </div>
                    )}

                    <form onSubmit={handleSubmit}>
                        <FormInput
                            label="Username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter your username"
                            required
                        />

                        <FormInput
                            label="Password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter your password"
                            required
                        />

                        <Button
                            type="submit"
                            variant="primary"
                            className="w-full mt-6"
                            disabled={loading}
                        >
                            {loading ? (
                                <div className="flex items-center justify-center space-x-2">
                                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                                    <span>Signing in...</span>
                                </div>
                            ) : (
                                'Sign In'
                            )}
                        </Button>
                    </form>

                    <div className="mt-6 pt-6 border-t border-dark-700">
                        <p className="text-xs text-gray-500 text-center mb-3">Demo Credentials</p>
                        <div className="space-y-2 text-xs">
                            <div className="bg-dark-800 p-3 rounded border border-dark-600">
                                <p className="text-gray-400 mb-1">Admin (Full Access)</p>
                                <p className="text-primary-400 font-mono">admin / admin123</p>
                            </div>
                            <div className="bg-dark-800 p-3 rounded border border-dark-600">
                                <p className="text-gray-400 mb-1">Base Commander</p>
                                <p className="text-primary-400 font-mono">commander / commander123</p>
                            </div>
                            <div className="bg-dark-800 p-3 rounded border border-dark-600">
                                <p className="text-gray-400 mb-1">Logistics Officer</p>
                                <p className="text-primary-400 font-mono">logistics / logistics123</p>
                            </div>
                        </div>
                    </div>

                    <div className="mt-6 pt-6 border-t border-dark-700 text-center">
                        <p className="text-sm text-gray-400">
                            Don't have an account?{' '}
                            <Link to="/signup" className="text-primary-500 hover:text-primary-400 font-medium transition-colors">
                                Sign up
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

export default Login;
