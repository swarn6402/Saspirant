import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function AuthCallback() {
    const [searchParams] = useSearchParams();
    const { login } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        const userId = searchParams.get('user_id');
        const name = searchParams.get('name');
        const email = searchParams.get('email');
        const error = searchParams.get('error');

        if (error) {
            console.error('OAuth error:', error);
            navigate('/login?error=' + error);
            return;
        }

        if (userId && name && email) {
            login({
                user_id: userId,
                name: name,
                email: email
            });
            navigate('/dashboard');
        } else {
            navigate('/login?error=oauth_failed');
        }
    }, [searchParams, login, navigate]);

    return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
    );
}
