import React from 'react';
import { Button } from 'flowbite-react';
import { useNavigate } from 'react-router-dom';

const CongratulationsPage = () => {
  const navigate = useNavigate();

  const handleGoHome = () => {
    navigate('/settings'); 
  };

  return (
    <div className="flex h-screen bg-gray-100 items-center justify-center">
      <div className="max-w-md p-6 bg-white rounded-lg shadow-lg text-center">
        <h1 className="text-4xl font-bold text-indigo-600 mb-4">Congratulations!</h1>
        <p className="text-xl text-gray-700 mb-6">
          You'll hear from us soon. Take a moment to relax, enjoy a coffee, and stay tuned for further updates!
        </p>
        <Button onClick={handleGoHome} className="w-full bg-green-500">
          Go to Home Page
        </Button>
      </div>
    </div>
  );
};

export default CongratulationsPage;
