import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const userId = localStorage.getItem('user_id');
    const userName = localStorage.getItem('user_name');
    const userEmail = localStorage.getItem('user_email');

    if (userId && userName) {
      setUser({
        id: userId,
        name: userName,
        email: userEmail,
      });
    }
    setLoading(false);
  }, []);

  const login = (userData) => {
    localStorage.setItem('user_id', userData.user_id);
    localStorage.setItem('user_name', userData.name);
    localStorage.setItem('user_email', userData.email);
    setUser({
      id: userData.user_id,
      name: userData.name,
      email: userData.email,
    });
  };

  const logout = () => {
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_email');
    setUser(null);
  };

  return <AuthContext.Provider value={{ user, login, logout, loading }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

export default AuthContext;
