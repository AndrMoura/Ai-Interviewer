import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, TextInput, Checkbox } from 'flowbite-react';
import axios from 'axios';

const LoginPage = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState(null);

  const handleLogin = async () => {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await axios.post('http://localhost:8000/login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.status === 200) {
        const { token, role } = response.data;
        console.log("loggd in token", token)
        console.log("role", role)
        if (rememberMe) {
          localStorage.setItem('authToken', token);
          localStorage.setItem('userRole', role);
        } else {
          sessionStorage.setItem('authToken', token);
          sessionStorage.setItem('userRole', role);
        }

        // Redirect to settings page
        navigate('/settings');
      }
    } catch (error) {
      if (error.response && error.response.status === 401) {
        setError("Incorrect username or password.");
      } else {
        setError("An error occurred. Please try again later.");
      }
    }
  };

  return (
    <div className="flex flex-col h-screen items-center justify-center bg-gray-100">
      <div className="text-center mb-6">
        <h1 className="text-4xl font-bold text-indigo-600 mb-2">Login to Ai Interviewer</h1>
        <p className="text-lg text-gray-500">Enter your credentials</p>
      </div>

      <div className="w-96 p-6 shadow-lg rounded-lg bg-white">
        <h2 className="text-2xl font-bold mb-4">Login</h2>
        <TextInput
          placeholder="Username"
          className="mb-4"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <TextInput
          type="password"
          placeholder="Password"
          className="mb-4"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <div className="flex items-center mb-4">
          <Checkbox
            id="rememberMe"
            checked={rememberMe}
            onChange={() => setRememberMe(!rememberMe)}
          />
          <label htmlFor="rememberMe" className="ml-2 text-sm text-gray-700">
            Remember Me
          </label>
        </div>

        <Button onClick={handleLogin} className="w-full">
          Login
        </Button>

        {error && <p className="text-red-500 mt-4 text-center">{error}</p>}
      </div>
    </div>
  );
};

export default LoginPage;
