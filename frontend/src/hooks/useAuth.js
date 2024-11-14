import { useState, useEffect } from 'react';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchUserDetails = () => {
    // Retrieve token and role from localStorage or sessionStorage
    const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    const userRole = localStorage.getItem('userRole') || sessionStorage.getItem('userRole');
    

    if (token && userRole) {
      setUser({
        token,   
        role: userRole,
      });
    }

    setLoading(false);
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    sessionStorage.removeItem('userRole');

    setUser(null);
  };

  useEffect(() => {
    fetchUserDetails();
  }, []);

  return { user, loading, logout };
};
