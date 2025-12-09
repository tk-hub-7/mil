import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Purchases from './pages/Purchases';
import Transfers from './pages/Transfers';
import Assignments from './pages/Assignments';

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<Signup />} />

                    <Route
                        path="/dashboard"
                        element={
                            <ProtectedRoute>
                                <Dashboard />
                            </ProtectedRoute>
                        }
                    />

                    <Route
                        path="/purchases"
                        element={
                            <ProtectedRoute>
                                <Purchases />
                            </ProtectedRoute>
                        }
                    />

                    <Route
                        path="/transfers"
                        element={
                            <ProtectedRoute>
                                <Transfers />
                            </ProtectedRoute>
                        }
                    />

                    <Route
                        path="/assignments"
                        element={
                            <ProtectedRoute roles={['admin', 'base_commander']}>
                                <Assignments />
                            </ProtectedRoute>
                        }
                    />

                    <Route path="/" element={<Navigate to="/login" replace />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;
