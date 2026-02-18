import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        logout();
        navigate('/');
    };

    return (
        <nav className="bg-white shadow-sm sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-2">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="#4F46E5">
                            <path d="M12 3L1 9l11 6 9-4.91V17h2V9L12 3zM5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"/>
                        </svg>
                        <span className="text-xl font-bold text-gray-900">Saspirant</span>
                    </Link>

                    {/* Navigation Links */}
                    <div className="hidden md:flex items-center gap-8">
                        <a href="/#about" className="text-gray-600 hover:text-indigo-600 transition-colors">About</a>
                        <a href="/#how-it-works" className="text-gray-600 hover:text-indigo-600 transition-colors">How It Works</a>
                        
                        {user ? (
                            <>
                                <Link to="/dashboard" className="text-gray-600 hover:text-indigo-600 transition-colors">Dashboard</Link>
                                <div className="flex items-center gap-3">
                                    <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                                        Hi, {user.name.split(' ')[0]}
                                    </span>
                                    <button
                                        onClick={handleLogout}
                                        className="text-sm text-red-500 hover:text-red-700 transition-colors"
                                    >
                                        Logout
                                    </button>
                                </div>
                            </>
                        ) : (
                            <>
                                <Link to="/login" className="text-gray-600 hover:text-indigo-600 transition-colors">Sign In</Link>
                                <Link
                                    to="/register"
                                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
                                >
                                    Get Started
                                </Link>
                            </>
                        )}
                    </div>

                    {/* Mobile menu button */}
                    <div className="md:hidden">
                        <button
                            onClick={() => {
                                const menu = document.getElementById('mobile-menu');
                                menu.classList.toggle('hidden');
                            }}
                            className="text-gray-600 hover:text-indigo-600"
                        >
                            <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Mobile menu */}
                <div id="mobile-menu" className="hidden md:hidden pb-4">
                    <div className="flex flex-col gap-4">
                        <a href="/#about" className="text-gray-600">About</a>
                        <a href="/#how-it-works" className="text-gray-600">How It Works</a>
                        {user ? (
                            <>
                                <Link to="/dashboard" className="text-gray-600">Dashboard</Link>
                                <span className="text-sm text-gray-500">Hi, {user.name.split(' ')[0]}</span>
                                <button onClick={handleLogout} className="text-red-500 text-left">Logout</button>
                            </>
                        ) : (
                            <>
                                <Link to="/login" className="text-gray-600">Sign In</Link>
                                <Link to="/register" className="text-indigo-600 font-medium">Get Started</Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}
