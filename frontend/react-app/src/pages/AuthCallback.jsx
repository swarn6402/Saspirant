import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function AuthCallback() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const handled = useRef(false);

  useEffect(() => {
    if (handled.current) return;
    handled.current = true;

    const params = new URLSearchParams(window.location.search);
    const user_id = params.get('user_id');
    const name = params.get('name');
    const email = params.get('email');
    const error = params.get('error');

    if (error || !user_id || !name) {
      navigate('/login', { replace: true });
      return;
    }

    login({ user_id, name, email });
    navigate('/dashboard', { replace: true });
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>
  );
}